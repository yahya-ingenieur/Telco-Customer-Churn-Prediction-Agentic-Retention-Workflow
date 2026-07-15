from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

WEBHOOK_URL = "http://localhost:5678/webhook/churn-predict"
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cleaned_telco.csv"

RED = "#D62728"     # churn
GREEN = "#2CA02C"   # retained
CHURN_COLORS = {"Yes": RED, "No": GREEN}

st.set_page_config(page_title="Telco Churn Retention Demo", page_icon="📉", layout="wide")

st.title("📉 Telco Customer Churn — Agentic Retention Demo")
st.markdown(
    "Enter a customer's profile to get a **churn prediction** from the ML model, an "
    "**AI-generated retention action**, and an automatic **Telegram alert** — all orchestrated "
    "through an n8n agentic workflow."
)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


tab_predict, tab_insights = st.tabs(["🔮 Live Prediction", "📊 Data Insights"])

# ---------------------------------------------------------------- Tab 1
with tab_predict:
    with st.form("customer_form"):
        st.subheader("Customer Profile")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            gender = st.selectbox("Gender", ["Female", "Male"])
            senior = st.selectbox("Senior Citizen", ["No", "Yes"])
            partner = st.selectbox("Partner", ["No", "Yes"])
            dependents = st.selectbox("Dependents", ["No", "Yes"])
        with c2:
            phone_service = st.selectbox("Phone Service", ["Yes", "No"])
            multiple_lines = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"])
            internet_service = st.selectbox("Internet Service", ["Fiber optic", "DSL", "No"])
            online_security = st.selectbox("Online Security", ["No", "Yes", "No internet service"])
        with c3:
            online_backup = st.selectbox("Online Backup", ["No", "Yes", "No internet service"])
            device_protection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"])
            tech_support = st.selectbox("Tech Support", ["No", "Yes", "No internet service"])
            streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
        with c4:
            streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])
            contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
            paperless = st.selectbox("Paperless Billing", ["Yes", "No"])
            payment_method = st.selectbox(
                "Payment Method",
                ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
            )

        n1, n2, n3 = st.columns(3)
        with n1:
            tenure = st.number_input("Tenure (months)", min_value=0, max_value=100, value=5)
        with n2:
            monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, max_value=200.0, value=85.0, step=0.05)
        with n3:
            total_charges = st.number_input("Total Charges ($)", min_value=0.0, max_value=10000.0, value=425.0, step=0.05)

        submitted = st.form_submit_button("🚀 Predict & Send Alert", use_container_width=True)

    if submitted:
        payload = {
            "gender": gender,
            "SeniorCitizen": 1 if senior == "Yes" else 0,
            "Partner": partner,
            "Dependents": dependents,
            "tenure": int(tenure),
            "PhoneService": phone_service,
            "MultipleLines": multiple_lines,
            "InternetService": internet_service,
            "OnlineSecurity": online_security,
            "OnlineBackup": online_backup,
            "DeviceProtection": device_protection,
            "TechSupport": tech_support,
            "StreamingTV": streaming_tv,
            "StreamingMovies": streaming_movies,
            "Contract": contract,
            "PaperlessBilling": paperless,
            "PaymentMethod": payment_method,
            "MonthlyCharges": float(monthly_charges),
            "TotalCharges": float(total_charges),
        }

        try:
            with st.spinner("Running churn model + retention agent..."):
                response = requests.post(WEBHOOK_URL, json=payload, timeout=90)
            response.raise_for_status()
            result = response.json()

            prediction = result.get("churn_prediction", "?")
            probability = float(result.get("churn_probability", 0.0))
            recommendation = result.get("agent_recommendation", "No recommendation returned.")

            r1, r2 = st.columns([1, 2])
            with r1:
                if prediction == "Yes":
                    st.error("### ⚠️ Likely to CHURN")
                else:
                    st.success("### ✅ Likely to STAY")
                st.metric("Churn Probability", f"{probability:.1%}")
                st.progress(min(max(probability, 0.0), 1.0))
            with r2:
                st.markdown("#### 🤖 Agent Retention Recommendation")
                if prediction == "Yes":
                    st.warning(recommendation)
                else:
                    st.info(recommendation)
                st.caption("📨 A Telegram alert with this recommendation was sent to the retention team.")

        except requests.exceptions.ConnectionError:
            st.error(
                "Could not reach the n8n webhook at "
                f"`{WEBHOOK_URL}`. Make sure n8n is running (Docker) and the "
                "'Churn Retention Workflow' is **active**."
            )
        except requests.exceptions.Timeout:
            st.error("The request timed out — check that the FastAPI server and n8n workflow are running.")
        except (ValueError, requests.exceptions.HTTPError) as exc:
            st.error(f"The webhook returned an unexpected response: {exc}")

# ---------------------------------------------------------------- Tab 2
with tab_insights:
    df = load_data()

    i1, i2 = st.columns(2)

    with i1:
        churn_counts = df["Churn"].value_counts().reset_index()
        churn_counts.columns = ["Churn", "Customers"]
        fig = px.pie(
            churn_counts, names="Churn", values="Customers", color="Churn",
            color_discrete_map=CHURN_COLORS, title="Churn Distribution", hole=0.35,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("About 1 in 4 customers churn — the class imbalance the model must handle.")

        fig = px.histogram(
            df, x="tenure", color="Churn", color_discrete_map=CHURN_COLORS,
            barmode="overlay", nbins=36, opacity=0.65,
            title="Tenure Distribution by Churn", labels={"tenure": "Tenure (months)"},
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Churn is heavily concentrated in the first months of a customer's lifetime.")

    with i2:
        contract_rate = (
            df.groupby("Contract")["Churn"].apply(lambda s: (s == "Yes").mean() * 100)
            .reset_index(name="Churn Rate (%)").sort_values("Churn Rate (%)", ascending=False)
        )
        fig = px.bar(
            contract_rate, x="Contract", y="Churn Rate (%)", title="Churn Rate by Contract Type",
            text_auto=".1f", color_discrete_sequence=[RED],
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Month-to-month contracts churn drastically more than one/two-year contracts.")

        internet_rate = (
            df.groupby("InternetService")["Churn"].apply(lambda s: (s == "Yes").mean() * 100)
            .reset_index(name="Churn Rate (%)").sort_values("Churn Rate (%)", ascending=False)
        )
        fig = px.bar(
            internet_rate, x="InternetService", y="Churn Rate (%)", title="Churn Rate by Internet Service",
            text_auto=".1f", color_discrete_sequence=[RED],
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Fiber-optic customers churn the most — a price/quality sensitivity signal.")
