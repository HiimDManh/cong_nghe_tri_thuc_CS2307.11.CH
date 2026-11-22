# CLAUDE.md

Đồ án cuối kỳ môn Công nghệ tri thức (UIT, cao học) – **Project 6: Dự báo khả năng tài chính cá nhân theo ngành nghề**, tiếp nối đề tài cũ "tính điểm tín dụng giả lập theo luật FICO" (không còn code cũ).
Nhóm: Mạnh, Nam, Khôi, Phúc. **Hạn nộp + báo cáo: 02/12/2026.**
**Phân công:** người dùng Claude Code là **Mạnh** – chủ trì & làm *toàn bộ* code/dữ liệu/mô hình/thí nghiệm/số liệu. Nam, Khôi, Phúc dùng AI khác → chỉ làm việc không sinh code/số liệu (đối chiếu nguồn, QA demo, chấm LLM, viết văn/slide từ artefact). Không giao cho họ việc sửa `src/`, `configs/`, `knowledge_base/*.csv`.

## Đọc trước khi làm
1. **`Progress.md`** – trạng thái hiện tại, quyết định đã chốt, việc tiếp theo. Đọc file này thay vì quét lại repo.
2. `docs/TASKS.md` – checklist chi tiết theo người/giai đoạn/tiêu chí hoàn thành.
3. Đề bài gốc: `docs/De tai mon Cong nghe tri thuc 2026.pdf` (trang 5–6, Project 6). Chỉ đọc khi cần.

## Quy tắc tự cập nhật tài liệu (Claude tự làm, không chờ nhắc)
- **`Progress.md`** – cập nhật *trước mỗi commit* và *trước khi kết thúc lượt trả lời* nếu có thay đổi đáng kể: mục "Hiện tại", "Quyết định đã chốt" (kèm lý do), "Kết quả đã có" (số liệu chính + đường dẫn file), "Vấn đề tồn đọng", "Tiếp theo", và thêm 1 dòng "Nhật ký" (ngày, việc, commit). Giữ ngắn (< ~120 dòng); thông tin cũ đã hết giá trị thì gộp/xoá.
- **`CLAUDE.md`** – chỉ sửa khi thay đổi thứ *bền vững*: lệnh chạy, cấu trúc thư mục, quy tắc, phân công, hạn, môi trường. Không ghi tiến độ vào đây.
- **`docs/TASKS.md`** – tick `[x]`/`[~]` ngay khi xong/bắt đầu một việc.
- Commit các file này cùng commit với thay đổi code liên quan.

## Yêu cầu cốt lõi của đề
- BN mô hình hóa `Ngành → Thu nhập → Biến cố → Khả năng vỡ nợ`; suy luận xuôi → điểm 300–850.
- **Suy luận ngược** (MAP + counterfactual trên biến điều khiển được) → điều kiện cần về thu nhập/chi tiêu.
- **LLM diễn giải** CPT/kết quả BN thành lời khuyên tiếng Việt (LLM không tự tính xác suất).
- Demo Streamlit + đồ thị nhân quả; **báo cáo thực nghiệm BN vs Black-box ML (quan trọng nhất)**: phân biệt, hiệu chỉnh, kiểm định thống kê, thiếu thông tin, dữ liệu ít, dịch chuyển theo ngành, nhất quán tri thức, ổn định giải thích, chi phí.
- Nêu rõ khác biệt so với đề tài FICO rule-based cũ.

## Lệnh
- Môi trường: `.venv` (Python 3.12). Gọi `.venv/Scripts/python` (Windows, không có `make`).
- `python -m src.cli data|eda|knowledge|dag|train|eval|app` · `python -m pytest -q` · Makefile chỉ bọc các lệnh này.
- Dữ liệu chính: Home Credit (`src/data/home_credit.py` → đặc trưng; `src/data/discretize.py` → trạng thái BN, fit ngưỡng quantile chỉ trên train). Tải `application_train.csv` mất ~10 s.
- Mạng Bayes: `src/bn/core.py` (`DiscreteBN`: CPT m-estimate, suy luận chính xác theo lô = gather + einsum trên biến ẩn, khớp pgmpy), `model.py` (BN-Expert 2 lớp + Mono, điểm 300–850), `expert_cpt.py` (CPT nút tri thức sinh từ `knowledge_base/`), `backward.py` (posterior ngược, MAP, counterfactual do()), `variants.py` (NB, TAN, HC, Hybrid). Mô hình cho demo: `models/*.json` (commit được).
- Console Windows là cp1252: script in tiếng Việt phải gọi `src.common.utf8_stdout()`.

## Cấu trúc
`src/{data,knowledge,bn,baselines,evaluation,llm,app}` (code) · `configs/*.yaml` (mọi tham số, seed=42) · `data/raw|interim` (ignored) · `knowledge_base/` (tri thức có `source_url`,`year`) · `experiments/<tên>/results.csv` · `reports/` · `tests/`.
Thư mục làm việc trên máy tên là `src`, nên code nằm ở `src/src/` – đó là gốc repo, không phải lỗi.

## Quy tắc bắt buộc
- Free tier only; CPU, RAM ≤ 12 GB, mỗi thí nghiệm ≤ ~30 phút (nặng → subsample, ghi rõ).
- **Không bịa số liệu / nguồn.** Mọi số trong báo cáo sinh từ script trong repo. Giả định ghi rõ "giả định".
- Báo cáo trung thực: không chỉnh thí nghiệm để BN "thắng".
- Không commit: PDF/PPT, `data/raw`, `.env`, `kaggle.json`, `access_token`, model `.pkl/.joblib`.
- Conventional commits; commit kết thúc bằng dòng Co-Authored-By được hệ thống yêu cầu.
- Code: type hints, docstring ngắn, cấu hình trong YAML; notebook chỉ để khám phá.
- Hỏi trước khi: tải dữ liệu lớn, chạy tuning dài (ước lượng thời gian trước).
- Điểm dừng xin nhóm duyệt: DAG BN-Expert (trước khi học tham số); bảng kết quả sơ bộ (trước khi viết báo cáo).
- Trả lời người dùng bằng tiếng Việt.
