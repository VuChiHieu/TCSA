# TCSA — Hệ thống Trợ lý Lọc nội dung độc hại và Phân tích cảm xúc thời gian thực

Dự án môn Trí tuệ Nhân tạo. Hệ thống sử dụng Machine Learning (Naive Bayes, MLP) để phát hiện nội dung độc hại và phân tích cảm xúc văn bản tiếng Việt theo thời gian thực, kèm theo bộ giao diện mô phỏng kiểm duyệt (Post, Comment, Live Chat) và Dashboard thống kê.

---

## 1. Cấu trúc dự án

```
TCSA/
  ai_core/
    data/
      vihsd/              -> dữ liệu huấn luyện toxic detection
      sentiment/           -> dữ liệu huấn luyện sentiment analysis
    models/                -> thư mục chứa file mô hình .pkl (tự tạo sau khi train)
    train_models_v2.py     -> script huấn luyện mô hình (bản mới nhất, dùng bản này)
    train_models.py        -> script huấn luyện bản đầu (tham khảo)
    check_data.py          -> script kiểm tra dữ liệu
  backend/
    main.py                -> FastAPI server, expose API cho mô hình AI
  frontend/
    src/
      pages/               -> 4 trang chính (Post, Comment, LiveChat, Dashboard)
      services/api.js      -> gọi API tới backend
      App.jsx
  requirements.txt
  .gitignore
  README.md
```

---

## 2. Yêu cầu hệ thống

- Python 3.13 (khuyến nghị dùng đúng bản này để tránh lỗi tương thích thư viện)
- Node.js bản LTS (khuyến nghị 18 trở lên)
- Git
- Hệ điều hành: Windows, macOS hoặc Linux đều chạy được (hướng dẫn dưới đây dùng lệnh Windows, các lệnh tương đương trên macOS/Linux có ghi chú riêng)

---

## 3. Clone dự án

```
git clone https://github.com/VuChiHieu/TCSA.git
cd TCSA
```

---

## 4. Cài đặt Backend (Python + AI Core)

### Bước 4.1 — Tạo môi trường ảo

Tại thư mục gốc `TCSA/`:

```
python -m venv venv
```

Kích hoạt môi trường ảo:

Windows (PowerShell):
```
venv\Scripts\Activate.ps1
```

macOS / Linux:
```
source venv/bin/activate
```

Sau khi kích hoạt, dòng lệnh sẽ có chữ `(venv)` ở đầu.

### Bước 4.2 — Cài thư viện

```
pip install -r requirements.txt
```

### Bước 4.3 — Huấn luyện mô hình AI (BẮT BUỘC, chỉ cần làm 1 lần)

Các file mô hình (`.pkl`) **không được đẩy lên Git** vì vượt quá giới hạn dung lượng của GitHub (file `mlp_*.pkl` nặng hơn 100MB). Vì vậy sau khi clone, thư mục `ai_core/models/` sẽ rỗng, và bạn **phải tự huấn luyện lại** trước khi chạy backend, nếu không backend sẽ báo lỗi không tìm thấy file `.pkl`.

Trước khi chạy script, tạo thư mục models nếu chưa có:

Windows:
```
mkdir ai_core\models
```

macOS / Linux:
```
mkdir -p ai_core/models
```

Dữ liệu thô dùng để huấn luyện đã có sẵn trong repo, không cần tải thêm:
- `ai_core/data/vihsd/vihsd-main/data/vihsd/` (train.csv, dev.csv, test.csv) — dữ liệu toxic, nguồn UIT-ViHSD: https://github.com/sonlam1102/vihsd
- `ai_core/data/sentiment/data - data.csv` — dữ liệu sentiment, gốc từ Kaggle: https://www.kaggle.com/datasets/linhlpv/vietnamese-sentiment-analyst

Chạy lệnh sau (đang ở thư mục gốc `TCSA/`, đã kích hoạt venv):

```
python ai_core/train_models_v2.py
```

Quá trình này mất khoảng 10-15 phút (MLP cần nhiều vòng lặp để huấn luyện). Khi chạy xong, script sẽ tự tạo 4 file vào đúng thư mục `ai_core/models/`:

```
ai_core/models/
  nb_toxic.pkl
  mlp_toxic.pkl
  nb_sentiment.pkl
  mlp_sentiment.pkl
```

Chỉ cần chạy bước này **một lần duy nhất** sau khi clone. Những lần chạy backend sau đó không cần huấn luyện lại, vì backend sẽ tự load 4 file đã có sẵn trong thư mục.

Nếu file dữ liệu `.csv` bị thiếu vì lý do nào đó, tải lại theo 2 link nguồn trên và đặt đúng đường dẫn như cấu trúc ở trên.

