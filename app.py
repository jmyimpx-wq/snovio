import streamlit as st
import pandas as pd
import requests
import io
import chardet

st.set_page_config(page_title="Snov.io Bulk Email Verifier", layout="wide")

st.sidebar.header("API Credentials")
api_user = st.sidebar.text_input("API User ID", type="password")
api_secret = st.sidebar.text_input("API Secret", type="password")

st.title("📧 Bulk Email Verifier with Snov.io")

uploaded_file = st.file_uploader("Upload a CSV file with emails", type=["csv"])

if uploaded_file is not None:
    raw_data = uploaded_file.read()
    result = chardet.detect(raw_data)
    encoding = result["encoding"]

    try:
        df = pd.read_csv(io.BytesIO(raw_data), encoding=encoding)
        st.success(f"CSV loaded successfully using encoding: {encoding}")
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        st.stop()

    if "email" not in df.columns:
        st.error("CSV must contain an 'email' column.")
        st.stop()

    st.write("### Preview of uploaded data")
    st.dataframe(df.head())

    if st.button("Verify Emails"):
        if not api_user or not api_secret:
            st.error("Please enter your API credentials in the sidebar.")
        else:
            verified_results = []
            for email in df["email"]:
                try:
                    url = "https://api.snov.io/v1/get-emails-verification-status"
                    headers = {"Content-Type": "application/json"}
                    payload = {"email": email}
                    response = requests.post(url, json=payload, auth=(api_user, api_secret))

                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("data", {}).get("status", "unknown")
                    else:
                        status = f"error {response.status_code}"

                except Exception as e:
                    status = f"error {str(e)}"

                verified_results.append({"email": email, "status": status})

            result_df = pd.DataFrame(verified_results)
            st.write("### Verification Results")
            st.dataframe(result_df)

            csv_out = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇ Download Verified Results",
                data=csv_out,
                file_name="verified_emails.csv",
                mime="text/csv",
            )
