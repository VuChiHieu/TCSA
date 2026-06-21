from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import re
import os

# ================================================
# KHOI TAO APP
# ================================================

app = FastAPI(title="TCSA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================
# LOAD MO HINH
# ================================================

MODEL_DIR = r"D:\TriTueNhanTao\Hieuha\TCSA\ai_core\models"

print("Dang load mo hinh...")
nb_toxic     = joblib.load(os.path.join(MODEL_DIR, "nb_toxic.pkl"))
mlp_toxic    = joblib.load(os.path.join(MODEL_DIR, "mlp_toxic.pkl"))
nb_sentiment = joblib.load(os.path.join(MODEL_DIR, "nb_sentiment.pkl"))
mlp_sentiment= joblib.load(os.path.join(MODEL_DIR, "mlp_sentiment.pkl"))
print("Load mo hinh thanh cong!")

# ================================================
# TIEN XU LY
# ================================================

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^\w\sàáâãèéêìíòóôõùúýăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ================================================
# REQUEST / RESPONSE SCHEMAS
# ================================================

class TextInput(BaseModel):
    text: str
    model: str = "nb"  # "nb" hoac "mlp"

class BatchInput(BaseModel):
    texts: list[str]
    model: str = "nb"

# ================================================
# ENDPOINTS
# ================================================

@app.get("/")
def root():
    return {"message": "TCSA API dang chay", "version": "1.0.0"}

@app.post("/predict/toxic")
def predict_toxic(data: TextInput):
    cleaned = clean_text(data.text)
    if not cleaned:
        return {"label": "CLEAN", "confidence": 1.0}
    
    model = nb_toxic if data.model == "nb" else mlp_toxic
    label = model.predict([cleaned])[0]
    proba = model.predict_proba([cleaned])[0]
    confidence = round(float(max(proba)), 4)
    
    return {
        "original_text": data.text,
        "cleaned_text": cleaned,
        "label": label,
        "confidence": confidence,
        "model_used": data.model
    }

@app.post("/predict/sentiment")
def predict_sentiment(data: TextInput):
    cleaned = clean_text(data.text)
    if not cleaned:
        return {"label": "NEUTRAL", "confidence": 1.0}
    
    model = nb_sentiment if data.model == "nb" else mlp_sentiment
    label = model.predict([cleaned])[0]
    proba = model.predict_proba([cleaned])[0]
    confidence = round(float(max(proba)), 4)
    
    return {
        "original_text": data.text,
        "cleaned_text": cleaned,
        "label": label,
        "confidence": confidence,
        "model_used": data.model
    }

@app.post("/predict/full")
def predict_full(data: TextInput):
    cleaned = clean_text(data.text)
    if not cleaned:
        return {
            "toxic": {"label": "CLEAN", "confidence": 1.0},
            "sentiment": {"label": "NEUTRAL", "confidence": 1.0}
        }
    
    model_toxic = nb_toxic if data.model == "nb" else mlp_toxic
    model_sent  = nb_sentiment if data.model == "nb" else mlp_sentiment
    
    toxic_label = model_toxic.predict([cleaned])[0]
    toxic_proba = round(float(max(model_toxic.predict_proba([cleaned])[0])), 4)
    
    sent_label  = model_sent.predict([cleaned])[0]
    sent_proba  = round(float(max(model_sent.predict_proba([cleaned])[0])), 4)
    
    return {
        "original_text": data.text,
        "toxic": {
            "label": toxic_label,
            "confidence": toxic_proba
        },
        "sentiment": {
            "label": sent_label,
            "confidence": sent_proba
        },
        "model_used": data.model
    }

@app.post("/predict/batch")
def predict_batch(data: BatchInput):
    results = []
    model_toxic = nb_toxic if data.model == "nb" else mlp_toxic
    model_sent  = nb_sentiment if data.model == "nb" else mlp_sentiment
    
    for text in data.texts:
        cleaned = clean_text(text)
        if not cleaned:
            results.append({
                "text": text,
                "toxic": "CLEAN",
                "sentiment": "NEUTRAL"
            })
            continue
        
        toxic_label = model_toxic.predict([cleaned])[0]
        sent_label  = model_sent.predict([cleaned])[0]
        
        results.append({
            "text": text,
            "toxic": toxic_label,
            "sentiment": sent_label
        })
    
    return {"results": results, "total": len(results)}