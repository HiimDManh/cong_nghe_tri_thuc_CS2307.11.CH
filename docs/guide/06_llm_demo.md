# 6. LLM diễn giải và demo

## 6.1. Vai trò của LLM: chỉ diễn đạt, không tính toán
Đề bài yêu cầu LLM "diễn giải CPT/kết quả BN thành lời khuyên". Nguy cơ lớn nhất của LLM là **bịa số** (hallucination).
Vì vậy dự án tách hai việc:

1. **BN tính mọi con số** (`src/llm/facts.py` → `build_facts`). Dữ kiện gồm:
   - điểm, mức rủi ro, P(vỡ nợ), P(vỡ nợ) trung bình quần thể;
   - hồ sơ (nhãn tiếng Việt), danh sách biến chưa biết;
   - 3 yếu tố kéo điểm xuống và 3 yếu tố giúp tăng điểm (mục 4.7);
   - rủi ro của nhóm ngành và nhóm lịch sử tín dụng (từ CPT);
   - what-if: mất việc, sức khỏe, suy thoái → điểm mới;
   - kế hoạch phản thực tới mức điểm kế tiếp, hoặc "tối đa đạt được".
2. **LLM chỉ viết lời** (`src/llm/prompt.py`). Prompt hệ thống bắt buộc:
   - chỉ dùng số trong dữ kiện; không suy diễn nguyên nhân khác;
   - ≤ 220 từ, có 4 mục **Tóm tắt / Yếu tố chính / Nên làm gì / Lưu ý**;
   - "Nên làm gì" chỉ dựa trên kế hoạch có trong dữ kiện;
   - nêu rõ đây là mô hình minh họa.
3. **Kiểm tra tự động độ trung thành** (`src/llm/faithfulness.py`):
   - `number_precision`: tỷ lệ con số trong lời khuyên có trong dữ kiện. Có cho phép làm tròn và định dạng Việt Nam
     như "6,4%" hay "1.500.000".
   - `fact_coverage`: có nhắc điểm, mức rủi ro, và yếu tố kéo điểm xuống mạnh nhất không.
   - `direction_ok`: trong phần mô tả yếu tố, không có câu nói ngược hướng, ví dụ yếu tố kéo điểm xuống lại được
     gọi là "điểm mạnh". Đây là luật heuristic và có thể sót; đó là lý do cần thêm chấm tay.
   - `faithful` = đạt cả ba tiêu chí.
4. **Đối chứng âm** (`template_corrupted`): lấy lời khuyên đúng rồi cố ý đổi điểm và đảo hướng một yếu tố, để
   chứng minh bộ kiểm tra *bắt được lỗi*. Kết quả mong đợi: faithful = 0%.
5. **Chấm tay** theo rubric 1–5 (đúng dữ kiện, dễ hiểu, hữu ích): `docs/handoff/llm_rating_rubric.md`.

## 6.2. Nhà cung cấp LLM (`src/llm/client.py`, `configs/llm.yaml`)
| Provider | Mô hình mặc định | Cần | Ghi chú |
|---|---|---|---|
| Gemini | `gemini-2.5-flash` | `GEMINI_API_KEY` (free tier) | Key gửi qua header `x-goog-api-key`, không đặt trong URL |
| Groq | `openai/gpt-oss-120b` (`reasoning_effort: low`); so sánh thêm `qwen/qwen3.8-27b` | `GROQ_API_KEY` (free tier) | API kiểu OpenAI; `llama-3.3-70b-versatile` đã bị gỡ (11/2026); lỗi 429 tự chờ rồi gọi lại |
| Ollama | `qwen2.5:7b` | `OLLAMA_HOST` (chạy local) | Không cần Internet |
| template | – | không | Lời khuyên tất định từ dữ kiện; dùng làm dự phòng và làm mốc |

