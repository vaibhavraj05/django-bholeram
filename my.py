import sqlite3
import os
import pickle
import subprocess

# Hardcoded credentials (sensitive data exposure)
USERNAME = "admin"
PASSWORD = "password123"

def authenticate(user, pwd):
    if user == USERNAME and pwd == PASSWORD:
        return True
    return False

def execute_query(user_input):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{user_input}';"
    cursor.execute(query)
    result = cursor.fetchall()
    
    conn.close()
    return result

def insecure_command(user_input):
    # Command Injection vulnerability
    os.system("ls " + user_input)

def insecure_deserialization(user_input):
    # Insecure Deserialization vulnerability
    return pickle.loads(user_input)

def main():
    user = input("Enter username: ")
    pwd = input("Enter password: ")
    
    if authenticate(user, pwd):
        print("Access granted")
        query_input = input("Enter search query: ")
        print(execute_query(query_input))
        
        cmd_input = input("Enter command to run: ")
        insecure_command(cmd_input)
        
        pickle_data = input("Enter serialized data: ").encode()
        print(insecure_deserialization(pickle_data))
    else:
        print("Access denied")

if __name__ == "__main__":
    main()
