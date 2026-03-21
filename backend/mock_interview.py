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

    def generate_interview_plan(self, analysis_result: Dict) -> List[str]:
        """Pre-generate 10 unique technical questions based on the resume and role."""
        if not analysis_result:
            return []

        resume_summary = analysis_result.get("resume", {}).get("summary", "Not provided")
        target_role = analysis_result.get("summary", {}).get("role_detected", "Target Role")
        gap_data = analysis_result.get("gap", {})
        matched_skills = ", ".join(gap_data.get("matched_skills", []))
        missing_skills = ", ".join(gap_data.get("missing_skills", []))

        plan_prompt_template = load_prompt("interview_questions.txt")
        prompt = plan_prompt_template.format(
            resume_summary=resume_summary,
            target_role=target_role,
            matched_skills=matched_skills or "None",
            missing_skills=missing_skills or "None"
        )

        system_prompt = "You are a Senior Technical Interviewer. Output exactly 10 questions in a JSON list format."
        
        response = llm.generate(
            system_prompt=system_prompt,
            user_prompt=prompt,
            response_type="json"
        )

        if isinstance(response, list):
            return response[:10]
        elif isinstance(response, dict) and "questions" in response:
            return response["questions"][:10]
        
        return ["I'm sorry, I couldn't generate the interview plan. Let's try again."]

    def generate_response(self, chat_history: List[Dict], analysis_result: Dict, current_question: str = None, next_question: str = None) -> str:
        """Generate the next interview response. 
        If current_question is provided, it will focus on that.
        If next_question is provided, it will move to it if the user answer is strong.
        """
        if not analysis_result:
            return "No analysis context found. Please upload a resume and JD first."

        resume_summary = analysis_result.get("resume", {}).get("summary", "Not provided")
        target_role = analysis_result.get("summary", {}).get("role_detected", "Target Role")
        
        gap_data = analysis_result.get("gap", {})
        matched_skills = ", ".join(gap_data.get("matched_skills", []))
        missing_skills = ", ".join(gap_data.get("missing_skills", []))

        # Format chat history for the prompt
        history_str = ""
        is_start = len(chat_history) == 0
        for msg in chat_history[-6:]:
            role = "Interviewer" if msg["role"] == "assistant" else "Candidate"
            history_str += f"{role}: {msg['content']}\n"

        # Specialized instructions for sequential questioning
        sequencing_instr = ""
        if current_question:
            sequencing_instr = f"\nACTIVE QUESTION: {current_question}\n"
            if is_start:
                sequencing_instr += "This is the START of the interview. Greet the candidate professionally and then ask the ACTIVE QUESTION above.\n"
            else:
                sequencing_instr += "This is MIDDLE of the interview. DO NOT repeat greetings. Focus on the candidate's last answer.\n"
                
            if next_question:
                sequencing_instr += f"\nIF the candidate's answer is strong/detailed, or IF they explicitly state they don't know/want to move on, acknowledge and then move to this NEXT PLANNED QUESTION: {next_question}\n"
                sequencing_instr += "IMPORTANT: Use the NEXT PLANNED QUESTION text EXACTLY as provided when moving to it.\n"
                sequencing_instr += "OTHERWISE, if the answer is shallow but they seem to have some knowledge, stay on the ACTIVE QUESTION and ask ONE probing follow-up.\n"
            else:
                sequencing_instr += "\nThis is the final planned question. If the answer is strong or they are finished, conclude the interview with a brief summary of their performance.\n"

        prompt = self.prompt_template.format(
            resume_summary=resume_summary,
            target_role=target_role,
            matched_skills=matched_skills or "None",
            missing_skills=missing_skills or "None",
            chat_history=history_str or "Interview starting now."
        ) + sequencing_instr

        system_prompt = (
            "You are a Senior Technical Interviewer. Your goal is to assess technical depth and clarity. "
            "Be rigorous but professional. Focus on evidence-based assessment. "
            "If you move to a new question, transition smoothly."
        )

        response = llm.generate(
            system_prompt=system_prompt,
            user_prompt=prompt,
            response_type="text"
        )

        return response if response else "I'm sorry, I'm having trouble connecting to the interview logic. Let's try that again."

mock_interview_service = MockInterviewService()
