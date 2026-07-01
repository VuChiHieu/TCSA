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
from sklearn.utils import resample

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "ai_core", "data")
MODEL_DIR  = os.path.join(BASE_DIR, "ai_core", "models")

VIHSD_TRAIN = os.path.join(DATA_DIR, "vihsd", "vihsd-main", "data", "vihsd", "train.csv")
VIHSD_TEST  = os.path.join(DATA_DIR, "vihsd", "vihsd-main", "data", "vihsd", "test.csv")
VIHSD_DEV   = os.path.join(DATA_DIR, "vihsd", "vihsd-main", "data", "vihsd", "dev.csv")
SENTIMENT   = os.path.join(DATA_DIR, "sentiment", "data - data.csv")

print(f"Thu muc goc du an : {BASE_DIR}")
print(f"Thu muc du lieu   : {DATA_DIR}")
print(f"Thu muc mo hinh   : {MODEL_DIR}")

# ================================================
# 1. TIEN XU LY VAN BAN
# ================================================

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^\w\sàáâãèéêìíòóôõùúýăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ================================================
# 2. LOAD DU LIEU TOXIC
# ================================================

print("\nDang xu ly du lieu Toxic...")

df_train = pd.read_csv(VIHSD_TRAIN)
df_test  = pd.read_csv(VIHSD_TEST)
df_dev   = pd.read_csv(VIHSD_DEV)

df_toxic = pd.concat([df_train, df_dev], ignore_index=True)
df_toxic = df_toxic[['free_text', 'label_id']].dropna()
df_toxic['free_text'] = df_toxic['free_text'].apply(clean_text)
df_toxic = df_toxic[df_toxic['free_text'].str.len() > 2]

label_map = {0: 'CLEAN', 1: 'OFFENSIVE', 2: 'HATE'}
df_toxic['label'] = df_toxic['label_id'].map(label_map)

df_clean     = df_toxic[df_toxic['label'] == 'CLEAN']
df_offensive = df_toxic[df_toxic['label'] == 'OFFENSIVE']
df_hate      = df_toxic[df_toxic['label'] == 'HATE']

target_size = len(df_clean)
df_offensive_up = resample(df_offensive, replace=True, n_samples=target_size // 2, random_state=42)
df_hate_up      = resample(df_hate,      replace=True, n_samples=target_size // 2, random_state=42)

df_toxic_balanced = pd.concat([df_clean, df_offensive_up, df_hate_up], ignore_index=True)
df_toxic_balanced = df_toxic_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Du lieu sau can bang: {df_toxic_balanced['label'].value_counts().to_dict()}")

X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
    df_toxic_balanced['free_text'], df_toxic_balanced['label'],
    test_size=0.2, random_state=42, stratify=df_toxic_balanced['label']
)

df_test_real = df_test[['free_text', 'label_id']].dropna()
df_test_real['free_text'] = df_test_real['free_text'].apply(clean_text)
df_test_real['label'] = df_test_real['label_id'].map(label_map)
df_test_real = df_test_real[df_test_real['free_text'].str.len() > 2]

# ================================================
# 3. LOAD DU LIEU SENTIMENT
# ================================================

print("Dang xu ly du lieu Sentiment...")

df_sent = pd.read_csv(SENTIMENT)
df_sent = df_sent[['comment', 'label']].dropna()
df_sent['comment'] = df_sent['comment'].apply(clean_text)
df_sent = df_sent[df_sent['label'].isin(['POS', 'NEG'])]
df_sent = df_sent[df_sent['comment'].str.len() > 2]

df_pos = df_sent[df_sent['label'] == 'POS']
df_neg = df_sent[df_sent['label'] == 'NEG']
df_neg_up = resample(df_neg, replace=True, n_samples=len(df_pos), random_state=42)
df_sent_balanced = pd.concat([df_pos, df_neg_up]).sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Du lieu sentiment sau can bang: {df_sent_balanced['label'].value_counts().to_dict()}")

X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
    df_sent_balanced['comment'], df_sent_balanced['label'],
    test_size=0.2, random_state=42, stratify=df_sent_balanced['label']
)

# ================================================
# 4. HUAN LUYEN MO HINH TOXIC
# ================================================

print("\n--- Huan luyen mo hinh Toxic ---")

print("Naive Bayes Toxic...")
pipe_nb_toxic = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=15000, ngram_range=(1, 3), sublinear_tf=True)),
    ('clf', MultinomialNB(alpha=0.5))
])
pipe_nb_toxic.fit(X_train_t, y_train_t)
y_pred = pipe_nb_toxic.predict(df_test_real['free_text'])
print("Naive Bayes Toxic (test that):")
print(f"Accuracy: {round(accuracy_score(df_test_real['label'], y_pred), 4)}")
print(classification_report(df_test_real['label'], y_pred))

print("MLP Toxic (mat 5-10 phut)...")
pipe_mlp_toxic = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=15000, ngram_range=(1, 2), sublinear_tf=True)),
    ('clf', MLPClassifier(
        hidden_layer_sizes=(256, 128, 64),
        max_iter=100,
        random_state=42,
        verbose=False
    ))
])
pipe_mlp_toxic.fit(X_train_t, y_train_t)
y_pred = pipe_mlp_toxic.predict(df_test_real['free_text'])
print("MLP Toxic (test that):")
print(f"Accuracy: {round(accuracy_score(df_test_real['label'], y_pred), 4)}")
print(classification_report(df_test_real['label'], y_pred))

# ================================================
# 5. HUAN LUYEN MO HINH SENTIMENT
# ================================================

print("\n--- Huan luyen mo hinh Sentiment ---")

print("Naive Bayes Sentiment...")
pipe_nb_sent = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=15000, ngram_range=(1, 3), sublinear_tf=True)),
    ('clf', MultinomialNB(alpha=0.3))
])
pipe_nb_sent.fit(X_train_s, y_train_s)
y_pred = pipe_nb_sent.predict(X_test_s)
print(f"Accuracy: {round(accuracy_score(y_test_s, y_pred), 4)}")
print(classification_report(y_test_s, y_pred))

print("MLP Sentiment...")
pipe_mlp_sent = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=15000, ngram_range=(1, 2), sublinear_tf=True)),
    ('clf', MLPClassifier(
        hidden_layer_sizes=(256, 128, 64),
        max_iter=100,
        random_state=42,
        verbose=False
    ))
])
pipe_mlp_sent.fit(X_train_s, y_train_s)
y_pred = pipe_mlp_sent.predict(X_test_s)
print(f"Accuracy: {round(accuracy_score(y_test_s, y_pred), 4)}")
print(classification_report(y_test_s, y_pred))

# ================================================
# 6. LUU MO HINH
# ================================================

print("\nDang luu mo hinh v2...")
os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(pipe_nb_toxic,  os.path.join(MODEL_DIR, "nb_toxic.pkl"))
joblib.dump(pipe_mlp_toxic, os.path.join(MODEL_DIR, "mlp_toxic.pkl"))
joblib.dump(pipe_nb_sent,   os.path.join(MODEL_DIR, "nb_sentiment.pkl"))
joblib.dump(pipe_mlp_sent,  os.path.join(MODEL_DIR, "mlp_sentiment.pkl"))

print("Da luu xong 4 mo hinh v2!")
print("Hoan tat huan luyen mo hinh!")