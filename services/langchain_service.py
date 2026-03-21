import os
from typing import List, Dict
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")

class LangChainService:
    def __init__(self):
        self.llm = HuggingFaceEndpoint(
            repo_id=MODEL_NAME,
            huggingfacehub_api_token=HF_TOKEN,
            temperature=0.1,
            max_new_tokens=1024,
        )
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Connect to existing ChromaDB
        self.course_vectorstore = Chroma(
            collection_name="course_catalog",
            embedding_function=self.embeddings,
            persist_directory="./chroma_db"
        )

    def generate_roadmap_steps(self, missing_skills: List[str], role: str) -> List[Dict]:
        """Use RAG to find courses for each missing skill and structure a roadmap."""
        roadmap = []
        
        prompt_template = """
        You are an expert career coach helping a candidate transition to a {role} role.
        The candidate is missing the following skill: {skill}
        
        Based on these available courses:
        {context}
        
        Recommend the BEST course for this skill.
        Return ONLY a JSON object with these keys: 
        "step": {step_num},
        "title": "Mastering {skill}",
        "course_name": "Course Title",
        "url": "Course URL",
        "reasoning": "Brief explanation why this course helps bridge the gap."
        """
        
        for i, skill in enumerate(missing_skills[:5]):
            # Retrieve relevant courses
            docs = self.course_vectorstore.similarity_search(skill, k=2)
            context = "\n".join([f"- {d.metadata['title']}: {d.metadata['url']}" for d in docs])
            
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["role", "skill", "context", "step_num"]
            )
            
            # Simple chain invocation
            chain = prompt | self.llm
            response = chain.invoke({
                "role": role,
                "skill": skill,
                "context": context,
                "step_num": i + 1
            })
            
            # Note: In a real implementation, we'd use a JsonOutputParser
            # For simplicity in this bridge turn, we'll try to parse or fallback
            try:
                import json
                start = response.find("{")
                end = response.rfind("}") + 1
                item = json.loads(response[start:end])
                roadmap.append(item)
            except:
                roadmap.append({
                    "step": i + 1,
                    "title": f"Mastering {skill}",
                    "course_name": docs[0].metadata['title'] if docs else f"{skill} Specialist",
                    "url": docs[0].metadata['url'] if docs else "https://coursera.org",
                    "reasoning": f"Critical gap identified for JD requirements."
                })
                
        return roadmap

langchain_service = LangChainService()
