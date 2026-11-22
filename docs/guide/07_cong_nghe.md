# 7. Công nghệ, tái lập, kiểm thử

## 7.1. Công nghệ và vai trò
| Công nghệ | Phiên bản | Dùng để | Ở đâu |
|---|---|---|---|
| Python | 3.12 | Ngôn ngữ chính | `.venv/` |
| NumPy | 2.5.5 | Mảng, `einsum` cho suy luận BN theo lô | `src/bn/core.py` |
| pandas | 3.1.1 | Bảng dữ liệu | khắp nơi |
| pgmpy | 1.1.2 | Đối chiếu suy luận (test), MAP, học cấu trúc TAN / Hill-Climb | `src/bn/variants.py`, `backward.py`, `tests/` |
| networkx | 3.7 | Đồ thị DAG, kiểm tra chu trình, tổ tiên | `src/bn/core.py`, `structure.py` |
| scikit-learn | 1.9.1 | LR, RF, MLP, tiền xử lý, isotonic regression, chỉ số | `src/baselines/`, `src/bn/model.py` |
| XGBoost | 3.4.1 | Gradient boosting (kể cả ràng buộc đơn điệu); TreeSHAP qua `pred_contribs` | `src/baselines/ml.py` |
| LightGBM | 4.7.0 | Gradient boosting | `src/baselines/ml.py` |
| Optuna | 5.1.0 | Tinh chỉnh XGBoost (TPE) | `src/baselines/ml.py` |
| SciPy | 1.18.1 | Kiểm định (t, chuẩn), xếp hạng | `src/evaluation/metrics.py` |
| matplotlib | 3.11.2 | Hình báo cáo | `src/evaluation/figures.py` |
| Streamlit | 1.67.0 | Demo web; Altair (biểu đồ), Graphviz DOT (đồ thị nhân quả, vẽ phía trình duyệt) | `src/app/` |
| requests | 2.34.2 | Gọi REST API của Gemini, Groq, Ollama | `src/llm/client.py` |
| python-dotenv | 1.2.4 | Đọc key từ `.env` | `src/llm/client.py` |
| wbgapi | 1.0.14 | API World Bank | `src/knowledge/fetch_macro.py` |
| openpyxl | 3.1.5 | Đọc xlsx của GSO | `src/knowledge/fetch_gso.py` |
| kaggle | 2.2.5 | Tải Home Credit | `src/data/download.py` |
| PyYAML | 6.0.4 | Đọc `configs/*.yaml` | `src/common.py` |
| pytest | 9.2.0 | Kiểm thử | `tests/` |
| Git / GitHub | – | Quản lý phiên bản, conventional commits | – |

Ràng buộc tài nguyên của dự án:
- Chỉ dùng free tier, CPU, RAM ≤ 12 GB, mỗi thí nghiệm ≤ ~30 phút.
- Toàn bộ thực nghiệm chạy khoảng 1 giờ trên CPU 16 luồng.

## 7.2. Tái lập
- **Seed:** `configs/data.yaml` (42); seed CV là 42, 43, 44 (`configs/eval.yaml`).
- **Split CV:** lưu ở `experiments/splits/home_credit_folds.npz`, có kiểm tra khớp `SK_ID_CURR`.
- **Tham số:** mọi tham số nằm trong `configs/*.yaml`, không hard-code.
- **Thư viện:** phiên bản ghim trong `requirements.txt`.
- **Chạy lại từ đầu:** `data` → `knowledge` → `train` → `tune` → `eval` → `llm` → `report`.

## 7.3. Kiểm thử (`tests/`, `python -m pytest -q`)
| File | Kiểm tra |
|---|---|
| `test_data.py`, `test_g2.py` | Đặc trưng, ánh xạ ngành/nghề, rời rạc hóa, tri thức tải về, FICO |
| `test_bn.py` | Suy luận theo lô khớp pgmpy (đủ và thiếu bằng chứng, truy vấn ngược chiều); BDeu khớp pgmpy; m-estimate; JSON; CPT hợp lệ; ràng buộc đơn điệu thỏa chính xác; biến cố làm rủi ro tăng; bằng chứng bất khả → NaN; λ = 0 trả lại CPT dữ liệu; quy đổi điểm; graph surgery; kế hoạch phản thực đúng hướng/bậc/chi phí; hậu nghiệm ngược là phân phối; các biến thể học được |
| `test_eval.py` | DeLong khớp sklearn và đúng khi H0; ECE; Holm; bootstrap đúng chiều; split phân tầng; gộp nhóm biến và che giấu (không đi làm ≠ thiếu); quy đổi VND; kiểm tra trung thành bắt được số bịa và sai hướng; placeholder báo cáo không tự điền số |

## 7.4. Quy ước
- Code có type hints và docstring ngắn tiếng Việt. Notebook chỉ dùng để khám phá.
- Console Windows dùng mã cp1252, nên script in tiếng Việt phải gọi `src.common.utf8_stdout()`.
- Commit theo **Conventional Commits** (`feat(bn): …`, `fix: …`, `docs: …`).
- **Không commit:**
  - PDF, PPT;
  - `data/raw`, `data/interim`;
  - `.env`, `kaggle.json`, `access_token`;
  - mô hình `.pkl`, `.joblib`;
  - `.cache/`.
- Điểm dừng xin nhóm duyệt:
  - DAG, đã duyệt 22/11;
  - bảng kết quả sơ bộ, tối 29/11.
