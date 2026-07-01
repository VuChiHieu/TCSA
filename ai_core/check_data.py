import pandas as pd
import os


BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "ai_core", "data")

VIHSD_TRAIN = os.path.join(DATA_DIR, "vihsd", "vihsd-main", "data", "vihsd", "train.csv")
SENTIMENT   = os.path.join(DATA_DIR, "sentiment", "data - data.csv")

print(f"Thu muc goc du an : {BASE_DIR}")
print(f"Thu muc du lieu   : {DATA_DIR}")

# Kiem tra du lieu toxic
print("\n=== DU LIEU TOXIC (ViHSD) ===")
df_train = pd.read_csv(VIHSD_TRAIN)
print("Columns:", df_train.columns.tolist())
print("Shape:", df_train.shape)
print("Nhan phan loai:")
print(df_train.iloc[:, -1].value_counts())
print("\nVai dong dau:")
print(df_train.head(3))

print("\n=== DU LIEU SENTIMENT ===")
df_sent = pd.read_csv(SENTIMENT)
print("Columns:", df_sent.columns.tolist())
print("Shape:", df_sent.shape)
print("Nhan phan loai:")
print(df_sent.iloc[:, -1].value_counts())
print("\nVai dong dau:")
print(df_sent.head(3))