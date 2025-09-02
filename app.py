import streamlit as st
import pandas as pd
from snov_client import SnovClient

st.set_page_config(page_title="Snov.io Bulk Email Verifier", layout="wide")

st.title("📧 Snov.io Bulk Email Verifier")

st.sidebar.header("API Credentials")
client_id = st.sidebar.text_input("API User ID", type="password")
client_secret = st.sidebar.text_input("API Secret", type="password")

uploaded_file = st.file_uploader("Upload a CSV with an 'email' column", type=["csv"])

if uploaded_file and client_id and client_secret:
    df = pd.read_csv(uploaded_file)
    if "email" not in df.columns:
        st.error("CSV must contain an 'email' column.")
    else:
        st.success(f"Loaded {len(df)} emails for verification.")

        if st.button("Start Verification"):
            client = SnovClient(client_id, client_secret)
            try:
                client.authenticate()
                job_id = client.start_bulk_verification(df["email"].tolist())
                st.info("Verification job started. Waiting for results...")
                results = client.wait_for_results(job_id)
                results_df = pd.DataFrame(results)
                st.dataframe(results_df)

                csv = results_df.to_csv(index=False).encode("utf-8")
                st.download_button("Download Results CSV", csv, "verified_emails.csv", "text/csv")
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.warning("Please upload a CSV and enter your API credentials.")
