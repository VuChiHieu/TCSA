from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, field_validator
from underthesea import word_tokenize
import joblib
import re
import os
import asyncio
import logging

# ================================================
# CAU HINH GIOI HAN (theo Non-functional Requirements)
# ================================================

MAX_TEXT_LENGTH = 5000        # 1 cau / 1 binh luan toi da 5000 ky tu
MAX_BATCH_SIZE = 200          # toi da 200 cau trong 1 lan goi batch
MAX_KEYWORD_TEXTS = 500       # toi da 500 cau khi trich xuat tu khoa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tcsa")

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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.warning(f"Du lieu dau vao khong hop le: {exc.errors()}")
    safe_errors = jsonable_encoder(exc.errors(), exclude={"ctx"})
    return JSONResponse(
        status_code=422,
        content={
            "error": "Du lieu dau vao khong hop le",
            "detail": safe_errors
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Loi khong xac dinh: {repr(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Da xay ra loi khi xu ly yeu cau. Vui long thu lai."}
    )

# ================================================
# LOAD MO HINH
# ================================================

# Dung duong dan tuong doi tinh tu vi tri file main.py nay,
# dam bao chay dung tren moi may sau khi clone, khong phu thuoc vao
# cau truc thu muc cu the cua tung nguoi dung.
#
# __file__  = .../TCSA/backend/main.py
# parent    = .../TCSA/backend/
# parent^2  = .../TCSA/
# MODEL_DIR = .../TCSA/ai_core/models/
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "ai_core", "models")

print(f"Thu muc goc du an : {BASE_DIR}")
print(f"Thu muc mo hinh   : {MODEL_DIR}")
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
    try:
        text = text.lower()
        text = re.sub(r'http\S+|www\S+', '', text)
        text = re.sub(r'[^\w\sàáâãèéêìíòóôõùúýăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        logger.warning(f"Loi khi lam sach van ban: {repr(e)}")
        return ""

STOP_WORDS = {
    'và', 'là', 'của', 'có', 'không', 'rất', 'này', 'cho', 'với', 'được',
    'mà', 'thì', 'lại', 'còn', 'một', 'những', 'các', 'đã', 'sẽ', 'vẫn',
    'như', 'mô tả', 'thôi', 'gì', 'ra', 'vào', 'lên', 'xuống', 'quá',
    'nên', 'cũng', 'để', 'tôi', 'bạn', 'mình', 'shop', 'sản phẩm', 'hàng',
    'ạ', 'nhé', 'à', 'ơi', 'vậy', 'thế', 'đi', 'nha'
}

def extract_keywords_from_texts(texts: list[str], top_n: int = 5) -> list[dict]:
    counter = {}
    for text in texts:
        cleaned = clean_text(text)
        if not cleaned:
            continue
        try:
            tokens = word_tokenize(cleaned)
        except Exception as e:
            logger.warning(f"Loi tach tu underthesea: {repr(e)}")
            continue
        for token in tokens:
            word = token.replace('_', ' ').strip()
            if len(word) < 2 or word in STOP_WORDS:
                continue
            counter[word] = counter.get(word, 0) + 1

    sorted_words = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    return [{"word": w, "count": c} for w, c in sorted_words[:top_n]]

# ================================================
# REQUEST / RESPONSE SCHEMAS (co validation)
# ================================================

class TextInput(BaseModel):
    text: str
    model: str = "nb"

    @field_validator('text')
    @classmethod
    def text_khong_duoc_rong(cls, v):
        if v is None or v.strip() == "":
            raise ValueError("Noi dung van ban khong duoc de trong")
        if len(v) > MAX_TEXT_LENGTH:
            raise ValueError(f"Van ban vuot qua do dai cho phep ({MAX_TEXT_LENGTH} ky tu)")
        return v

    @field_validator('model')
    @classmethod
    def model_phai_hop_le(cls, v):
        if v not in ("nb", "mlp"):
            raise ValueError("model phai la 'nb' hoac 'mlp'")
        return v

class BatchInput(BaseModel):
    texts: list[str]
    model: str = "nb"

    @field_validator('texts')
    @classmethod
    def texts_phai_hop_le(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Danh sach van ban khong duoc de rong")
        if len(v) > MAX_BATCH_SIZE:
            raise ValueError(f"So luong cau vuot qua gioi han ({MAX_BATCH_SIZE} cau/lan)")
        for t in v:
            if len(t) > MAX_TEXT_LENGTH:
                raise ValueError(f"Mot cau trong danh sach vuot qua do dai cho phep ({MAX_TEXT_LENGTH} ky tu)")
        return v

    @field_validator('model')
    @classmethod
    def model_phai_hop_le(cls, v):
        if v not in ("nb", "mlp"):
            raise ValueError("model phai la 'nb' hoac 'mlp'")
        return v

class KeywordInput(BaseModel):
    texts: list[str]
    top_n: int = 5

    @field_validator('texts')
    @classmethod
    def texts_phai_hop_le(cls, v):
        if len(v) > MAX_KEYWORD_TEXTS:
            raise ValueError(f"So luong cau vuot qua gioi han ({MAX_KEYWORD_TEXTS} cau/lan)")
        return v

    @field_validator('top_n')
    @classmethod
    def top_n_phai_hop_le(cls, v):
        if v < 1 or v > 50:
            raise ValueError("top_n phai trong khoang 1 den 50")
        return v

# ================================================
# HAM XU LY 1 CAU
# ================================================

def analyze_one(text: str, model: str) -> dict:
    cleaned = clean_text(text)
    if not cleaned:
        return {"text": text, "toxic": "CLEAN", "sentiment": "NEUTRAL"}

    model_toxic = nb_toxic if model == "nb" else mlp_toxic
    model_sent  = nb_sentiment if model == "nb" else mlp_sentiment

    toxic_label = model_toxic.predict([cleaned])[0]
    sent_label  = model_sent.predict([cleaned])[0]

    return {"text": text, "toxic": toxic_label, "sentiment": sent_label}

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
async def predict_batch(data: BatchInput):
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, analyze_one, text, data.model)
        for text in data.texts
    ]
    results = await asyncio.gather(*tasks)
    return {"results": results, "total": len(results)}

@app.post("/analyze/keywords")
def analyze_keywords(data: KeywordInput):
    keywords = extract_keywords_from_texts(data.texts, data.top_n)
    return {"keywords": keywords, "total_texts_analyzed": len(data.texts)}