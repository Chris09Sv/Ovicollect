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