Các cơ chế đi kèm:
- **Cache:** lời khuyên lưu ở `.cache/llm/` theo mã băm của prompt. Thư mục này không commit.
- **Dự phòng:** lỗi mạng hoặc hết quota thì tự trả template kèm thông báo. Thông báo chỉ có loại lỗi, không lộ key.
- Chạy đánh giá: `python -m src.cli llm` → `experiments/llm_faithfulness/results.csv` và
  `samples_for_rating.csv` (file để chấm tay).

**Bảo mật key.**
- Key chỉ nằm ở `.env` (local) hoặc Secrets của Streamlit Cloud.
- `.env` đã nằm trong `.gitignore`.
- Không dán key vào chat nhóm, repo, slide hay ảnh chụp màn hình.
- Lộ key thì thu hồi ngay trên trang của nhà cung cấp.

## 6.3. Demo Streamlit (`src/app/streamlit_app.py`)
**Đầu vào.** Form 3 cột, mọi trường đều có lựa chọn "Không rõ":

| Nhóm | Trường |
|---|---|
| Nghề nghiệp | ngành, nghề, học vấn, tình trạng làm việc, thâm niên, tuổi |
| Thu nhập & gia đình | thu nhập hộ, số người trong hộ, thu nhập cá nhân, số con, nhà, xe |
| Khoản vay & tín dụng | trả góp/tháng, dư nợ, lịch sử trả nợ tự đánh giá, số lần hỏi vay, khu vực |

**Quy đổi** (`src/app/convert.py`; các mục đánh dấu *giả định* được ghi rõ trên demo):
- Thu nhập bình quân đầu người = thu nhập hộ / số người. Đổi sang nhóm 1–5 theo ranh giới là **trung điểm** giữa
  trung bình hai nhóm kề nhau của GSO 2024 (*giả định*, vì GSO chỉ công bố trung bình mỗi nhóm).
- DSTI = trả góp / thu nhập cá nhân; LTI = dư nợ / (12 × thu nhập cá nhân).
- Lịch sử trả nợ tự đánh giá ↔ ngũ phân vị điểm tín dụng ngoài (*giả định*).
- Khu vực 1/2/3 ↔ xếp hạng vùng của Home Credit (*giả định*).
- "Không đi làm" → ngành và thâm niên = `not_working`.

**6 tab.**
1. **Kết quả:** điểm, mức rủi ro, P(vỡ nợ); so sánh với FICO (luật cũ) và XGBoost (hộp đen); biểu đồ đóng góp
   từng yếu tố.
2. **Đồ thị nhân quả:** DAG 20 nút, tô màu theo lớp; nút có bằng chứng viền đậm; hiển thị xác suất hậu nghiệm.
3. **Suy luận ngược:** thanh trượt điểm mục tiêu → bảng kế hoạch rẻ nhất; bảng "điều kiện cần" cho ba mục tiêu (không
   vỡ nợ, có nhà, có nhà và xe).
4. **What-if biến cố:** mất việc (bị khóa nếu không đi làm), sức khỏe, lạm phát, suy thoái, chi phí sinh hoạt.
5. **Lời khuyên (LLM):** lời khuyên, nhãn ✅/⚠️ của bộ kiểm tra, dữ kiện JSON đã gửi cho LLM.
6. **Tri thức & CPT:** nguồn CPT của từng nút, bảng CPT, lý do từng cạnh, bảng khác biệt với FICO.

**Mô hình demo** nằm ở `models/` (đã commit; **không cần dữ liệu Home Credit** khi chạy demo):
- `bn_expert_mono.json`, `bn_expert.json`, `discretizer.json`;
- `xgb_disc.json`: XGBoost lưu dạng JSON gốc, không dùng pickle;
- sinh lại bằng `python -m src.cli train`.

**Hồ sơ mẫu:** `data/samples/profiles.csv`, nạp từ sidebar. Phúc mở rộng lên ~50 hồ sơ theo
`docs/handoff/phuc_profiles_spec.md`.

**Triển khai:** `docs/DEPLOY.md`. Streamlit Community Cloud, file chính `src/app/streamlit_app.py`, thư viện gọn ở
`src/app/requirements.txt`, key đặt trong Secrets.
