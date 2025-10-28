import streamlit as st
import json
import os
import hashlib
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import re

USER_FILE = "users.json"
PROGRESS_FILE = "progress.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

def register_user(username, password, role="learner"):
    users = load_users()
    if username in users:
        return False
    users[username] = {"password": hash_password(password), "role": role}
    save_users(users)
    progress = load_progress()
    progress[username] = {"completed_cases": [], "points": 0, "badges": []}
    save_progress(progress)
    return True

def authenticate_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return users[username]["role"]
    return None

def execute_user_code(code, local_env):
    try:
        exec(code, {"__builtins__": {}}, local_env)
        return True, local_env
    except Exception as e:
        return False, str(e)

def award_badge(progress, username, badge_name):
    if badge_name not in progress[username]["badges"]:
        progress[username]["badges"].append(badge_name)

def calculate_points(progress, username, points):
    progress[username]["points"] += points

def render_progress_dashboard(progress, username):
    user_data = progress[username]
    st.subheader("Progress Dashboard")
    st.write("Completed Cases:", user_data["completed_cases"])
    st.write("Points:", user_data["points"])
    st.write("Badges:", user_data["badges"])
    timeline = pd.DataFrame({
        "Case": user_data["completed_cases"],
        "Completion": [i+1 for i in range(len(user_data["completed_cases"]))]
    })
    if not timeline.empty:
        fig = px.line(timeline, x="Case", y="Completion", title="Case Completion Timeline")
        st.plotly_chart(fig)

def render_leaderboard(progress):
    st.subheader("Leaderboard")
    leaderboard = []
    for user, pdata in progress.items():
        leaderboard.append((user, pdata["points"]))
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    df = pd.DataFrame(leaderboard, columns=["User", "Points"])
    st.table(df)

def evidence_analysis():
    st.subheader("Evidence Analysis Task")
    st.write("Enter text logs to extract IP addresses and emails using Python regex.")
    logs = st.text_area("Logs")
    if st.button("Analyze"):
        ips = re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", logs)
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", logs)
        st.write("IP Addresses Found:", ips)
        st.write("Emails Found:", emails)

def case_selection(username, progress):
    st.subheader("Available Cases")
    all_cases = ["Case 1: Basic Loops", "Case 2: Conditionals", "Case 3: Functions", "Case 4: Dictionaries", "Case 5: Recursion"]
    completed = progress[username]["completed_cases"]
    for c in all_cases:
        if c in completed:
            st.write(c, "- Completed")
        else:
            prereq_met = True
            idx = all_cases.index(c)
            if idx > 0 and all_cases[idx-1] not in completed:
                prereq_met = False
            if prereq_met:
                if st.button(f"Start {c}"):
                    st.session_state["current_case"] = c

def code_execution_interface(username, progress):
    if "current_case" not in st.session_state:
        return
    st.subheader(f"Executing {st.session_state['current_case']}")
    code = st.text_area("Enter Python Code")
    local_env = {}
    if st.button("Run Code"):
        success, result = execute_user_code(code, local_env)
        if success:
            st.success("Code executed successfully.")
            st.write(result)
            calculate_points(progress, username, 10)
            award_badge(progress, username, f"Completed {st.session_state['current_case']}")
            progress[username]["completed_cases"].append(st.session_state["current_case"])
            save_progress(progress)
            del st.session_state["current_case"]
        else:
            st.error(f"Error: {result}")

def heatmap_visualization():
    st.subheader("Anomaly Heatmap")
    data = pd.DataFrame({
        "Node": ["A","B","C","D","E"],
        "Anomaly": [2,5,1,3,4]
    })
    fig, ax = plt.subplots()
    ax.bar(data["Node"], data["Anomaly"], color='red')
    ax.set_ylabel("Anomaly Level")
    ax.set_title("Node Anomaly Heatmap")
    st.pyplot(fig)

def main():
    st.title("Python Intelligence Detective")
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        choice = st.radio("Login or Register", ["Login", "Register"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if choice == "Register":
            if st.button("Register"):
                if register_user(username, password):
                    st.success("User registered. Please login.")
                else:
                    st.error("Username already exists.")
        else:
            if st.button("Login"):
                role = authenticate_user(username, password)
                if role:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["role"] = role
                    st.success(f"Logged in as {role}")
                else:
                    st.error("Invalid credentials.")
    else:
        username = st.session_state["username"]
        progress = load_progress()
        if st.session_state["role"] == "learner":
            case_selection(username, progress)
            code_execution_interface(username, progress)
            evidence_analysis()
            render_progress_dashboard(progress, username)
            render_leaderboard(progress)
            heatmap_visualization()
        else:
            st.subheader("Instructor Dashboard")
            st.write("Instructor features like case management and learner monitoring go here.")

if __name__ == "__main__":
    main()
