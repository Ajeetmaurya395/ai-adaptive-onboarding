import streamlit as st
import os
from PyPDF2 import PdfReader
from app.components.loaders import loading_spinner
from app.components.alerts import show_success, show_error
from backend.parser import parse_resume, parse_jd
from backend.gap_engine import calculate_gap
from backend.roadmap_builder import generate_roadmap
from app.database import save_result, save_roadmap

st.set_page_config(page_title="Upload & Analyze", layout="wide")
st.title("📄 Upload & Analyze")

def read_pdf(file):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def load_sample_resume():
    """Load sample resume text for demo"""
    return """Senior Software Engineer with 5+ years experience building scalable web applications. 
Proficient in Python, Django, PostgreSQL, AWS (EC2, S3, Lambda), Docker, and Kubernetes. 
Strong background in CI/CD pipelines, microservices architecture, and agile methodologies. 
Led team of 4 developers to deliver cloud migration project ahead of schedule."""

def load_sample_jd():
    """Load sample job description text for demo"""
    """Senior Cloud Engineer - TechCorp
We're seeking an experienced engineer to lead our cloud infrastructure initiatives.

Required Skills:
- Advanced Python programming
- AWS services (EC2, S3, Lambda, RDS, CloudFormation)
- Containerization: Docker, Kubernetes
- Infrastructure as Code: Terraform or CloudFormation
- CI/CD: GitHub Actions, Jenkins
- Monitoring: CloudWatch, Prometheus

Preferred:
- Experience with microservices architecture
- Knowledge of security best practices
- Leadership/mentoring experience"""

# File Upload Section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Resume")
    resume_file = st.file_uploader("Upload Resume (PDF/TXT)", type=["pdf", "txt"], key="resume_uploader")
    
    if st.button("🎯 Try Sample Resume", use_container_width=True):
        st.session_state.resume_text = load_sample_resume()
        show_success("Sample resume loaded!")

with col2:
    st.subheader("💼 Job Description")
    jd_file = st.file_uploader("Upload JD (TXT)", type=["txt"], key="jd_uploader")
    
    if st.button("🎯 Try Sample JD", use_container_width=True):
        st.session_state.jd_text = load_sample_jd()
        show_success("Sample JD loaded!")

# Analysis Trigger
if st.button("🚀 Analyze Skill Gap", type="primary", use_container_width=True):
    resume_text = st.session_state.get("resume_text") or ""
    jd_text = st.session_state.get("jd_text") or ""
    
    # Process uploaded files if no session text
    if not resume_text and resume_file:
        if resume_file.type == "application/pdf":
            resume_text = read_pdf(resume_file)
        else:
            resume_text = resume_file.read().decode("utf-8")
        st.session_state.resume_text = resume_text
    
    if not jd_text and jd_file:
        jd_text = jd_file.read().decode("utf-8")
        st.session_state.jd_text = jd_text
    
    # Validation
    if not resume_text or len(resume_text) < 50:
        show_error("Please provide a valid resume (min 50 characters)")
        st.stop()
    
    if not jd_text or len(jd_text) < 50:
        show_error("Please provide a valid job description (min 50 characters)")
        st.stop()
    
    # Processing with loading state
    with loading_spinner("🤖 AI is analyzing your documents..."):
        try:
            # Step 1: Parse documents
            resume_data = parse_resume(resume_text)
            jd_data = parse_jd(jd_text)
            
            # Validate parsing results
            if not resume_data.get("skills"):
                show_error("Could not extract skills from resume. Please try again.")
                st.stop()
            
            # Step 2: Calculate skill gap
            gap_result = calculate_gap(
                resume_data.get("skills", []),
                jd_data.get("skills", [])
            )
            
            # Step 3: Generate learning roadmap
            roadmap = generate_roadmap(
                gap_result["missing_skills"],
                jd_data.get("role", "Target Role")
            )
            
            # Step 4: Save to database if user logged in
            user_id = st.session_state.get("user_id")
            if user_id:
                save_result(user_id, gap_result["match_score"])
                if roadmap:
                    save_roadmap(user_id, roadmap)
            
            # Step 5: Store results for other pages
            st.session_state.analysis_result = {
                "resume": resume_data,
                "jd": jd_data,
                "gap": gap_result,
                "roadmap": roadmap,
                "resume_text": resume_text[:500] + "..."  # Truncated for display
            }
            
            show_success("✅ Analysis complete! Navigate to other tabs for results.")
            
            # Quick preview
            with st.expander("📊 Quick Results Preview", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("Match Score", f"{gap_result['match_score']}%")
                c2.metric("Skills Matched", len(gap_result["matched_skills"]))
                c3.metric("Skills to Learn", len(gap_result["missing_skills"]))
                
        except Exception as e:
            show_error(f"Analysis failed: {str(e)}")
            st.exception(e)  # Show full traceback in dev mode