### Bước 4.4 — Chạy Backend server

```
cd backend
uvicorn main:app --reload --port 8000
```

Server chạy thành công khi thấy dòng:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Kiểm tra API hoạt động bằng cách mở trình duyệt vào:

```
http://127.0.0.1:8000/docs
```

Đây là giao diện Swagger, cho phép test toàn bộ API trực tiếp trên trình duyệt mà không cần Postman.

**Lưu ý:** giữ terminal này luôn chạy trong suốt quá trình sử dụng frontend. Mở terminal mới cho các bước tiếp theo.

---

## 5. Cài đặt Frontend (ReactJS)

Mở terminal mới (không tắt terminal backend), tại thư mục gốc `TCSA/`:

```
cd frontend
npm install
npm run dev
```

Sau khi chạy, mở trình duyệt vào:

```
http://localhost:5173
```

Giao diện gồm 4 tab: Kiểm duyệt bài đăng, Kiểm duyệt bình luận, Trò chuyện trực tiếp, Bảng điều khiển.

---

## 6. Tóm tắt thứ tự chạy mỗi lần mở máy

**Lưu ý:** lần đầu tiên sau khi clone, phải tạo thư mục `ai_core/models/` và chạy `python ai_core/train_models_v2.py` trước (xem Bước 4.3), nếu không backend sẽ lỗi vì chưa có file model.

```
# Terminal 1 — Backend
cd TCSA
venv\Scripts\Activate.ps1
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd TCSA\frontend
npm run dev
```

Sau đó vào `http://localhost:5173` để sử dụng.

---

## 7. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend API | Python, FastAPI, Uvicorn |
| AI / Machine Learning | Scikit-learn (Naive Bayes, MLP Classifier) |
| Xử lý ngôn ngữ tiếng Việt | Underthesea (tách từ), Regex (tiền xử lý) |
| Frontend | ReactJS (Vite) |
| Trực quan hóa dữ liệu | Recharts |
| Giao tiếp API | Axios |

---

## 8. Kết quả mô hình (tham khảo)

| Mô hình | Tác vụ | Accuracy | F1-Score (macro) |
|---|---|---|---|
| Naive Bayes | Toxic Detection | ~84.6% | ~0.59 |
| MLP | Toxic Detection | ~84.0% | ~0.58 |
| Naive Bayes | Sentiment Analysis | ~91.6% | ~0.92 |
| MLP | Sentiment Analysis | ~96.0% | ~0.96 |

Chi tiết classification report (precision, recall, F1-score từng nhãn) xem trong output của `train_models_v2.py` hoặc trong báo cáo dự án.

**Hạn chế đã ghi nhận:**
- Mô hình dựa trên TF-IDF, không xử lý tốt các câu phủ định ("không tệ") hoặc mỉa mai (sarcasm) do thiếu khả năng hiểu ngữ cảnh sâu.
- Mô hình phân loại ở cấp độ câu (sentence-level), không định vị được từng từ vi phạm cụ thể (token-level), nên tính năng Live Chat Word Masking dùng từ điển hỗ trợ để xác định vị trí che.
- Hướng cải thiện trong tương lai: sử dụng PhoBERT hoặc mô hình transformer tiếng Việt.

---

## 9. Xử lý lỗi thường gặp

**Lỗi `ModuleNotFoundError: No module named 'fastapi'`**
→ Chưa kích hoạt môi trường ảo trong terminal hiện tại. Chạy `venv\Scripts\Activate.ps1` trước.

**Lỗi `Could not import module "main"`**
→ Đang chạy uvicorn ở sai thư mục. Phải `cd backend` trước khi chạy `uvicorn main:app`.

**Lỗi `FileNotFoundError: nb_toxic.pkl`**
→ Chưa chạy bước huấn luyện mô hình. Chạy `python ai_core/train_models_v2.py` trước.

**Lỗi kết nối API trên frontend**
→ Backend chưa chạy hoặc đã tắt. Kiểm tra lại terminal backend còn dòng `Uvicorn running` không.

**API trả về lỗi 422 Unprocessable Entity**
→ Dữ liệu gửi lên không hợp lệ: văn bản rỗng, vượt quá 5000 ký tự, hoặc tham số `model` không phải `"nb"` hoặc `"mlp"`. Kiểm tra lại nội dung request.

**Cảnh báo `ConvergenceWarning` khi huấn luyện MLP**
→ Không phải lỗi nghiêm trọng, chỉ là mô hình cần thêm vòng lặp để hội tụ tối ưu hơn. Không ảnh hưởng đến việc sử dụng mô hình đã lưu.

---

## 10. Nhóm thực hiện

Dự án môn Trí tuệ Nhân tạo — TCSA Team.