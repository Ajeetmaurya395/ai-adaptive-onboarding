"""
MongoDB Database Module for AI Adaptive Learning Engine
Handles all CRUD operations with PyMongo
"""
import os
import sys
import bcrypt
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pymongo import MongoClient, errors
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()

# Avoid UnicodeEncodeError on Windows terminals using legacy encodings.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "ai_onboarding")
DB_VERBOSE = os.getenv("DB_VERBOSE", "0").strip().lower() in {"1", "true", "yes", "on"}

# Global client and database references
_client: Optional[MongoClient] = None
_db: Optional[Any] = None
_indexes_initialized: bool = False


def _log(message: str) -> None:
    if DB_VERBOSE:
        print(message)

def get_client() -> MongoClient:
    """Get or create MongoDB client with connection pooling"""
    global _client
    if _client is None:
        try:
            _client = MongoClient(
                MONGODB_URI,
                maxPoolSize=50,
                minPoolSize=10,
                serverSelectionTimeoutMS=5000,
                socketTimeoutMS=10000,
                connectTimeoutMS=10000,
                retryWrites=True,
                retryReads=True
            )
            # Test connection
            _client.admin.command('ping')
            _log(f"Connected to MongoDB: {MONGODB_URI}")
        except errors.ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            print("Ensure MongoDB is running or check MONGODB_URI in .env")
            raise
    return _client


def get_db() -> Any:
    """Get database instance"""
    global _db
    if _db is None:
        _db = get_client()[MONGODB_DB]
    return _db


def get_collection(name: str) -> Collection:
    """Get collection instance with type hint"""
    return get_db()[name]


def init_db(verbose: bool = False):
    """Initialize database indexes once per process."""
    global _indexes_initialized
    if _indexes_initialized:
        return

    db = get_db()

    # Users collection indexes
    db.users.create_index("username", unique=True, name="idx_username_unique")
    db.users.create_index("email", unique=True, name="idx_email_unique")
    db.users.create_index("created_at", name="idx_users_created")

    # Results collection indexes
    db.results.create_index("user_id", name="idx_results_user")
    db.results.create_index("created_at", name="idx_results_created")
    db.results.create_index([("user_id", 1), ("created_at", -1)], name="idx_user_history")

    # Roadmaps collection indexes
    db.roadmaps.create_index("user_id", name="idx_roadmaps_user")
    db.roadmaps.create_index("created_at", name="idx_roadmaps_created")

    _indexes_initialized = True
    if verbose:
        print("Database indexes created")


def close_db():
    """Close MongoDB client connection"""
    global _client, _db, _indexes_initialized
    if _client:
        _client.close()
        _client = None
        _db = None
        _indexes_initialized = False
        _log("MongoDB connection closed")


# ============ USER OPERATIONS ============

def create_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Create new user with hashed password
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        users = get_collection("users")
        
        # Check if user already exists
        if users.find_one({"$or": [{"username": username}, {"email": email}]}):
            return False, "Username or email already exists"
        
        # Hash password with bcrypt
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')
        
        # Create user document
        user_doc = {
            "username": username,
            "email": email.lower(),
            "password_hash": password_hash,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "is_active": True,
            "profile": {
                "first_name": None,
                "last_name": None,
                "avatar_url": None
            }
        }
        
        result = users.insert_one(user_doc)
        return True, f"User created successfully (ID: {result.inserted_id})"
        
    except errors.DuplicateKeyError:
        return False, "Username or email already exists"
    except Exception as e:
        print(f"Error creating user: {e}")
        return False, f"Database error: {str(e)}"


