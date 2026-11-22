# Dự báo khả năng tài chính cá nhân theo ngành nghề (Bayesian Network)

Đồ án cuối kỳ môn **Chuyên đề nghiên cứu và ứng dụng về Công nghệ tri thức** – Project 6,
tiếp nối đề tài *Hệ thống tính điểm tín dụng cá nhân giả lập dựa trên luật FICO cơ bản*.

Chuỗi nhân quả cốt lõi: `Ngành → Thu nhập → Biến cố → Khả năng vỡ nợ`, biểu diễn bằng Mạng Bayes;
suy luận xuôi (dự báo điểm 300–850), suy luận ngược (điều kiện cần để đạt mục tiêu),
LLM diễn giải CPT thành lời khuyên; so sánh thực nghiệm với FICO rule-based và Black-box ML.

> Trạng thái: **Giai đoạn 1 – Khởi tạo**. Xem tiến độ trong [docs/TASKS.md](docs/TASKS.md).

## Cài đặt

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # điền key LLM nếu dùng (không commit .env)
```

## Dữ liệu

| Dataset | Vai trò | Cách lấy |
|---|---|---|
| German Credit (OpenML `credit-g`) | phụ / thí nghiệm dữ liệu nhỏ | tự động |
| Home Credit Default Risk – `application_train.csv` | chính (dự kiến) | Kaggle API: đặt `kaggle.json` vào `~/.kaggle/` và chấp nhận luật cuộc thi, hoặc tải tay vào `data/raw/` |

Dữ liệu thô nằm trong `data/raw/` và **không** được commit.

## Chạy

Không có `make` (Windows) thì dùng `python -m src.cli <bước>`:

```bash
make data    # = python -m src.cli data   – tải dữ liệu
make eda     # = python -m src.cli eda    – EDA nhanh -> reports/eda/
make train   # (giai đoạn 3)
make eval    # (giai đoạn 4)
make app     # (giai đoạn 5) Streamlit demo
make test    # = python -m pytest -q
```

## Cấu trúc

```
src/            code chính: data/ knowledge/ bn/ baselines/ evaluation/ llm/ app/
configs/        cấu hình YAML (seed, đường dẫn, ngưỡng, cấu trúc BN, thí nghiệm)
data/           raw/ interim/ (bị ignore), processed/
knowledge_base/ tri thức tài chính đã mã hóa, có cột nguồn (source_url, year)
experiments/    kết quả từng thí nghiệm (results.csv + hình)
reports/        báo cáo, EDA, hình
docs/           TASKS.md (đề bài PDF để ở đây nhưng bị ignore)
tests/          pytest
```

## Demo

_Link sẽ cập nhật sau khi deploy._
