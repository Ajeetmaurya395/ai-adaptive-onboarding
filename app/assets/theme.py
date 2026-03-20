THEME = {
    "primary": "#4CAF50",
    "secondary": "#2196F3",
    "bg": "#0e1117",
    "card_bg": "#1c1f26",
    "text": "#ffffff"
}

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background-color: #0e1117;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-card {
        background-color: #1c1f26;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2b2f36;
        color: white;
        text-align: center;
    }
    
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        border: none;
    }
    
    .stSidebar {
        background-color: #161b22;
    }
    </style>
    """, unsafe_allow_html=True)