import os
import json
from typing import List, Dict
from services.llm_service import llm

def load_prompt(filename):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(base_dir, "prompts", filename)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

class MockInterviewService:
    def __init__(self):
        self.prompt_template = load_prompt("mock_interview.txt")

    def generate_response(self, chat_history: List[Dict], analysis_result: Dict) -> str:
        """Generate the next interview question or feedback based on history and resume."""
        if not analysis_result:
            return "No analysis context found. Please upload a resume and JD first."

        resume_summary = analysis_result.get("resume", {}).get("summary", "Not provided")
        target_role = analysis_result.get("summary", {}).get("role_detected", "Target Role")
        
        gap_data = analysis_result.get("gap", {})
        matched_skills = ", ".join(gap_data.get("matched_skills", []))
        missing_skills = ", ".join(gap_data.get("missing_skills", []))

        # Format chat history for the prompt
        history_str = ""
        for msg in chat_history[-6:]:  # Keep recent context
            role = "Interviewer" if msg["role"] == "assistant" else "Candidate"
            history_str += f"{role}: {msg['content']}\n"

        prompt = self.prompt_template.format(
            resume_summary=resume_summary,
            target_role=target_role,
            matched_skills=matched_skills or "None",
            missing_skills=missing_skills or "None",
            chat_history=history_str or "Interview starting now."
        )

        system_prompt = (
            "You are a Senior Technical Interviewer. Your goal is to assess technical depth and clarity. "
            "Be rigorous but professional. Focus on evidence-based assessment."
        )

        response = llm.generate(
            system_prompt=system_prompt,
            user_prompt=prompt,
            response_type="text"
        )

        return response if response else "I'm sorry, I'm having trouble connecting to the interview logic. Let's try that again."

mock_interview_service = MockInterviewService()
