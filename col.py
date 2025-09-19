import streamlit as st
import requests
import datetime

API_URL = "http://127.0.0.1:8000"



import streamlit as st
import requests
import datetime

API_URL = "http://127.0.0.1:8000"  # Your FastAPI base URL

def report_pending_traps():
    st.title("Pending Weekly Reports - Ovitrampas")

    access_token = st.session_state.get("access_token")
    if not access_token:
        st.error("You must be logged in to see pending traps.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # --- Select the reporting week manually ---
    today = datetime.date.today()
    default_week_number = today.isocalendar()[1]
    default_year = today.year

    st.subheader("Select Week to Report")

    selected_year = st.number_input("Year", value=default_year, step=1)
    selected_week = st.number_input("Week Number (1-52)", min_value=1, max_value=52, value=default_week_number)

    # --- Load pending traps ---
    response = requests.get(f"{API_URL}/trap_reports/pending/", headers=headers)

    if response.status_code != 200:
        st.error(f"Failed to load traps: {response.text}")
        return

    pending_traps = response.json()

    if not pending_traps:
        st.success("All traps have been reported for this week!")
        return

    st.write(f"Found {len(pending_traps)} traps needing report.")

    # Pick trap
    selected_trap = st.selectbox(
        "Select a Trap to Report",
        options=pending_traps,
        format_func=lambda trap: f"Trap {trap['trap_key']} (ID: {trap['id']})"
    )

    is_positive = st.radio("Trap Result", options=["Positive", "Negative"])
    positive_flag = is_positive == "Positive"

    access_token = st.session_state.get("access_token")
    user_id = 1 # st.session_state.get("user_id")

    if not access_token:
        st.error("Please login first to submit.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }


    payload = {
        "trap_id": selected_trap["id"],  # Correct: use trap ID
        "week_number": selected_week,
        "year": selected_year,
        "is_positive": positive_flag,
        "created_by": user_id
    }

    submit_response = requests.post(
        f"{API_URL}/trap_reports/",   # Correct endpoint
        json=payload,                 # JSON payload
        headers=headers                # ✅ Correct headers with token
    )

    # Handle response
    if submit_response.status_code == 200:
        st.success("Trap report submitted successfully!")
    else:
        st.error(f"Failed to submit trap report: {submit_response.status_code} - {submit_response.text}")


def trap_dashboard():
    st.title("Ovitrampas Weekly Dashboard")

    access_token = st.session_state.get("access_token")
    if not access_token:
        st.error("You must be logged in.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(f"{API_URL}/trap_reports/summary/", headers=headers)

    if response.status_code != 200:
        st.error(f"Failed to load summary: {response.text}")
        return

    summary = response.json()

    st.metric("Total Reports", summary["total_reports"])
    st.metric("Positive Traps", summary["positive_reports"])
    st.metric("Negative Traps", summary["negative_reports"])



trap_dashboard()