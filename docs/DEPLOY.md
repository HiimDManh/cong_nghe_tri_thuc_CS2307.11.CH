# Triển khai demo (Streamlit Community Cloud – miễn phí)

Demo chỉ cần các file đã commit: `models/*.json` (BN, discretizer, XGBoost dạng JSON), `configs/`, `knowledge_base/`,
`data/samples/profiles.csv`. **Không cần** dữ liệu Home Credit trên server.

1. Repo GitHub (public, hoặc private nếu đã kết nối tài khoản) – Mạnh push nhánh `main`.
2. https://share.streamlit.io → *Create app* → chọn repo, branch `main`, **Main file path** `src/app/streamlit_app.py`,
   *Advanced settings* → Python **3.12**.
3. Thư viện: Community Cloud ưu tiên `requirements.txt` cạnh file chính → dùng `src/app/requirements.txt` (gọn, không
   có LightGBM/Optuna/SHAP/pgmpy).
4. *Advanced settings* → **Secrets** (KHÔNG commit, KHÔNG gửi vào chat nhóm):
   ```toml
   GEMINI_API_KEY = "…"
   GROQ_API_KEY = "…"
   LLM_PROVIDER = "gemini"
   ```
   App đọc qua `st.secrets` (`src/llm/client.py`). Không có key → tự dùng lời khuyên template.
5. Deploy → kiểm tra theo `docs/handoff/khoi_qa_checklist.md`; dán link vào README và Chương 5 báo cáo.

Phương án dự phòng: Hugging Face Spaces (SDK Streamlit) – cùng `requirements`, key đặt ở *Settings › Variables and secrets*.

Chạy local: `.venv/Scripts/python -m src.cli app` (key đặt trong `.env`, xem `.env.example`).
