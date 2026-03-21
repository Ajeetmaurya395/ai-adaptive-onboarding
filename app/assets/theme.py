from pathlib import Path

import streamlit as st

THEME = {
    "primary": "#06b6d4",
    "secondary": "#0891b2",
    "bg": "#f5fcff",
    "card_bg": "#ffffff",
    "text": "#0f172a",
}


def load_css() -> None:
    css_path = Path(__file__).with_name("styles.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def _surface_palette(mode: str) -> dict[str, str]:
    if mode == "Dark":
        return {
            "bg_0": "#08131d",
            "bg_1": "#0d1f2d",
            "ink": "#e7f7ff",
            "muted": "#b7d4df",
            "line": "rgba(125, 211, 252, 0.24)",
            "surface_bg": """
                radial-gradient(circle at 8% 0%, rgba(34, 211, 238, 0.16), transparent 30%),
                radial-gradient(circle at 100% 100%, rgba(8, 145, 178, 0.18), transparent 38%),
                linear-gradient(180deg, #08131d 0%, #0b1a25 100%)
            """,
            "header_bg": "linear-gradient(180deg, rgba(9, 19, 29, 0.94), rgba(9, 21, 31, 0.84))",
            "sidebar_bg": "linear-gradient(180deg, rgba(10, 20, 30, 0.96), rgba(9, 28, 40, 0.9))",
            "brand_bg": "linear-gradient(140deg, rgba(14, 28, 40, 0.92), rgba(10, 56, 73, 0.76))",
            "hero_bg": """
                radial-gradient(circle at 92% 10%, rgba(34, 211, 238, 0.22), transparent 28%),
                linear-gradient(120deg, rgba(14, 25, 37, 0.82), rgba(8, 44, 61, 0.72), rgba(7, 61, 78, 0.56))
            """,
            "card_bg": "linear-gradient(180deg, rgba(11, 23, 35, 0.74), rgba(13, 31, 45, 0.62))",
            "card_soft": "linear-gradient(180deg, rgba(14, 28, 40, 0.78), rgba(13, 34, 49, 0.68))",
            "card_strong": "linear-gradient(180deg, rgba(17, 52, 70, 0.86), rgba(15, 72, 94, 0.74))",
            "footer_bg": "rgba(11, 23, 35, 0.74)",
            "metric_ink": "#f0fbff",
            "progress_track": "rgba(125, 211, 252, 0.16)",
            "shadow": "0 24px 48px rgba(0, 0, 0, 0.28)",
            "shadow_soft": "0 14px 30px rgba(0, 0, 0, 0.2)",
            "info_bg": "linear-gradient(180deg, rgba(13, 38, 54, 0.88), rgba(11, 53, 72, 0.7))",
            "success_bg": "linear-gradient(180deg, rgba(8, 52, 45, 0.9), rgba(12, 83, 67, 0.72))",
            "warning_bg": "linear-gradient(180deg, rgba(61, 45, 9, 0.92), rgba(110, 79, 13, 0.72))",
        }

    return {
        "bg_0": "#f5fcff",
        "bg_1": "#ffffff",
        "ink": "#0f172a",
        "muted": "#475569",
        "line": "#bae6fd",
        "surface_bg": """
            radial-gradient(circle at 6% 0%, rgba(6, 182, 212, 0.16), transparent 35%),
            radial-gradient(circle at 100% 100%, rgba(14, 116, 144, 0.12), transparent 42%),
            linear-gradient(180deg, #f9feff 0%, #f5fcff 100%)
        """,
        "header_bg": "linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(240, 251, 255, 0.9))",
        "sidebar_bg": "linear-gradient(180deg, #ffffff 0%, #f0fbff 100%)",
        "brand_bg": "linear-gradient(140deg, #ecfeff, #e0f2fe)",
        "hero_bg": """
            radial-gradient(circle at 90% 8%, rgba(34, 211, 238, 0.28), rgba(34, 211, 238, 0)),
            linear-gradient(115deg, #ffffff 0%, #ecfbff 34%, #d7f3ff 100%)
        """,
        "card_bg": "linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(240, 251, 255, 0.84))",
        "card_soft": "linear-gradient(180deg, rgba(244, 251, 255, 0.92), rgba(230, 247, 255, 0.82))",
        "card_strong": "linear-gradient(180deg, rgba(217, 244, 255, 0.94), rgba(200, 238, 255, 0.9))",
        "footer_bg": "rgba(255, 255, 255, 0.75)",
        "metric_ink": "#082f49",
        "progress_track": "rgba(186, 230, 253, 0.35)",
        "shadow": "0 14px 35px rgba(8, 145, 178, 0.12)",
        "shadow_soft": "0 8px 18px rgba(8, 145, 178, 0.08)",
        "info_bg": "linear-gradient(180deg, rgba(236, 254, 255, 0.9), rgba(222, 247, 255, 0.78))",
        "success_bg": "linear-gradient(180deg, rgba(236, 253, 245, 0.92), rgba(220, 252, 231, 0.82))",
        "warning_bg": "linear-gradient(180deg, rgba(255, 251, 235, 0.94), rgba(254, 243, 199, 0.82))",
    }


def inject_css() -> None:
    load_css()
    if "app_surface_mode" not in st.session_state:
        st.session_state.app_surface_mode = "Light"
    palette = _surface_palette(st.session_state.get("app_surface_mode", "Light"))
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

        :root {
            --bg-0: #f5fcff;
            --bg-1: #ffffff;
            --ink: #0f172a;
            --muted: #475569;
            --line: #bae6fd;
            --cyan-500: #06b6d4;
            --cyan-600: #0891b2;
            --cyan-700: #0e7490;
            --cyan-soft: #ecfeff;
            --ok: #0f766e;
            --warn: #b45309;
            --danger: #be123c;
            --shadow: 0 14px 35px rgba(8, 145, 178, 0.12);
            --shadow-soft: 0 8px 18px rgba(8, 145, 178, 0.08);
            --gap: 1.2rem;
        }

        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif;
            color: var(--ink);
        }

        .stApp {
            background:
                radial-gradient(circle at 6% 0%, rgba(6, 182, 212, 0.16), transparent 35%),
                radial-gradient(circle at 100% 100%, rgba(14, 116, 144, 0.12), transparent 42%),
                linear-gradient(180deg, #f9feff 0%, var(--bg-0) 100%);
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(240, 251, 255, 0.9));
            border-bottom: 1px solid #c8ebf8;
        }

        [data-testid="stToolbar"] {
            right: 1rem;
        }

        [data-testid="stDecoration"] {
            display: none;
        }

        .main .block-container {
            padding-top: 1.35rem;
            padding-bottom: 2.4rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
            max-width: none;
            width: 100%;
        }

        .main .block-container > div[data-testid="stVerticalBlock"] {
            gap: 0.95rem;
        }

        [data-testid="stHorizontalBlock"] {
            gap: 1.2rem !important;
        }

        [data-testid="column"] > div[data-testid="stVerticalBlock"] {
            gap: 0.9rem;
        }

        hr {
            border-color: #d6eef8 !important;
            margin: 0.4rem 0 0.9rem !important;
        }

        .stMarkdown, .stText, .stSubheader, .stCaption,
        [data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"],
        h1, h2, h3, h4, h5, h6, p, li, small, span, label {
            color: var(--ink) !important;
        }

        .stMetric label, [data-testid="stMetricLabel"] p {
            color: var(--muted) !important;
        }

        .stMetric [data-testid="stMetricValue"] {
            color: #082f49 !important;
        }

        [data-testid="stSidebar"] * {
            color: #0f172a !important;
        }

        [data-testid="stSidebar"] a {
            color: #0b4f65 !important;
            border-radius: 10px;
        }

        [data-testid="stSidebar"] a:hover {
            background: #ecfeff !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #f0fbff 100%);
            border-right: 1px solid var(--line);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
        }

        [data-testid="stSidebarNav"] {
            display: none;
        }

        .sidebar-brand {
            background: linear-gradient(140deg, #ecfeff, #e0f2fe);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 12px 14px;
            margin-bottom: 12px;
            box-shadow: var(--shadow-soft);
        }

        .sidebar-brand-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.2;
        }

        .sidebar-brand-sub {
            font-size: 12px;
            color: var(--muted);
            margin-top: 4px;
        }

        .sidebar-section {
            margin: 10px 0 4px;
            color: var(--cyan-700);
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        [data-testid="stSidebar"] .stButton > button {
            border-radius: 12px;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            margin-bottom: 0.2rem;
        }

        .app-header {
            position: relative;
            overflow: hidden;
            background:
                radial-gradient(circle at 90% 8%, rgba(34, 211, 238, 0.28), rgba(34, 211, 238, 0)),
                linear-gradient(115deg, #ffffff 0%, #ecfbff 34%, #d7f3ff 100%);
            border: 1px solid #8fd8f4;
            border-radius: 20px;
            padding: 28px 32px;
            margin-bottom: 16px;
            box-shadow: 0 18px 34px rgba(8, 145, 178, 0.16);
        }

        .app-header::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, #22d3ee, #06b6d4, #0891b2);
        }

        .app-header::after {
            content: "";
            position: absolute;
            top: -24px;
            right: -24px;
            width: 180px;
            height: 180px;
            background: radial-gradient(circle, rgba(6, 182, 212, 0.28), rgba(6, 182, 212, 0));
            pointer-events: none;
        }

        .app-eyebrow {
            color: var(--cyan-700);
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .app-header-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 42px;
            font-weight: 800;
            margin: 0;
            color: #0b2533;
            line-height: 1.15;
        }

        .app-header-subtitle {
            margin-top: 10px;
            color: var(--muted);
            font-size: 16px;
            line-height: 1.45;
            max-width: 950px;
        }

        .section-card {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 20px;
            box-shadow: var(--shadow-soft);
            margin-bottom: 8px;
        }

        .section-title {
            margin: 0 0 4px 0;
            color: #0b2533;
            font-size: 20px;
            font-weight: 800;
        }

        .section-subtitle {
            margin: 0;
            color: var(--muted);
            font-size: 13px;
        }

        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 8px;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            border: 1px solid #b6e6f8;
            border-radius: 999px;
            background: #f0fbff;
            color: #0e7490;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
        }

        .metric-card {
            background: linear-gradient(180deg, #ffffff 0%, #f0fbff 100%);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: var(--shadow-soft);
        }

        .metric-label {
            color: var(--muted);
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .metric-value {
            color: #082f49;
            font-size: 30px;
            font-weight: 800;
            line-height: 1.1;
        }

        .timeline-step {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 10px;
            box-shadow: var(--shadow-soft);
        }

        .timeline-step-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .timeline-step-title {
            font-weight: 700;
            color: #082f49;
            margin: 0;
        }

        .timeline-chip {
            font-size: 11px;
            font-weight: 700;
            border-radius: 999px;
            padding: 4px 10px;
            border: 1px solid var(--line);
            background: var(--cyan-soft);
            color: var(--cyan-700);
        }

        .timeline-meta {
            color: var(--muted);
            font-size: 13px;
            margin: 3px 0;
        }

        .stButton > button {
            border-radius: 12px;
            border: 1px solid #67e8f9;
            background: linear-gradient(135deg, var(--cyan-600), var(--cyan-500));
            color: #ffffff;
            font-weight: 700;
            min-height: 46px;
            letter-spacing: 0.01em;
            box-shadow: var(--shadow-soft);
        }

        .stButton > button:hover {
            border-color: #22d3ee;
            transform: translateY(-1px);
        }

        .stFileUploader {
            border-radius: 12px;
        }

        div[data-testid="stFileUploaderDropzone"] {
            background: #ffffff !important;
            border: 1px dashed #7dd3fc !important;
            border-radius: 12px !important;
            padding: 14px !important;
        }

        div[data-testid="stFileUploaderDropzone"] * {
            color: #0f172a !important;
        }

        div[data-baseweb="input"],
        div[data-baseweb="base-input"] {
            border: 1px solid #cbeaf5 !important;
            border-radius: 12px !important;
            background: #ffffff !important;
            min-height: 48px;
            box-shadow: 0 0 0 0 rgba(6, 182, 212, 0);
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="base-input"]:focus-within {
            border-color: #22d3ee !important;
            box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.15);
        }

        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox input {
            border: none !important;
            background: transparent !important;
            color: #0f172a !important;
            min-height: 46px !important;
            font-size: 17px !important;
        }

        .stTextInput > div > div > input::placeholder,
        .stTextArea textarea::placeholder {
            color: #64748b !important;
        }

        div[data-baseweb="input"]:has(input[type="password"]),
        div[data-baseweb="base-input"]:has(input[type="password"]) {
            border-radius: 10px !important;
            overflow: hidden;
        }

        div[data-baseweb="input"]:has(input[type="password"]) button,
        div[data-baseweb="base-input"]:has(input[type="password"]) button {
            border-left: 1px solid #d5edf8 !important;
            border-radius: 0 10px 10px 0 !important;
            background: #ffffff !important;
            color: #0e7490 !important;
            min-width: 42px !important;
            width: 44px !important;
            margin: 0 !important;
            padding: 0 !important;
            display: inline-flex !important;
            align-items: center;
            justify-content: center;
        }

        div[data-baseweb="input"]:has(input[type="password"]) svg,
        div[data-baseweb="base-input"]:has(input[type="password"]) svg {
            width: 20px !important;
            height: 20px !important;
        }

        input[type="password"] {
            -webkit-text-security: disc;
            text-security: disc;
        }

        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.75);
            border: 1px solid #cfeefe;
            border-radius: 14px;
            padding: 16px 18px 12px;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            padding-bottom: 4px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 12px;
            background: #eefbff;
            border: 1px solid var(--line);
            padding: 9px 18px !important;
            min-height: 48px;
            min-width: 114px;
            justify-content: center;
            font-weight: 700;
            font-size: 17px;
        }

        .stTabs [aria-selected="true"] {
            background: #d5f5ff !important;
            border-color: #67e8f9 !important;
        }

        .app-footer {
            margin-top: 26px;
            padding: 14px 16px;
            border-radius: 12px;
            border: 1px dashed #9bdcf0;
            background: rgba(255, 255, 255, 0.75);
            color: #0e7490;
            text-align: center;
            font-size: 12px;
            font-weight: 600;
        }

        .skill-chip-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 4px;
        }

        .skill-chip {
            display: inline-flex;
            align-items: center;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            border: 1px solid transparent;
        }

        .skill-chip.match {
            color: #0f766e;
            background: #ecfeff;
            border-color: #99f6e4;
        }

        .skill-chip.miss {
            color: #9f1239;
            background: #fff1f2;
            border-color: #fecdd3;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid #cfeefe;
            border-radius: 12px;
            overflow: hidden;
            background: #ffffff;
        }

        [data-testid="stDataFrame"] table {
            font-size: 16px !important;
        }

        @media (max-width: 768px) {
            .app-header {
                padding: 16px;
            }

            .app-header-title {
                font-size: 26px;
            }

            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <style>
        :root {{
            --bg-0: {palette["bg_0"]};
            --bg-1: {palette["bg_1"]};
            --ink: {palette["ink"]};
            --muted: {palette["muted"]};
            --line: {palette["line"]};
            --shadow: {palette["shadow"]};
            --shadow-soft: {palette["shadow_soft"]};
            --surface-bg: {palette["bg_0"]};
            --surface-panel: rgba(255, 255, 255, 0.9);
            --surface-card: {palette["bg_1"]};
            --surface-soft: {palette["card_soft"]};
            --border-soft: {palette["line"]};
            --text-main: {palette["ink"]};
            --text-muted: {palette["muted"]};
        }}

        .stApp {{
            background: {palette["surface_bg"]} !important;
            color: var(--ink) !important;
        }}

        [data-testid="stHeader"] {{
            background: {palette["header_bg"]} !important;
            border-bottom: 1px solid var(--line) !important;
        }}

        [data-testid="stSidebar"] {{
            background: {palette["sidebar_bg"]} !important;
            border-right: 1px solid var(--line) !important;
        }}

        [data-testid="stSidebar"] *,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] a {{
            color: var(--ink) !important;
        }}

        .sidebar-brand {{
            background: {palette["brand_bg"]} !important;
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }}

        .app-header {{
            background: {palette["hero_bg"]} !important;
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }}

        .section-card,
        .metric-card,
        .timeline-step,
        [data-testid="stMetric"],
        [data-testid="stDataFrame"],
        [data-testid="stForm"],
        div[data-testid="stFileUploaderDropzone"],
        div[data-baseweb="input"],
        div[data-baseweb="base-input"],
        .streamlit-expanderContent,
        .app-footer,
        .input-panel,
        .upload-input-card,
        .readiness-strip,
        .theme-toggle-card {{
            background: {palette["card_bg"]} !important;
            border-color: var(--line) !important;
            box-shadow: var(--shadow-soft) !important;
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }}

        .streamlit-expanderHeader,
        .stTabs [data-baseweb="tab"],
        [data-testid="stSidebar"] [role="radiogroup"] label {{
            background: {palette["card_soft"]} !important;
            border-color: var(--line) !important;
        }}

        .stTabs [aria-selected="true"] {{
            background: {palette["card_strong"]} !important;
            border-color: #67e8f9 !important;
            box-shadow: var(--shadow-soft) !important;
        }}

        .app-footer {{
            background: {palette["footer_bg"]} !important;
        }}

        .stMetric [data-testid="stMetricValue"],
        .metric-value,
        .timeline-step-title,
        .app-header-title,
        .section-title {{
            color: {palette["metric_ink"]} !important;
        }}

        .stMetric label,
        [data-testid="stMetricLabel"] p,
        .section-subtitle,
        .timeline-meta,
        .app-header-subtitle,
        .theme-toggle-sub,
        .sidebar-brand-sub {{
            color: var(--muted) !important;
        }}

        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox input,
        .stTextInput > div > div > input::placeholder,
        .stTextArea textarea::placeholder {{
            color: var(--ink) !important;
        }}

        [data-testid="stInfo"] {{
            background: {palette["info_bg"]} !important;
            border: 1px solid var(--line) !important;
        }}

        [data-testid="stSuccess"] {{
            background: {palette["success_bg"]} !important;
            border: 1px solid var(--line) !important;
        }}

        [data-testid="stWarning"] {{
            background: {palette["warning_bg"]} !important;
            border: 1px solid var(--line) !important;
        }}

        .stProgress > div > div {{
            background: {palette["progress_track"]} !important;
        }}

        .stProgress > div > div > div {{
            background: linear-gradient(90deg, #22d3ee, #06b6d4, #0891b2) !important;
        }}

        .theme-toggle-card {{
            border-radius: 14px;
            padding: 12px 14px 10px;
            margin: 8px 0 14px;
        }}

        .theme-toggle-title {{
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--cyan-700) !important;
            margin-bottom: 6px;
        }}

        .theme-toggle-sub {{
            font-size: 12px;
            margin-bottom: 2px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
