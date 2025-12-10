import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import json
import os
from datetime import datetime

st.set_page_config(page_title="PYTHON INTELLIGENCE DETECTIVE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .main {background:#0d1117; color:#c9d1d9; padding:0;}
    .stApp {background:#0d1117;}
    h1,h2,h3,h4 {color:#58a6ff; font-family:'Segoe UI',sans-serif; margin:0.5rem 0;}
    .header-bar {background:#161b22; padding:1rem; text-align:center; border-bottom:3px solid #58a6ff;}
    .card {background:#161b22; border:1px solid #30363d; border-radius:12px; padding:20px; margin:15px 0;}
    .terminal {background:#010409; border:1px solid #30363d; border-radius:8px; padding:16px; font-family:'Courier New'; color:#7ce38b;}
    .badge {background:#1f6feb; color:white; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:bold; display:inline-block; margin:4px;}
    .success {background:#238636; color:white; padding:16px; border-radius:8px; text-align:center; font-size:18px; font-weight:bold;}
    .metric-big {font-size:48px; font-weight:bold; color:#58a6ff; margin:0;}
    .stTextArea > div > div > textarea {background:#010409 !important; color:#7ce38b !important; border:2px solid #30363d !important; font-family:'Courier New' !important;}
    .stButton>button {background:#238636; color:white; border:none; padding:12px 32px; border-radius:8px; font-weight:bold;}
    .stButton>button:hover {background:#2ea043;}
</style>
""", unsafe_allow_html=True)

DATA_FILE = "pid_progress.json"
if "user" not in st.session_state: st.session_state.user = None
if "progress" not in st.session_state: st.session_state.progress = {}
if "current_case" not in st.session_state: st.session_state.current_case = None

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            st.session_state.progress = json.load(f).get("data", {})

def save():
    with open(DATA_FILE, "w") as f:
        json.dump({"data": st.session_state.progress}, f)

if os.path.exists(DATA_FILE):
    load()

cases = {
    "case_01": {
        "title": "The Silent Server",
        "desc": "Server went dark at 02:14. Extract final logs.",
        "concept": "Lists & Slicing",
        "data": [
            "2024-04-01 01:50 - Login success user=admin",
            "2024-04-01 01:55 - File access /config",
            "2024-04-01 02:00 - Suspicious packet from 192.168.1.77",
            "2024-04-01 02:10 - Failed login attempt x12",
            "2024-04-01 02:12 - Root privilege escalation",
            "2024-04-01 02:14 - System shutdown initiated"
        ],
        "task": "Create variable `evidence` = last 5 log entries",
        "solution": lambda evidence=None: evidence and len(evidence) >= 5 and any("02:14" in x for x in evidence)
    },
    "case_02": {
        "title": "Phantom Traffic",
        "desc": "Find all malicious IPs in traffic dump.",
        "concept": "Loops & Conditionals",
        "prereq": "case_01",
        "data": [
            "192.168.1.10 - normal",
            "192.168.77.33 - high volume",
            "10.0.0.55 - internal",
            "192.168.77.88 - encrypted payload",
            "172.16.0.5 - normal"
        ],
        "task": "Create list `suspects` with IPs containing '77.'",
        "solution": lambda suspects=None: suspects and any("77." in x for x in suspects)
    },
    "case_03": {
        "title": "Encrypted Messages",
        "desc": "Hidden messages in emails. Reverse long words.",
        "concept": "String Operations",
        "prereq": "case_02",
        "data": [
            "Project deadline moved to friday",
            "Confidential files transferred",
            "Meeting scheduled midnight"
        ],
        "task": "Create list `decoded` with reversed words >8 letters",
        "solution": lambda decoded=None: decoded and any(x in ["yadirf", "thgindim"] for x in decoded)
    },
    "case_04": {
        "title": "The Insider",
        "desc": "Find who accessed files after 22:00.",
        "concept": "Dictionaries",
        "prereq": "case_03",
        "data": {
            "alice": "21:30",
            "bob": "23:45",
            "carol": "20:15",
            "dave": "00:30"
        },
        "task": "Create set `insiders` with late-night users",
        "solution": lambda insiders=None: insiders and {"bob", "dave"} <= set(insiders)
    },
    "case_05": {
        "title": "Anomaly Heatmap",
        "desc": "Visualize attack distribution.",
        "concept": "Visualization",
        "prereq": "case_04",
        "data": pd.DataFrame({
            "zone": ["North", "South", "East", "West", "Core"],
            "attacks": [23, 56, 12, 89, 44]
        }),
        "task": "Create variable `fig` = plotly bar chart",
        "solution": lambda fig=None: fig is not None and hasattr(fig, "data") and len(fig.data) > 0
    }
}

if not st.session_state.user:
    st.markdown("<div class='header-bar'><h1>PYTHON INTELLIGENCE DETECTIVE</h1><p>Cyber Investigation Division • Restricted Access</p></div>", unsafe_allow_html=True)
    col1, _, col2 = st.columns([1, 1, 1])
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### ENTER SYSTEM")
        name = st.text_input("Agent Callsign")
        if st.button("LOGIN", type="primary"):
            if name.strip():
                st.session_state.user = name.strip()
                if name not in st.session_state.progress:
                    st.session_state.progress[name] = {"points": 0, "badges": [], "cases": {}}
                save()
        st.markdown("</div>", unsafe_allow_html=True)

else:
    user_data = st.session_state.progress[st.session_state.user]
    points = user_data.get("points", 0)
    badges = user_data.get("badges", [])
    solved_cases = [c for c, v in user_data.get("cases", {}).items() if v.get("solved")]

    st.markdown(f"<div class='header-bar'><h1>AGENT {st.session_state.user.upper()}</h1><p>Points: {points} • Cases Solved {len(solved_cases)}/{len(cases)}</p></div>", unsafe_allow_html=True)

    tab_overview, tab_cases, tab_board, tab_leader, tab_stats = st.tabs(["OVERVIEW", "CASE FILES", "EVIDENCE BOARD", "LEADERBOARD", "AGENCY INTEL"])

    with tab_overview:
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='card'><h3>CASES SOLVED</h3><p class='metric-big'>{len(solved_cases)}</p><p>of {len(cases)}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h3>INTEL POINTS</h3><p class='metric-big'>{points}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h3>SKILLS</h3><p class='metric-big'>{len(badges)}</p></div>", unsafe_allow_html=True)
        sorted_points = sorted([d.get('points', 0) for d in st.session_state.progress.values()], reverse=True)
        rank = sorted_points.index(points) + 1 if points in sorted_points else "-"
        col4.markdown(f"<div class='card'><h3>RANK</h3><p class='metric-big'>#{rank}</p></div>", unsafe_allow_html=True)
        if badges:
            st.markdown("### ACQUIRED SKILLS")
            st.markdown(" ".join([f"<span class='badge'>{b}</span>" for b in badges]), unsafe_allow_html=True)

    with tab_cases:
        st.markdown("### ACTIVE INVESTIGATIONS")

        # Debug display of solved cases
        st.write("DEBUG: Solved Cases:", solved_cases)

        for cid, case in cases.items():
            locked = case.get("prereq") and case["prereq"] not in solved_cases
            solved = cid in solved_cases
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {case['title']}")
                    st.write(case["desc"])
                    st.caption(f"Teaches: {case['concept']}")
                with col2:
                    if solved:
                        st.success("SOLVED")
                    elif locked:
                        st.error("LOCKED")
                    else:
                        if st.button("OPEN CASE", key=cid):
                            st.session_state.current_case = cid

        if st.session_state.current_case and st.session_state.current_case not in solved_cases:
            case = cases[st.session_state.current_case]
            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"## {case['title']}")
            st.write(case["desc"])
            st.markdown("#### MISSION OBJECTIVE")
            st.write(case["task"])
            with st.expander("CLASSIFIED DATA"):
                if isinstance(case["data"], list):
                    st.code("\n".join(case["data"]))
                elif isinstance(case["data"], dict):
                    st.json(case["data"])
                else:
                    st.write(case["data"])
            code = st.text_area("YOUR CODE", height=400, key="user_code")
            if st.button("SUBMIT ANALYSIS", type="primary"):
                try:
                    local_vars = {}
                    exec(code, {}, local_vars)
                    filtered_vars = {k: v for k, v in local_vars.items() if not k.startswith("_")}

                    import inspect
                    expected_args = inspect.signature(case["solution"]).parameters.keys()
                    filtered_vars = {k: v for k, v in filtered_vars.items() if k in expected_args}

                    if case["solution"](**filtered_vars):
                        st.markdown("<div class='success'>CASE SUCCESSFULLY CRACKED</div>", unsafe_allow_html=True)
                        user_data["points"] += 150
                        user_data["cases"][st.session_state.current_case] = {"solved": True, "date": datetime.now().isoformat()}
                        if case["concept"] not in badges:
                            user_data["badges"].append(case["concept"])
                        save()
                        load()  # <-- Reload progress after saving to keep session state updated
                        st.balloons()
                    else:
                        st.error("Incorrect solution. Review evidence and try again.")
                except Exception as e:
                    st.error(f"Execution failed: {e}")

    with tab_board:
        st.markdown("### CENTRAL EVIDENCE NETWORK")
        if solved_cases:
            G = nx.DiGraph()
            for c in solved_cases:
                G.add_node(cases[c]["title"])
            for c in solved_cases:
                nxt = [k for k, v in cases.items() if v.get("prereq") == c]
                for n in nxt:
                    G.add_edge(cases[c]["title"], cases[n]["title"])
            pos = nx.kamada_kawai_layout(G)
            edge_x, edge_y = [], []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x += [x0, x1, None]
                edge_y += [y0, y1, None]
            edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=3, color="#58a6ff"), mode='lines')
            node_x, node_y, node_text = [], [], []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
            node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', text=node_text, textposition="bottom center",
                                    marker=dict(size=40, color="#238636", line=dict(width=2, color="#58a6ff")))
            fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
                paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#c9d1d9"), showlegend=False, hovermode='closest'))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No cases solved yet. Complete your first investigation to unlock the network.")

    with tab_leader:
        st.markdown("### GLOBAL LEADERBOARD")
        board = []
        for user, data in st.session_state.progress.items():
            board.append({"AGENT": user, "POINTS": data.get("points", 0),
                          "CASES": len([v for v in data.get("cases", {}).values() if v.get("solved")])})
        if board:
            df = pd.DataFrame(board).sort_values("POINTS", ascending=False).reset_index(drop=True)
            df.index += 1
            st.dataframe(df, use_container_width=True, hide_index=False)
        else:
            st.info("No agents registered.")

    with tab_stats:
        st.markdown("### AGENCY PERFORMANCE METRICS")
        total_agents = len(st.session_state.progress)
        total_points = sum(d.get("points", 0) for d in st.session_state.progress.values())
        col1, col2 = st.columns(2)
        col1.metric("Active Agents", total_agents)
        col2.metric("Total Intel Points Distributed", total_points)
        if solved_cases:
            st.markdown("### Your Solved Cases")
            for c in solved_cases:
                st.markdown(f"**{cases[c]['title']}** - {cases[c]['concept']}")
