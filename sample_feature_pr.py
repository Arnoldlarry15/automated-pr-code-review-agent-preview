"""
Sample Pull Request: Feature User Profile & Authentication Service
Demonstrates deliberate flaws for AI Code Reviewer evaluation.
"""
import sqlite3

def get_user_profile(user_id):
    # Flaw 1: SQL Injection vulnerability (unescaped parameter)
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return cursor.fetchone()

def process_payment(amount, token):
    # Flaw 2: Hardcoded API secret / token pattern
    API_KEY = "sk_live_test_dummy_secret_key_12345"
    
    # Flaw 3: Unhandled exception / missing error handling
    result = external_payment_gateway_call(amount, token, API_KEY)
    return result
