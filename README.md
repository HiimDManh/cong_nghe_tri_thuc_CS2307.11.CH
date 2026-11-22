# Dự báo khả năng tài chính cá nhân theo ngành nghề (Bayesian Network)

Đồ án cuối kỳ môn **Chuyên đề nghiên cứu và ứng dụng về Công nghệ tri thức** – Project 6,
tiếp nối đề tài *Hệ thống tính điểm tín dụng cá nhân giả lập dựa trên luật FICO cơ bản*.

Chuỗi nhân quả cốt lõi: `Ngành → Thu nhập → Biến cố → Khả năng vỡ nợ`, biểu diễn bằng Mạng Bayes;
suy luận xuôi (dự báo điểm 300–850), suy luận ngược (điều kiện cần để đạt mục tiêu),
LLM diễn giải CPT thành lời khuyên; so sánh thực nghiệm với FICO rule-based và Black-box ML.

> Trạng thái: xem [Progress.md](Progress.md). Bàn giao cho nhóm: [docs/HANDOFF.md](docs/HANDOFF.md). Kết quả thực nghiệm: [reports/results_summary.md](reports/results_summary.md).

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
| Home Credit Default Risk – `application_train.csv` | **chính** (đã chốt 22/11) | xem bên dưới |

**Home Credit** (bắt buộc bấm *I understand and accept* luật cuộc thi trên
[trang dữ liệu](https://www.kaggle.com/competitions/home-credit-default-risk/data) trước):
- *Cách 1 – tải tay, không cần token:* tải `application_train.csv`, giải nén vào `data/raw/`.
- *Cách 2 – API:* Kaggle › Settings › API › **Generate New Token**, lưu chuỗi token vào
  `~/.kaggle/access_token` (hoặc biến môi trường `KAGGLE_API_TOKEN`), rồi `python -m src.cli data`.
  Token chỉ cấp quyền vào tài khoản Kaggle, không bao giờ được commit; có thể thu hồi trong Settings.

Dữ liệu thô nằm trong `data/raw/` và **không** được commit.

## Nhóm

Mạnh · Nam · Khôi · Phúc — hạn nộp & báo cáo **02/12/2026**. Phân công: [docs/TASKS.md](docs/TASKS.md).

## Chạy

Không có `make` (Windows) thì dùng `python -m src.cli <bước>`:

```bash
make data    # = python -m src.cli data   – tải dữ liệu
make eda     # = python -m src.cli eda    – EDA German Credit + Home Credit -> reports/eda/
make knowledge # = python -m src.cli knowledge – tri thức vĩ mô (World Bank, WHO) -> knowledge_base/
make dag     # = python -m src.cli dag    – kiểm tra + vẽ DAG BN-Expert
make train   # = python -m src.cli train  – học BN-Expert(+Mono), XGBoost demo -> models/*.json
python -m src.cli tune           # Optuna XGBoost (25 trial, ~3 phút) -> experiments/tuning/
make eval    # = python -m src.cli eval   – toàn bộ thực nghiệm (~1 giờ CPU) -> experiments/, reports/results/
python -m src.cli eval missing   # chỉ một thí nghiệm (main_cv phải chạy trước)
python -m src.cli llm            # độ trung thành lời khuyên LLM -> experiments/llm_faithfulness/
python -m src.cli report         # ghép reports/chapters/*.md + bảng số liệu -> reports/report.md
make app     # = python -m src.cli app    – Streamlit demo
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

Chạy local: `python -m src.cli app` (chỉ cần `models/*.json` đã commit, không cần dữ liệu Home Credit;
cài tối thiểu: `pip install -r src/app/requirements.txt`). Triển khai: [docs/DEPLOY.md](docs/DEPLOY.md).
_Link deploy: (cập nhật sau)._
