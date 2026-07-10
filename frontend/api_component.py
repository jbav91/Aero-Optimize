import streamlit as st
import requests

def execute_and_display_results(api_url, payload):
    """Sends the payload to the backend and renders the UI results."""
    with st.spinner("Querying XGBoost and PuLP Engines..."):
        try:
            response = requests.post(api_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                status = result['flight_status']
                
                col1, col2, col3 = st.columns(3)
                
                if status == "On Time":
                    col1.metric("Predicted Status", "✅ On Time")
                    col2.metric("Action Required", "None")
                    col3.metric("Crew Cost Impact", "$0")
                    st.success("The flight is cleared for an on-time departure. Standard crew remains assigned.")
                else:
                    col1.metric("Predicted Status", "🚨 Delayed")
                    col2.metric("Action Required", "Standby Activated")
                    
                    opt_details = result.get('optimization_details', {})
                    if opt_details.get('Status') == 'Optimal': 
                        col3.metric("Optimized Crew Cost", f"${opt_details['Total_Hourly_Cost']} / hr")
                        st.warning("High risk of delay detected. Original crew is projected to time out.")
                        st.info(f"**Optimal Legal Crew Found:** {', '.join(opt_details['Selected_Crew'])}")
                    else:
                        col3.metric("Optimized Crew Cost", "ERROR")
                        st.error(f"Optimization failed: {opt_details.get('Message', 'Not enough legal hours.')}")
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Ensure FastAPI is running.")