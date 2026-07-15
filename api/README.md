# Telco Churn Prediction API

## Run locally

From the project root:

```
uvicorn api.main:app --reload --port 8000
```

## Endpoints

- `GET /health` — health check
- `POST /predict` — predict churn for a single customer

## Example request

Using Git Bash / a POSIX shell:

```
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"gender": "Male", "SeniorCitizen": 0, "Partner": "Yes", "Dependents": "Yes", "tenure": 72, "PhoneService": "Yes", "MultipleLines": "Yes", "InternetService": "Fiber optic", "OnlineSecurity": "Yes", "OnlineBackup": "Yes", "DeviceProtection": "Yes", "TechSupport": "Yes", "StreamingTV": "Yes", "StreamingMovies": "Yes", "Contract": "Two year", "PaperlessBilling": "Yes", "PaymentMethod": "Credit card (automatic)", "MonthlyCharges": 114.05, "TotalCharges": 8468.2}'
```

Using PowerShell:

```
curl.exe -X POST http://localhost:8000/predict `
  -H "Content-Type: application/json" `
  -d '{\"gender\": \"Male\", \"SeniorCitizen\": 0, \"Partner\": \"Yes\", \"Dependents\": \"Yes\", \"tenure\": 72, \"PhoneService\": \"Yes\", \"MultipleLines\": \"Yes\", \"InternetService\": \"Fiber optic\", \"OnlineSecurity\": \"Yes\", \"OnlineBackup\": \"Yes\", \"DeviceProtection\": \"Yes\", \"TechSupport\": \"Yes\", \"StreamingTV\": \"Yes\", \"StreamingMovies\": \"Yes\", \"Contract\": \"Two year\", \"PaperlessBilling\": \"Yes\", \"PaymentMethod\": \"Credit card (automatic)\", \"MonthlyCharges\": 114.05, \"TotalCharges\": 8468.2}'
```

Expected response:

```
{"churn_prediction": "No", "churn_probability": 0.1171}
```
