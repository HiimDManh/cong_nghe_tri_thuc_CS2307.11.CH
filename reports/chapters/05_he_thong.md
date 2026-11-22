## 5. Hệ thống demo và LLM diễn giải

<!-- NGƯỜI VIẾT: Phúc. Viết văn bản + chụp màn hình demo (lưu reports/figures/demo_*.png, rồi chèn bằng
{{fig:demo_xxx.png|chú thích}}). KHÔNG tự gõ số kết quả – dùng {{table:llm}} và các số trong demo. -->

### 5.1. Kiến trúc
```
Người dùng (form tiếng Việt, VND)
   │  src/app/convert.py: VND → trạng thái BN (ngũ phân vị GSO 2024, DSTI, LTI – giả định quy đổi)
   ▼
BN-Expert-Mono (models/bn_expert_mono.json) ── suy luận xuôi: P(vỡ nợ) → điểm 300–850
   │                                         ├─ đóng góp từng yếu tố (so với mức phổ biến)
   │                                         ├─ suy luận ngược: phản thực do(), hậu nghiệm ngược
   │                                         └─ what-if biến cố (nút tri thức)
   ▼
src/llm/facts.py: dữ kiện JSON (mọi con số do BN tính)
   ▼
LLMClient (Gemini / Groq / Ollama / template; cache) → lời khuyên → faithfulness.py kiểm tra số & hướng
```
So sánh trong demo: FICO rule-based (đề tài cũ) và XGBoost (hộp đen, `models/xgb_disc.json`).

### 5.2. Các màn hình
<!-- Gợi ý: mỗi tab 1 ảnh + 2–3 câu: Kết quả; Đồ thị nhân quả; Suy luận ngược; What-if biến cố; Lời khuyên LLM;
Tri thức & CPT. Dùng các hồ sơ mẫu trong data/samples/profiles.csv. Nêu: nhập "Không rõ" vẫn ra điểm (BN lấy biên). -->

### 5.3. LLM diễn giải và kiểm tra độ trung thành
<!-- Gợi ý: nguyên tắc "LLM không tự tính xác suất"; prompt (src/llm/prompt.py); 3 tiêu chí kiểm tra tự động
(số khớp dữ kiện, bao phủ dữ kiện bắt buộc, không nói ngược hướng); đối chứng âm (lời khuyên cố ý sai) để chứng
minh bộ kiểm tra bắt được lỗi; kết quả chấm tay của nhóm (rubric 1–5). -->

{{table:llm}}

### 5.4. Triển khai
<!-- Gợi ý: Streamlit Community Cloud (hoặc HF Spaces); key LLM để trong Secrets, không trong repo; link demo. -->