def verify_user(identifier: str, password: str) -> tuple[bool, Optional[Dict]]:
    """
    Verify user credentials
    
    Args:
        identifier: username or email
        password: plain text password
        
    Returns:
        tuple: (success: bool, user_data: dict or None)
    """
    try:
        users = get_collection("users")
        
        # Find user by username OR email (case-insensitive)
        user = users.find_one({
            "$or": [
                {"username": identifier},
                {"email": identifier.lower()}
            ]
        })
        
        if not user:
            return False, None
        
        # Verify password
        if bcrypt.checkpw(
            password.encode('utf-8'), 
            user["password_hash"].encode('utf-8')
        ):
            # Return safe user data (exclude password)
            user_data = {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "created_at": user.get("created_at"),
                "profile": user.get("profile", {})
            }
            return True, user_data
        
        return False, None
        
    except Exception as e:
        print(f"Error verifying user: {e}")
        return False, None


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user document by MongoDB _id"""
    try:
        from bson.objectid import ObjectId
        users = get_collection("users")
        user = users.find_one({"_id": ObjectId(user_id)})
        
        if user:
            user["id"] = str(user["_id"])
            return user
        return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None


def update_user(user_id: str, updates: Dict) -> bool:
    """Update user document with new fields"""
    try:
        from bson.objectid import ObjectId
        users = get_collection("users")
        
        updates["updated_at"] = datetime.now(timezone.utc)
        
        result = users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updates}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating user: {e}")
        return False


# ============ RESULTS OPERATIONS ============

def save_result(user_id: str, score: float, gap_data: Optional[Dict] = None, 
                metadata: Optional[Dict] = None) -> tuple[bool, str]:
    """
    Save analysis result to database
    
    Returns:
        tuple: (success: bool, result_id: str)
    """
    try:
        results = get_collection("results")
        
        result_doc = {
            "user_id": user_id,
            "score": round(score, 2),
            "gap_data": gap_data or {},
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc)
        }
        
        result = results.insert_one(result_doc)
        return True, str(result.inserted_id)
        
    except Exception as e:
        print(f"Error saving result: {e}")
        return False, str(e)


def get_results(user_id: str, limit: int = 10, offset: int = 0) -> List[Dict]:
    """Get user's analysis results with pagination"""
    try:
        results = get_collection("results")
        
        cursor = results.find(
            {"user_id": user_id},
            {"password_hash": 0}  # Exclude sensitive fields if any
        ).sort("created_at", -1).skip(offset).limit(limit)
        
        results_list = []
        for doc in cursor:
            doc["id"] = str(doc["_id"])
            results_list.append(doc)
        
        return results_list
        
    except Exception as e:
        print(f"Error fetching results: {e}")
        return []


def get_result_by_id(result_id: str) -> Optional[Dict]:
    """Get single result by ID"""
    try:
        from bson.objectid import ObjectId
        results = get_collection("results")
        doc = results.find_one({"_id": ObjectId(result_id)})
        
        if doc:
            doc["id"] = str(doc["_id"])
            return doc
        return None
    except Exception as e:
        print(f"Error fetching result: {e}")
        return None


def delete_result(result_id: str, user_id: str) -> bool:
    """Delete a result (owner verification)"""
    try:
        from bson.objectid import ObjectId
        results = get_collection("results")
        
        result = results.delete_one({
            "_id": ObjectId(result_id),
            "user_id": user_id
        })
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting result: {e}")
        return False


# ============ ROADMAP OPERATIONS ============

def save_roadmap(user_id: str, roadmap_data: Dict, 
                 metadata: Optional[Dict] = None) -> tuple[bool, str]:
    """
    Save learning roadmap to database
    
    Returns:
        tuple: (success: bool, roadmap_id: str)
    """
    try:
        roadmaps = get_collection("roadmaps")
        
        roadmap_doc = {
            "user_id": user_id,
            "roadmap_data": roadmap_data,
            "metadata": metadata or {},
            "version": 1,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        result = roadmaps.insert_one(roadmap_doc)
        return True, str(result.inserted_id)
        
    except Exception as e:
        print(f"Error saving roadmap: {e}")
        return False, str(e)


def get_roadmaps(user_id: str, limit: int = 5) -> List[Dict]:
    """Get user's saved roadmaps"""
    try:
        roadmaps = get_collection("roadmaps")
        
        cursor = roadmaps.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit)
        
        roadmaps_list = []
        for doc in cursor:
            doc["id"] = str(doc["_id"])
            roadmaps_list.append(doc)
        
        return roadmaps_list
        
    except Exception as e:
        print(f"Error fetching roadmaps: {e}")
        return []


