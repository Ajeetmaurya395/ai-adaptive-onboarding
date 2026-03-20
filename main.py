#!/usr/bin/env python3
"""
AI Adaptive Learning Engine - MongoDB Edition
Main entry point for production deployment

Usage:
    python main.py                    # Run with Streamlit
    python main.py --check            # Run system diagnostics
    python main.py --seed             # Seed database with demo data
    python main.py --stats            # Show database statistics
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import init_db, close_db, health_check, get_collection
from services.llm_service import llm


def check_dependencies():
    """Verify all required dependencies are installed"""
    required = [
        "streamlit", "pandas", "plotly", "pymongo", 
        "bcrypt", "requests", "python-dotenv", "dnspython"
    ]
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    print("✅ All dependencies installed")
    return True


def check_mongodb_connection():
    """Verify MongoDB connection and configuration"""
    try:
        from pymongo import MongoClient
        from app.database import get_client, MONGODB_URI, MONGODB_DB
        
        # Test connection
        client = get_client()
        client.admin.command('ping')
        
        # Verify database access
        db = client[MONGODB_DB]
        db.command("collStats", "users")  # Test collection access
        
        print(f"✅ MongoDB connected: {MONGODB_URI}")
        print(f"📦 Database: {MONGODB_DB}")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("💡 Check MONGODB_URI in .env")
        print("💡 Ensure MongoDB is running: mongod --port 27017")
        print("💡 For Atlas: Verify network access and credentials")
        return False


def check_env_vars():
    """Verify environment configuration"""
    required_vars = ["HF_TOKEN", "MODEL_NAME", "MONGODB_URI"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"⚠️  Missing env vars: {missing}")
        print("💡 Copy .env.example to .env and configure")
        return False
    
    # Test HF connection (non-blocking)
    try:
        result = llm.generate(
            system_prompt="You are a test endpoint.",
            user_prompt="Respond with {'status': 'ok'}",
            response_type="json"
        )
        if result:
            print("✅ Hugging Face API connected")
    except Exception as e:
        print(f"⚠️  HF API test failed: {e}")
        print("💡 App will use mock mode for demo")
    
    return True


def seed_demo_data():
    """Insert sample data for testing"""
    from app.database import create_user, save_result, save_roadmap, get_collection
    import bcrypt
    
    print("🌱 Seeding demo data...")
    
    # Create demo user
    success, msg = create_user("demo", "demo@example.com", "demo123")
    if success:
        print(f"✅ Demo user created: demo / demo123")
    else:
        print(f"⚠️  User exists: {msg}")
    
    # Get user ID for seeding results
    users = get_collection("users")
    demo_user = users.find_one({"username": "demo"})
    
    if demo_user:
        user_id = str(demo_user["_id"])
        
        # Seed sample results
        sample_results = [
            {"score": 85.5, "gap_data": {"matched_skills": ["Python", "SQL"], "missing_skills": ["AWS", "Docker"]}},
            {"score": 72.3, "gap_data": {"matched_skills": ["JavaScript"], "missing_skills": ["React", "Node.js", "TypeScript"]}},
            {"score": 91.0, "gap_data": {"matched_skills": ["Python", "AWS", "Docker"], "missing_skills": ["Kubernetes"]}},
        ]
        
        for sample in sample_results:
            save_result(
                user_id=user_id,
                score=sample["score"],
                gap_data=sample["gap_data"],
                metadata={"seeded": True, "source": "demo_data"}
            )
        
        # Seed sample roadmap
        sample_roadmap = {
            "target_role": "Senior Data Engineer",
            "items": [
                {"skill": "AWS", "resource": "AWS Certified Solutions Architect", "duration": "6 weeks", "priority": "High"},
                {"skill": "Docker", "resource": "Docker Mastery Course", "duration": "3 weeks", "priority": "Medium"},
                {"skill": "Kubernetes", "resource": "Kubernetes Fundamentals", "duration": "4 weeks", "priority": "High"}
            ]
        }
        save_roadmap(user_id=user_id, roadmap_data=sample_roadmap)
        
        print("✅ Sample results and roadmaps seeded")
    
    print("🎉 Demo data seeding complete")


def show_stats():
    """Display database statistics"""
    print("📊 Database Statistics")
    print("-" * 40)
    
    try:
        health = health_check()
        print(f"Status: {health['status'].upper()}")
        print(f"Database: {health.get('database')}")
        print(f"Collections: {health.get('collections')}")
        print(f"Storage: {health.get('storage_size_mb')} MB")
        print()
        
        # Collection counts
        for coll_name in ["users", "results", "roadmaps"]:
            count = get_collection(coll_name).count_documents({})
            print(f"{coll_name}: {count} documents")
        
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")


def run_streamlit():
    """Launch Streamlit application"""
    print("🚀 Starting AI Adaptive Learning Engine...")
    print("📍 Access at: http://localhost:8501")
    print("🗄️  Backend: MongoDB")
    print("💡 Press Ctrl+C to stop\n")
    
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "app/ui.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--theme.base=dark",
        "--theme.primaryColor=#4CAF50",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ]
    
    try:
        subprocess.run(cmd, cwd=project_root, check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        close_db()
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit failed: {e}")
        close_db()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="AI Adaptive Learning Engine - MongoDB Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --check     # Run diagnostics
  python main.py --seed      # Add demo user (demo/demo123)
  python main.py --stats     # Show database stats
  python main.py             # Launch application
        """
    )
    parser.add_argument("--check", action="store_true", help="Run system diagnostics")
    parser.add_argument("--seed", action="store_true", help="Seed database with demo data")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    
    args = parser.parse_args()
    
    print(f"🤖 AI Adaptive Learning Engine v1.0")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if args.check:
        print("🔍 Running diagnostics...")
        deps_ok = check_dependencies()
        mongo_ok = check_mongodb_connection()
        env_ok = check_env_vars()
        
        if deps_ok and mongo_ok and env_ok:
            print("\n🎉 System ready for launch!")
        else:
            print("\n⚠️  Fix issues above before running")
        return
    
    if args.seed:
        init_db()
        seed_demo_data()
        close_db()
        return
    
    if args.stats:
        init_db()
        show_stats()
        close_db()
        return
    
    # Default: run application
    print("🔧 Initializing...")
    init_db()
    
    # Pre-flight checks
    if not check_dependencies():
        sys.exit(1)
    
    if not check_mongodb_connection():
        print("\n⚠️  Continuing with mock mode (no database persistence)")
    
    check_env_vars()
    
    # Launch app
    try:
        run_streamlit()
    finally:
        close_db()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        close_db()
        sys.exit(0)