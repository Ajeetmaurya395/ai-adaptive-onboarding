import os
import json
import time
from typing import List, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
API_URL = "https://router.huggingface.co/v1/chat/completions"

class LLMService:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        self.max_retries = 1
        self.retry_delay = 0.25
        self.has_token = bool(HF_TOKEN)

    def _query(self, payload):
        """Send request to Hugging Face Inference API with retry logic"""
        if not self.has_token:
            return None

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

    def _generate_mock(self, prompt_type, user_prompt=""):
        """Improved adaptive mock responses that use the input text."""
        # Simple extraction for demo purposes when API is down
        text = user_prompt.lower()
        extracted_skills = []
        common_skills = [
            "python", "javascript", "aws", "docker", "kubernetes", "sql", "react",
            "java", "go", "terraform", "jenkins", "prometheus", "cloudformation",
            "github actions", "git", "redis", "leadership", "communication",
            "microservices"
        ]
        for s in common_skills:
            if s in text:
                extracted_skills.append(" ".join(part.capitalize() for part in s.split()))
        
        if not extracted_skills:
            extracted_skills = ["Communication", "Problem Solving", "Adaptability"]

        mocks = {
            "resume": {
                "skills": extracted_skills[:5],
                "experience_years": 5,
                "summary": "Experienced professional with background in " + ", ".join(extracted_skills[:3])
            },
            "jd": {
                "skills": extracted_skills or ["Python", "AWS", "Cloud Infrastructure"],
                "role": "Software Professional",
                "seniority": "Senior"
            },
            "roadmap": [
                {
                    "title": f"Mastering {skill}",
                    "course_name": f"{skill} Advanced Course",
                    "duration": "4 weeks",
                    "priority": "High",
                    "url": "https://coursera.org",
                    "reasoning": f"Critical gap identified for this role requirement."
                }
                for skill in extracted_skills[:5]
            ],
            "trace": f"The candidate shows strength in {', '.join(extracted_skills[:2])} but needs to develop deeper expertise in other required areas."
        }
        return mocks.get(prompt_type, {})

    def _generate_chat_mock(self, messages: List[Dict[str, str]]) -> str:
        latest_user_message = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                latest_user_message = message.get("content", "")
                break
        latest_user_message = latest_user_message.strip()
        if not latest_user_message:
            latest_user_message = "Tell me about my analysis."

        return (
            "I could not reach the live Qwen endpoint just now, so I am answering from the local fallback context. "
            f"Your latest question was: \"{latest_user_message[:220]}\". "
            "If you ask about your analysis, roadmap, missing skills, or learning resources, I can still guide you with the data already available in the app."
        )

    def generate(self, system_prompt, user_prompt, response_type="json"):
        """
        Generate response from Qwen model with chat formatting.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.1 if response_type == "json" else 0.7,
            "max_tokens": 1024,
            "stream": False
        }
        
        result = self._query(payload)
        
        if result and "choices" in result:
            content = result["choices"][0]["message"]["content"]
            if response_type == "json":
                return self._parse_json_response(content)
            return content
        
        print("[WARN] Using adaptive mock response (API unavailable or failed)")
        p_type = ("resume" if "resume" in user_prompt.lower() or "candidate" in user_prompt.lower() else 
                  "jd" if "job" in user_prompt.lower() or "requirements" in user_prompt.lower() else
                  "roadmap" if "roadmap" in user_prompt.lower() else "trace")
        return self._generate_mock(p_type, user_prompt)

    def chat(self, messages: List[Dict[str, str]], system_prompt: str | None = None, temperature: float = 0.4, max_tokens: int = 900) -> str:
        chat_messages = []
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(messages)

        payload = {
            "model": MODEL_NAME,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        result = self._query(payload)
        if result and "choices" in result:
            return result["choices"][0]["message"]["content"]

        print("[WARN] Using adaptive chat fallback (API unavailable or failed)")
        return self._generate_chat_mock(chat_messages)

llm = LLMService()
