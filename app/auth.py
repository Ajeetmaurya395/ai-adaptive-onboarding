import re
import streamlit as st
from app.database import create_user, verify_user

def validate_username(username):
    """Validate username: 3-20 alphanumeric characters"""
    return bool(re.match(r"^[a-zA-Z0-9]{3,20}$", username))

def validate_email(email):
    """Validate email format"""
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))

def validate_password(password):
    """Validate password: min 6 chars, must contain letter and number"""
    if len(password) < 6:
        return False
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    return has_letter and has_number

def register(username, email, password):
    """
    Register new user
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not validate_username(username):
        return False, "Username must be 3-20 alphanumeric characters"
    
    if not validate_email(email):
        return False, "Please enter a valid email address"
    
    if not validate_password(password):
        return False, "Password must be 6+ characters with at least one letter and one number"
    
    success, msg = create_user(username, email, password)
    return success, msg

def login(identifier, password):
    """
    Authenticate user
    
    Returns:
        tuple: (success: bool, user_data: dict or None)
    """
    if not identifier or not password:
        return False, None
    
    success, user_data = verify_user(identifier, password)
    
    if success and user_data:
        return True, user_data
    return False, None