def get_roadmap_by_id(roadmap_id: str) -> Optional[Dict]:
    """Get single roadmap by ID"""
    try:
        from bson.objectid import ObjectId
        roadmaps = get_collection("roadmaps")
        doc = roadmaps.find_one({"_id": ObjectId(roadmap_id)})
        
        if doc:
            doc["id"] = str(doc["_id"])
            return doc
        return None
    except Exception as e:
        print(f"Error fetching roadmap: {e}")
        return None


def update_roadmap(roadmap_id: str, user_id: str, updates: Dict) -> bool:
    """Update existing roadmap"""
    try:
        from bson.objectid import ObjectId
        roadmaps = get_collection("roadmaps")
        
        updates["updated_at"] = datetime.now(timezone.utc)
        
        result = roadmaps.update_one({
            "_id": ObjectId(roadmap_id),
            "user_id": user_id
        }, {"$set": updates})
        
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating roadmap: {e}")
        return False


# ============ HISTORY & ANALYTICS ============

def get_history(user_id: str, days: int = 30) -> List[Dict]:
    """
    Get user's analysis history for dashboard
    
    Args:
        user_id: User identifier
        days: Lookback period in days
        
    Returns:
        List of result summaries
    """
    try:
        from datetime import timedelta
        results = get_collection("results")
        
        # Calculate date filter
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Aggregate pipeline for summary stats
        pipeline = [
            {"$match": {
                "user_id": user_id,
                "created_at": {"$gte": since}
            }},
            {"$sort": {"created_at": -1}},
            {"$project": {
                "_id": 1,
                "score": 1,
                "created_at": 1,
                "gap_summary": {
                    "matched": {"$size": "$gap_data.matched_skills"},
                    "missing": {"$size": "$gap_data.missing_skills"}
                }
            }}
        ]
        
        cursor = results.aggregate(pipeline)
        history = []
        
        for doc in cursor:
            doc["id"] = str(doc["_id"])
            history.append(doc)
        
        return history
        
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []


def get_user_stats(user_id: str) -> Dict:
    """Get aggregated statistics for user dashboard"""
    try:
        results = get_collection("results")
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": None,
                "total_analyses": {"$sum": 1},
                "avg_score": {"$avg": "$score"},
                "best_score": {"$max": "$score"},
                "last_analysis": {"$max": "$created_at"}
            }}
        ]
        
        result = list(results.aggregate(pipeline))
        
        if result:
            stats = result[0]
            return {
                "total_analyses": stats.get("total_analyses", 0),
                "avg_score": round(stats.get("avg_score", 0), 2),
                "best_score": round(stats.get("best_score", 0), 2),
                "last_analysis": stats.get("last_analysis")
            }
        
        return {
            "total_analyses": 0,
            "avg_score": 0,
            "best_score": 0,
            "last_analysis": None
        }
        
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {}


# ============ UTILITY FUNCTIONS ============

def count_collection(collection_name: str, query: Optional[Dict] = None) -> int:
    """Count documents in a collection"""
    try:
        coll = get_collection(collection_name)
        return coll.count_documents(query or {})
    except Exception as e:
        print(f"Error counting {collection_name}: {e}")
        return 0


def health_check() -> Dict:
    """Check database connection health"""
    try:
        client = get_client()
        client.admin.command('ping')
        
        db = get_db()
        stats = db.command("dbStats")
        
        return {
            "status": "healthy",
            "database": MONGODB_DB,
            "collections": stats.get("collections", 0),
            "storage_size_mb": round(stats.get("storageSize", 0) / (1024 * 1024), 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Context manager for automatic connection handling
class DatabaseSession:
    """Context manager for database operations"""
    def __enter__(self):
        init_db()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"Database error: {exc_val}")
        # Keep connection open for Streamlit session persistence
        return False

