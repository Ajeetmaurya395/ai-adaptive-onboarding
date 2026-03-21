import os
from typing import List, Dict

from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

from backend.data_loader import data_loader

try:
    from langchain_community.vectorstores import Chroma
except Exception:  # pragma: no cover - optional in cloud deploys
    Chroma = None

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
        
        self.course_data = data_loader.load_json("course_catalog.json", {}).get("courses", [])
        self.course_vectorstore = None
        if Chroma is not None:
            try:
                self.course_vectorstore = Chroma(
                    collection_name="course_catalog",
                    embedding_function=self.embeddings,
                    persist_directory="./chroma_db"
                )
            except Exception:
                self.course_vectorstore = None

    def _fallback_course_docs(self, skill: str) -> List[Dict]:
        normalized_skill = (skill or "").strip().lower()
        matches = []
        for course in self.course_data:
            course_skill = (course.get("skill") or "").strip().lower()
            title = course.get("title") or f"{skill} Specialist"
            if normalized_skill and (normalized_skill in course_skill or course_skill in normalized_skill):
                matches.append({
                    "title": title,
                    "url": course.get("url") or "https://coursera.org",
                })
        return matches[:2]

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
            docs = []
            if self.course_vectorstore is not None:
                try:
                    docs = self.course_vectorstore.similarity_search(skill, k=2)
                except Exception:
                    docs = []

            if docs:
                context = "\n".join([f"- {d.metadata['title']}: {d.metadata['url']}" for d in docs])
                first_title = docs[0].metadata["title"]
                first_url = docs[0].metadata["url"]
            else:
                fallback = self._fallback_course_docs(skill)
                context = "\n".join([f"- {item['title']}: {item['url']}" for item in fallback])
                first_title = fallback[0]["title"] if fallback else f"{skill} Specialist"
                first_url = fallback[0]["url"] if fallback else "https://coursera.org"
            
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
                    "course_name": first_title,
                    "url": first_url,
                    "reasoning": f"Critical gap identified for JD requirements."
                })
                
        return roadmap

langchain_service = LangChainService()
