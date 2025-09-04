import streamlit as st
import pandas as pd
from itertools import combinations

# 🧠 Load all required data
def load_data():
    profiles = pd.read_csv("employee_profiles.csv")
    tasks = pd.read_csv("task_inputs.csv")
    traits = pd.read_csv("employee_trait_scores.csv")
    skills = pd.read_csv("skill_match_scores.csv")
    synergy = pd.read_csv("employee_synergy_scores.csv")
    teams = pd.read_csv("top_team_recommendations.csv")
    solo = pd.read_csv("top_solo_recommendations.csv")
    return profiles, tasks, traits, skills, synergy, teams, solo

df_profiles, df_tasks, df_traits, df_skills, df_synergy, df_teams, df_solo = load_data()

# 🔧 Synergy lookup
def synergy_score(emp1, emp2):
    match = df_synergy[
        ((df_synergy["Employee 1"] == emp1) & (df_synergy["Employee 2"] == emp2)) |
        ((df_synergy["Employee 1"] == emp2) & (df_synergy["Employee 2"] == emp1))
    ]
    return match["Synergy Score"].values[0] if not match.empty else 0

# 🎯 Task-based team selector
def get_best_teams(task_name, top_n=3):
    task_data = df_skills[df_skills["Task Name"].str.lower() == task_name.lower()]
    people = task_data["Employee Name"].unique()
    if len(people) < 3:
        return "❌ Not enough employees for a team."

    combos = list(combinations(people, 3))
    team_results = []

    for team in combos:
        skill_sum = task_data[task_data["Employee Name"].isin(team)]["Match Score"].sum()
        synergy_sum = (
            synergy_score(team[0], team[1]) +
            synergy_score(team[0], team[2]) +
            synergy_score(team[1], team[2])
        )
        total = skill_sum + synergy_sum
        team_results.append({
            "Team": ", ".join(team),
            "Skill Score": skill_sum,
            "Synergy Score": synergy_sum,
            "Total Score": total,
            "Explanation": f"Skill: {skill_sum}, Synergy: {synergy_sum} → Total: {total}"
        })

    df = pd.DataFrame(team_results)
    return df.sort_values(by="Total Score", ascending=False).head(top_n)

# 🖥️ Streamlit UI
st.set_page_config(page_title="Team Harmony Engine", layout="wide")
st.title("🧠 Task-Based Team Matcher")
st.markdown("Welcome to the Team Harmony Engine — built by Anurag 🚀")

# 🎭 Role selection
role = st.sidebar.radio("Who are you?", ["Admin", "Employee"])

# 🔐 Admin View
if role == "Admin":
    tab1, tab2, tab3 = st.tabs(["📋 Task Matching", "📊 Insights", "🧑‍💼 Profiles"])

    with tab1:
        st.subheader("🔍 Match Teams for a Task")
        task_options = sorted(df_tasks["Task Name"].unique())
        selected_task = st.selectbox("Select a Task", task_options)

        if selected_task:
            st.markdown("### 🏆 Best Solo Performer")
            solo = df_skills[df_skills["Task Name"].str.lower() == selected_task.lower()]
            solo_top = solo.sort_values(by="Match Score", ascending=False).head(1)[["Employee Name", "Match Score"]]
            st.dataframe(solo_top, use_container_width=True)

            st.markdown("### 👥 Top 3 Team Recommendations")
            team_result = get_best_teams(selected_task, top_n=3)
            if isinstance(team_result, pd.DataFrame):
                st.dataframe(team_result, use_container_width=True)
                with st.expander("See explanation for top team"):
                    st.write(team_result["Explanation"].iloc[0])
            else:
                st.warning(team_result)

    with tab2:
        st.subheader("📊 Top 5 Teams (Overall)")
        st.dataframe(df_teams.head(5), use_container_width=True)

        st.subheader("🌟 Top Solo Performers (Overall)")
        st.dataframe(df_solo.head(5), use_container_width=True)

    with tab3:
        st.subheader("🧑‍💼 All Employee Profiles")
        st.dataframe(df_profiles, use_container_width=True)

# 👤 Employee View
else:
    st.subheader("👋 Welcome Employee")
    st.markdown("Your profile has been saved. Please contact Admin for task assignments.")
    st.dataframe(df_profiles[df_profiles["Name"].str.lower() == "anurag"], use_container_width=True)

# Footer
st.markdown("---")
st.caption("Streamlit App · File 08 · Modular, Interactive, and Built for Real HR Impact 💼")



