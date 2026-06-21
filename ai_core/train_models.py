import pandas as pd
import numpy as np
import re
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline

# ================================================
# 1. TIEN XU LY VAN BAN
# ================================================

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Chuyen thuong
    text = text.lower()
    # Xoa URL
    text = re.sub(r'http\S+|www\S+', '', text)
    # Xoa emoji va ky tu dac biet, giu lai chu Viet
    text = re.sub(r'[^\w\sàáâãèéêìíòóôõùúýăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]', ' ', text)
    # Xoa khoang trang thua
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ================================================
# 2. LOAD VA XU LY DU LIEU TOXIC
# ================================================

print("Dang xu ly du lieu Toxic...")

df_toxic = pd.read_csv(r"D:\TriTueNhanTao\Hieuha\TCSA\ai_core\data\vihsd\vihsd-main\data\vihsd\train.csv")
df_toxic = df_toxic[['free_text', 'label_id']].dropna()
df_toxic['free_text'] = df_toxic['free_text'].apply(clean_text)
df_toxic = df_toxic[df_toxic['free_text'].str.len() > 2]

# Doi nhan so sang chu
label_toxic_map = {0: 'CLEAN', 1: 'OFFENSIVE', 2: 'HATE'}
df_toxic['label'] = df_toxic['label_id'].map(label_toxic_map)

X_toxic = df_toxic['free_text']
y_toxic = df_toxic['label']

X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
    X_toxic, y_toxic, test_size=0.2, random_state=42, stratify=y_toxic
)

print(f"Train: {len(X_train_t)} mau | Test: {len(X_test_t)} mau")
print("Phan bo nhan:", y_toxic.value_counts().to_dict())

# ================================================
# 3. LOAD VA XU LY DU LIEU SENTIMENT
# ================================================

print("\nDang xu ly du lieu Sentiment...")

df_sent = pd.read_csv(r"D:\TriTueNhanTao\Hieuha\TCSA\ai_core\data\sentiment\data - data.csv")
df_sent = df_sent[['comment', 'label']].dropna()
df_sent['comment'] = df_sent['comment'].apply(clean_text)
df_sent = df_sent[df_sent['comment'].str.len() > 2]

# Giu lai nhan POS va NEG, them NEUTRAL tu rate neu co
# Bo cac nhan khong hop le
df_sent = df_sent[df_sent['label'].isin(['POS', 'NEG'])]

X_sent = df_sent['comment']
y_sent = df_sent['label']

X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
    X_sent, y_sent, test_size=0.2, random_state=42, stratify=y_sent
)

print(f"Train: {len(X_train_s)} mau | Test: {len(X_test_s)} mau")
print("Phan bo nhan:", y_sent.value_counts().to_dict())

# ================================================
# 4. HUAN LUYEN MO HINH TOXIC
# ================================================

print("\n--- Huan luyen mo hinh Toxic ---")

# Naive Bayes
print("Dang huan luyen Naive Bayes Toxic...")
pipe_nb_toxic = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
    ('clf', MultinomialNB())
])
pipe_nb_toxic.fit(X_train_t, y_train_t)
y_pred = pipe_nb_toxic.predict(X_test_t)
print("Naive Bayes Toxic Accuracy:", round(accuracy_score(y_test_t, y_pred), 4))
print(classification_report(y_test_t, y_pred))

# MLP
print("Dang huan luyen MLP Toxic (co the mat vai phut)...")
pipe_mlp_toxic = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
    ('clf', MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=30, random_state=42, verbose=False))
])
pipe_mlp_toxic.fit(X_train_t, y_train_t)
y_pred = pipe_mlp_toxic.predict(X_test_t)
print("MLP Toxic Accuracy:", round(accuracy_score(y_test_t, y_pred), 4))
print(classification_report(y_test_t, y_pred))

# ================================================
# 5. HUAN LUYEN MO HINH SENTIMENT
# ================================================

print("\n--- Huan luyen mo hinh Sentiment ---")

# Naive Bayes
print("Dang huan luyen Naive Bayes Sentiment...")
pipe_nb_sent = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
    ('clf', MultinomialNB())
])
pipe_nb_sent.fit(X_train_s, y_train_s)
y_pred = pipe_nb_sent.predict(X_test_s)
print("Naive Bayes Sentiment Accuracy:", round(accuracy_score(y_test_s, y_pred), 4))
print(classification_report(y_test_s, y_pred))

# MLP
print("Dang huan luyen MLP Sentiment (co the mat vai phut)...")
pipe_mlp_sent = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
    ('clf', MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=30, random_state=42, verbose=False))
])
pipe_mlp_sent.fit(X_train_s, y_train_s)
y_pred = pipe_mlp_sent.predict(X_test_s)
print("MLP Sentiment Accuracy:", round(accuracy_score(y_test_s, y_pred), 4))
print(classification_report(y_test_s, y_pred))

# ================================================
# 6. LUU MO HINH
# ================================================

print("\nDang luu mo hinh...")
os.makedirs(r"D:\TriTueNhanTao\Hieuha\TCSA\ai_core\models", exist_ok=True)

joblib.dump(pipe_nb_toxic,  r"D:\TriTueNhanTao\Hieuha\TCSA\ai_core\models\nb_toxic.pkl")
joblib.dump(pipe_mlp_toxic, r"D:\TriTueNhanTao\Hieuha\TCSA\ai_core\models\mlp_toxic.pkl")
joblib.dump(pipe_nb_sent,   r"D:\TriTueNhanTao\Hieuha\TCSA\ai_core\models\nb_sentiment.pkl")
joblib.dump(pipe_mlp_sent,  r"D:\TriTueNhanTao\Hieuha\TCSA\ai_core\models\mlp_sentiment.pkl")

print("Da luu xong 4 mo hinh vao thu muc models/")
print("Hoan tat Giai doan 2!")