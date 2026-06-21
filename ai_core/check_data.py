import pandas as pd

# Kiem tra du lieu toxic
print("=== DU LIEU TOXIC (ViHSD) ===")
df_train = pd.read_csv(r"D:\TriTueNhanTao\Hieuha\TCSA\ai_core\data\vihsd\vihsd-main\data\vihsd\train.csv")
print("Columns:", df_train.columns.tolist())
print("Shape:", df_train.shape)
print("Nhan phan loai:")
print(df_train.iloc[:, -1].value_counts())
print("\nVai dong dau:")
print(df_train.head(3))

print("\n=== DU LIEU SENTIMENT ===")
df_sent = pd.read_csv(r"D:\TriTueNhanTao\Hieuha\TCSA\ai_core\data\sentiment\data - data.csv")
print("Columns:", df_sent.columns.tolist())
print("Shape:", df_sent.shape)
print("Nhan phan loai:")
print(df_sent.iloc[:, -1].value_counts())
print("\nVai dong dau:")
print(df_sent.head(3))