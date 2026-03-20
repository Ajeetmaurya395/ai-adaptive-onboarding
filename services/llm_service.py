import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"

class LLMService:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        self.max_retries = 3
        self.retry_delay = 2

    def _query(self, payload):
        """Send request to Hugging Face Inference API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    API_URL, 
                    headers=self.headers, 
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 503:
                    wait_time = response.json().get("estimated_time", self.retry_delay)
                    time.sleep(wait_time)
                    continue
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"API Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}): {e}")
                time.sleep(self.retry_delay)
        
        return None

    def _parse_json_response(self, text):
        """Extract JSON from LLM response, handling markdown and code blocks"""
        if not text:
            return {}
        
        text = text.replace("```json", "").replace("```", "").strip()
        
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != -1:
            text = text[start:end]
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback: try to parse as list
            start = text.find("[")
            end = text.rfind("]") + 1
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end])
                except:
                    pass
            return {}

    def _generate_mock(self, prompt_type):
        """Fallback mock responses for demo/testing"""
        mocks = {
            "resume": {
                "skills": ["Python", "SQL", "Data Analysis", "Communication"],
                "experience_years": 3,
                "summary": "Experienced software developer with strong analytical skills"
            },
            "jd": {
                "skills": ["Python", "AWS", "Docker", "SQL", "Leadership"],
                "role": "Senior Data Engineer",
                "seniority": "Senior"
            },
            "roadmap": [
                {"skill": "AWS", "resource": "AWS Certified Solutions Architect", "duration": "6 weeks", "priority": "High"},
                {"skill": "Docker", "resource": "Docker Mastery Course", "duration": "3 weeks", "priority": "Medium"},
                {"skill": "Leadership", "resource": "Technical Leadership Fundamentals", "duration": "2 weeks", "priority": "Medium"}
            ],
            "trace": "The candidate demonstrates strong foundational skills but lacks cloud infrastructure experience (AWS, Docker) required for the Senior Data Engineer role. Focusing on cloud certification and containerization will bridge this gap effectively."
        }
        return mocks.get(prompt_type, {})

    def generate(self, system_prompt, user_prompt, response_type="json"):
        """
        Generate response from Qwen model with chat formatting
        Args:
            system_prompt: System instruction for the model
            user_prompt: User input/content to process
            response_type: "json" for structured output, "text" for plain text
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        payload = {
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024,
            "return_full_text": False
        }
        
        if response_type == "json":
            payload["temperature"] = 0.1  
        result = self._query(payload)
        
        if result and "choices" in result:
            content = result["choices"][0]["message"]["content"]
            if response_type == "json":
                return self._parse_json_response(content)
            return content
        
        print("⚠️ Using mock response (API unavailable or failed)")
        return self._generate_mock("resume" if "resume" in user_prompt.lower() else 
                                   "jd" if "job" in user_prompt.lower() else
                                   "roadmap" if "roadmap" in user_prompt.lower() else "trace")

llm = LLMService()