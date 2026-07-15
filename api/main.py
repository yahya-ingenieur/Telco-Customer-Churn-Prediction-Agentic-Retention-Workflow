from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "churn_pipeline.pkl"

app = FastAPI(title="Telco Churn Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = None


@app.on_event("startup")
def load_model():
    global pipeline
    pipeline = joblib.load(MODEL_PATH)


class CustomerInput(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": jsonable_encoder(exc.errors())})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(customer: CustomerInput):
    try:
        df = pd.DataFrame([customer.model_dump()])
        prediction = pipeline.predict(df)[0]
        probability = pipeline.predict_proba(df)[0][1]
        return {
            "churn_prediction": "Yes" if prediction == 1 else "No",
            "churn_probability": round(float(probability), 4),
        }
    except Exception as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
