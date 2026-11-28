# Bản thảo chi tiết Slide của Phúc (Slide 1–3, 16–18) & Khung ghép 18 Slide

> **Nguyên tắc bắt buộc (`docs/HANDOFF.md` & `slides_outline.md`):**
> - Mọi con số dưới đây đều trích nguyên văn từ `reports/results_summary.md`, `reports/results/key_numbers.json` và các chương `01`, `04`, `05`, `06` — **không tự sửa số hoặc làm tròn khác đi**.
> - File slide xuất ra (`.pptx` / `.pdf`) **gửi riêng cho nhóm/Mạnh, KHÔNG commit vào Git repo**.
> - Thời lượng toàn nhóm: **15 phút / 18 slide** (~45–50 giây/slide). Phúc dựng **Slide 1–3, 16–18**, ghép toàn bộ 18 slide và trực tiếp thuyết trình **Slide 16–17**.

---

## Phần 1: Nội dung chi tiết 6 Slide do Phúc dựng

### SLIDE 1 — Trang bìa *(Người trình bày: Mạnh)*
* **Tiêu đề lớn:** DỰ BÁO KHẢ NĂNG TÀI CHÍNH CÁ NHÂN THEO NGÀNH NGHỀ BẰNG MẠNG BAYES
* **Tiêu đề phụ:** Suy luận xuôi – Suy luận ngược phản thực `do()` – Diễn giải bằng LLM – Đối chứng thực nghiệm với Black-box ML
* **Thông tin môn học:** Đồ án cuối kỳ – Chuyên đề nghiên cứu và ứng dụng về Công nghệ tri thức (Project 6)
* **Nhóm thực hiện:** Mạnh · Nam · Khôi · Phúc
* **Ngày báo cáo:** 02/12/2026

---

### SLIDE 2 — Bài toán & Chuỗi nhân quả *(Người trình bày: Mạnh · Nguồn: `01_gioi_thieu.md` §1.1–1.2)*
* **Đặt vấn đề:**
  * Rủi ro vỡ nợ cá nhân không chỉ phụ thuộc các chỉ số tài chính tĩnh tại thời điểm vay, mà còn chịu chi phối bởi **bối cảnh ngành nghề** (quyết định mức và độ ổn định thu nhập) cùng **các biến cố bất định** (mất việc, chi phí y tế thảm họa, lạm phát, suy thoái).
* **Sơ đồ chuỗi nhân quả trung tâm (vẽ khối ngang lớn giữa slide):**
  $$\text{Ngành nghề} \longrightarrow \text{Thu nhập \& Ổn định việc làm} \longrightarrow \text{Biến cố (Hụt dòng tiền)} \longrightarrow \text{Khả năng vỡ nợ}$$
* **4 bài toán giải quyết trong đồ án:**
  1. **Suy luận xuôi:** Tính chính xác $P(\text{vỡ nợ} \mid \text{bằng chứng})$ $\rightarrow$ quy đổi điểm tín dụng **300–850**.
  2. **Suy luận ngược:** Hậu nghiệm ngược, MAP và can thiệp phản thực `do()` trên **7 đòn bẩy** người dùng điều khiển được.
  3. **LLM diễn giải:** Chuyển kết quả Mạng Bayes thành lời khuyên tiếng Việt, có **kiểm tra độ trung thành tự động**.
  4. **Kiểm chứng thực nghiệm (9 tiêu chí):** So sánh công bằng với 8 mô hình ML hộp đen và 4 biến thể Bayes trên **Home Credit (307.511 hồ sơ, tỷ lệ vỡ nợ 8,07%)**, **German Credit (1.000 hồ sơ)** và tri thức vĩ mô Việt Nam (World Bank, WHO, GSO KSMS 2024).

---

### SLIDE 3 — Khác biệt so với đề tài FICO Rule-based cũ *(Người trình bày: Mạnh · Nguồn: `01_gioi_thieu.md` §1.3)*
* **Bối cảnh kế thừa:** Tái hiện hệ luật FICO cơ bản (5 nhóm trọng số cố định) làm baseline đối sánh trực tiếp trên cùng tập dữ liệu.
* **Bảng so sánh trực diện:**

| Khía cạnh | FICO rule-based (đề tài cũ) | Mạng Bayes `BN-Expert-Mono` (đề tài này) |
|---|---|---|
| **Biểu diễn tri thức** | Luật cộng điểm cố định (35/30/15/10/10) | DAG nhân quả **20 nút, 35 cạnh** có lý do; CPT học từ dữ liệu + tri thức vĩ mô |
| **Đầu ra** | Điểm số tất định | Xác suất vỡ nợ hậu nghiệm (có hiệu chỉnh) $\rightarrow$ điểm **300–850** |
| **Ngành nghề & Biến cố** | Không mô hình hóa | Ngành $\rightarrow$ Nghề $\rightarrow$ Thu nhập, Ổn định; 6 nút tri thức biến cố what-if |
| **Thiếu thông tin** | Gán điểm trung tính cố định | **Lấy biên chính xác** theo phân phối xác suất (không cần điền khuyết) |
| **Suy luận ngược** | Không hỗ trợ | Hậu nghiệm ngược + MAP + **phản thực `do()` có chi phí** |
| **Học dữ liệu & Ràng buộc** | Không học (chỉ hiệu chỉnh Platt khi đo) | Ước lượng `m-estimate` ($m=10$) + chiếu đơn điệu chuyên gia (POCS) |
| **Độ phân biệt (ROC-AUC)** | **0,692** (ECE: **0,0069**) | **0,715** (**+0,022 AUC**, thắng 15/15 fold; ECE: **0,0047**) |

---

### SLIDE 16 — Hệ thống Demo tương tác (Streamlit – 6 màn hình) *(Người trình bày: PHÚC · Nguồn: `05_he_thong.md` + `figures/demo_*.png`)*
* **Bố cục gợi ý:** Cột trái (35%) tóm tắt kiến trúc & hồ sơ minh họa; Cột phải (65%) chèn lưới 2×3 từ **6 file ảnh đã chụp sẵn** trong `reports/figures/` (hoặc mở `http://localhost:8501` demo trực tiếp):
  * `reports/figures/demo_01_ket_qua.png` · `reports/figures/demo_02_do_thi.png` · `reports/figures/demo_03_suy_luan_nguoc.png`
  * `reports/figures/demo_04_what_if.png` · `reports/figures/demo_05_llm.png` · `reports/figures/demo_06_tri_thuc.png`
* **Nội dung trên slide:**
  * **Đầu vào thực tế cho người dùng Việt Nam:**
    * Nhập liệu bằng **triệu VND**, nạp sẵn **54 hồ sơ mẫu** đa dạng (đủ 9 nhóm ngành, nhóm không đi làm, tuổi 20–70, trả góp nặng $\ge 40\%$ và khuyết thông tin).
    * Quy đổi tự động sang trạng thái BN qua ngũ phân vị **GSO KSMS 2024** (*giả định* trung điểm) & ngưỡng DSTI/LTI.
    * **Chịu khuyết tự nhiên:** Minh họa trên hồ sơ *Thu ngân siêu thị* để trống **3/13 trường ("Không rõ")** $\rightarrow$ `BN-Expert-Mono` vẫn tính chính xác **613 điểm – Trung bình ($P = 5{,}6\%$)** nhờ lấy biên xác suất (đối sánh trực tiếp FICO `580`, XGBoost `593 – 7,2%`).
  * **6 màn hình chức năng (đã chụp minh họa xuyên suốt 1 hồ sơ):**
    1. **Kết quả (`demo_01`):** Điểm 300–850, đối sánh FICO (AUC `0,692`) & XGBoost rời rạc (AUC `0,731`), biểu đồ đóng góp điểm từng yếu tố.
    2. **Đồ thị nhân quả (`demo_02`):** DAG 20 nút (xanh: dữ liệu, cam: tri thức), phân biệt viền đậm (đã biết) và viền mảnh kèm xác suất hậu nghiệm (biến ẩn).
    3. **Suy luận ngược (`demo_03`):** Duyệt **4.320 tổ hợp** can thiệp `do()` tìm phương án ít tốn kém nhất (mục tiêu `650` $\rightarrow$ đạt `673` điểm, chi phí `5`) & bảng *lift* điều kiện cần.
    4. **What-if biến cố (`demo_04`):** Bật *Mất việc + Lạm phát cao* $\rightarrow$ điểm sụt còn **540 (−73 điểm)**, $P(\text{hụt dòng tiền}) = 34{,}9\%$ (thực nghiệm toàn tập ở $\lambda=0{,}3$: mất việc **−72 điểm**, sức khỏe **−48 điểm**); tự khóa *mất việc* nếu *không đi làm*.
    5. **Lời khuyên LLM (`demo_05`):** Tư vấn 4 mục kèm nhãn `✅ Trung thành với dữ kiện (số khớp 100%, bao phủ 100%)` và JSON gốc.
    6. **Tri thức & CPT (`demo_06`):** Kiểm toán nguồn CPT (ví dụ *Biến cố sức khỏe* từ WHO SDG 3.8.2) và bảng lý do 35 cạnh nhân quả.
  * **Đóng gói gọn nhẹ:** Chỉ nạp `models/*.json` (~116 KB với BN), **không cần tập dữ liệu Home Credit** trên máy chủ.

> **🎤 Lời thoại gợi ý cho Phúc (~1 phút 15 giây, khớp đúng số trên 6 ảnh bạn vừa chụp):**
> *"Tiếp theo em xin trình bày hệ thống demo trên Streamlit. Người dùng nhập thông tin bằng tiếng Việt theo đơn vị triệu đồng hoặc chọn từ bộ 54 hồ sơ mẫu của nhóm; hệ thống quy đổi sang trạng thái Mạng Bayes qua ngũ phân vị GSO 2024 và các ngưỡng nợ chuẩn. Trên hình là hồ sơ mẫu 'Thu ngân siêu thị' cố ý để trống 3 trên 13 trường 'Không rõ': nhờ lấy biên xác suất chính xác, Mạng Bayes vẫn tính ra 613 điểm (rủi ro 5,6%) và đặt cạnh điểm FICO cũ (580) cùng XGBoost hộp đen (593).*
> *Ứng dụng gồm 6 màn hình: Tab 1 giải thích đóng góp cộng/trừ điểm của từng yếu tố; Tab 2 hiển thị đồ thị 20 nút với viền đậm cho biến đã biết và xác suất hậu nghiệm cho biến chưa biết; Tab 3 duyệt 4.320 tổ hợp can thiệp `do()` để tìm lộ trình nâng điểm lên 673 với chi phí nỗ lực thấp nhất; Tab 4 mô phỏng what-if — khi bật biến cố mất việc và lạm phát cao, điểm giảm ngay 73 điểm xuống 540; Tab 5 sinh lời khuyên từ Gemini đạt khớp số và bao phủ 100%; và Tab 6 công khai toàn bộ nguồn dữ liệu WHO, World Bank cùng bảng CPT để kiểm toán."*

---

### SLIDE 17 — LLM diễn giải & Kiểm tra độ trung thành *(Người trình bày: PHÚC · Nguồn: Bảng 10 `reports/results/llm.md`, `04_thuc_nghiem.md` §4.11, `05_he_thong.md` §5.3)*
* **Nguyên tắc cốt lõi chống ảo giác (Hallucination):**
  * **Tách bạch tính toán và diễn đạt:** Mạng Bayes tính **100% con số** (`facts.json`) $\rightarrow$ LLM chỉ tóm tắt thành lời khuyên tiếng Việt ($\le 220$ từ, 4 mục: *Tóm tắt, Yếu tố chính, Nên làm gì, Lưu ý*), cấm tự tính hay suy diễn ngoài dữ kiện.
* **Kiểm chứng kép (Tự động + Chấm tay độc lập):**
  1. **Tự động (`faithfulness.py`):** Kiểm tra `number_precision` (khớp số dữ kiện), `fact_coverage` (đủ điểm, mức rủi ro, yếu tố kéo xuống mạnh nhất) và `direction_ok` (không nói ngược chiều tác động).
  2. **Chấm tay độc lập (Rubric 1–5, 150 dòng = 50 hồ sơ × 3 nguồn):** Đánh giá *Đúng dữ kiện – Dễ hiểu – Hữu ích* (mỗi thành viên chấm 15 hồ sơ riêng + 5 hồ sơ chung để đo đồng thuận và bắt thêm lỗi ngữ nghĩa như gán sai đơn vị `%` cho chi phí nỗ lực).
* **Bảng 10 – Kết quả đánh giá tự động trên 50 hồ sơ kiểm thử:**

| Nguồn sinh lời khuyên | Khớp số (`number_precision`) | Bao phủ (`fact_coverage`) | Đúng hướng (`direction_ok`) | **Trung thành (`faithful`)** | Số bài có số ngoài dữ kiện | Số bài sai hướng |
|---|---:|---:|---:|---:|---:|---:|
| `template` *(mốc dự phòng)* | 1,000 | 1,000 | 1,00 | **100%** | 0/50 | 0/50 |
| `template_corrupted` *(đối chứng âm)* | 0,959 | 0,823 | 0,04 | **0%** | 48/50 | 48/50 |
| **`groq:qwen3.8-27b`** *(chọn mặc định)* | **1,000** | 0,993 | 0,96 | **94%** | **0/50** | 2/50 |
| `groq:gpt-oss-120b` *(đối sánh)* | 0,989 | 0,993 | 0,98 | **72%** | 12/50 | 1/50 |

* **Kết luận thiết kế:**
  * Đối chứng âm đạt **0%** chứng minh bộ kiểm tra bắt lỗi hiệu quả.
  * **Mô hình lớn hơn không đồng nghĩa trung thành hơn:** `gpt-oss-120b` chỉ đạt **72%** (tự cộng/trừ điểm ở 12/50 bài và qua chấm tay còn phát hiện tự gắn sai đơn vị `%` cho chi phí nỗ lực, hoặc bỏ sót cảnh báo khi mục tiêu vượt trần khả thi) $\rightarrow$ chốt **`qwen3.8-27b` (94%, 0 số bịa)** cho Groq, hỗ trợ song song **Gemini** và tự động fallback về `template` khi lỗi API.

> **🎤 Lời thoại gợi ý cho Phúc (~1 phút 15 giây):**
> *"Ở tầng tư vấn bằng LLM, rủi ro lớn nhất trong tài chính là mô hình tự bịa xác suất hoặc tính nhẩm sai. Nhóm giải quyết bằng cách đóng gói toàn bộ kết quả của Mạng Bayes thành JSON dữ kiện và buộc LLM chỉ diễn đạt lại, đi kèm kiểm chứng kép: vừa kiểm tra tự động trên 3 tiêu chí, vừa chấm tay độc lập 150 lời khuyên theo Rubric 1–5.*
> *Trên Bảng 10, đối chứng âm cố ý sửa sai bị bắt lỗi 100% (trung thành giảm về 0%). Khi so sánh hai mô hình thực tế trên 50 hồ sơ, mô hình nhỏ `qwen3.8-27b` đạt 94% trung thành và không bịa bất kỳ con số nào, vượt xa mô hình lớn `gpt-oss-120b` chỉ đạt 72% do 12 trên 50 bài tự ý cộng trừ điểm dù prompt đã cấm. Qua chấm tay, nhóm còn phát hiện thêm các lỗi ngữ nghĩa tinh vi mà kiểm tra tự động khó thấy, như việc `gpt-oss-120b` tự gắn đơn vị phần trăm cho điểm chi phí nỗ lực hoặc bỏ sót cảnh báo khi hồ sơ không thể chạm mốc mục tiêu. Từ đó hệ thống chọn `qwen3.8-27b` làm mặc định và luôn có `template` dự phòng an toàn."*

---

### SLIDE 18 — Kết luận, Hạn chế & Hướng phát triển *(Người trình bày: Mạnh · Nguồn: `06_ket_luan.md`)*
* **1. Kết luận thực nghiệm (trung thực & toàn diện):**
  * **Về phân biệt:** ML hộp đen xếp hạng tốt hơn (`XGBoost` **0,740** vs `BN-Expert-Mono` **0,715**, chênh **0,026** AUC); nhưng `BN-Expert-Mono` vượt xa luật **FICO** (**0,692**, hơn **+0,022** AUC) và hiệu chỉnh tốt (ECE **0,0047**).
  * **Giá trị cốt lõi của Mạng Bayes:** Chịu **thiếu thông tin ngẫu nhiên** tốt nhất (vượt XGBoost từ mức che 20%: **0,699** vs **0,689**; ở 50% chỉ giảm **−0,049** vs **−0,119**), **nhất quán tri thức chuyên gia** cao nhất trong các mô hình học (vi phạm TB **11,3%** vs XGBoost **53,9%**), **giải thích ổn định** hơn boosting (Spearman **0,943** vs **0,888**), mô hình gọn nhẹ (~**116 KB**) và sở hữu **suy luận ngược `do()` + what-if nhân quả** mà ML hộp đen không có.
* **2. Hạn chế nhìn nhận thẳng thắn:**
  * Home Credit không công bố quốc gia/tiền tệ $\rightarrow$ quy đổi VND sang ngũ phân vị trong demo là *giả định*; lớp tri thức vĩ mô VN chỉ phục vụ what-if.
  * Một số tham số lớp chuyên gia ($\lambda = 0{,}3$, chi phí đòn bẩy) là *giả định* ($\lambda=0 \rightarrow 0{,}3$ làm AUC giảm nhẹ **0,7168 $\rightarrow$ 0,7146**).
  * CPT dạng bảng cần nhiều dữ liệu (1% mẫu chỉ đạt **0,661**) và không ngoại suy được khi thiếu toàn bộ một trạng thái cha (`not_working`: **−0,1745** AUC); thiếu biến mạnh nhất (`ext_score`) kém hơn ML do cấu trúc thưa.
* **3. Hướng phát triển:**
  * Dùng **CPT tham số hóa** (noisy-OR / logistic CPD) cho nút nhiều cha; mở rộng ràng buộc đơn điệu sang biến thâm niên.
  * Kết hợp dữ liệu tín dụng/khảo sát hộ gia đình Việt Nam & thu nhập ngành GSO để học trực tiếp $\lambda$.
  * **Kiến trúc lai (Hybrid):** Dùng ML hộp đen để xếp hạng sàng lọc + dùng Mạng Bayes để giải thích nhân quả, chạy what-if và tư vấn lộ trình cải thiện; bổ sung kiểm định công bằng (*fairness*).

---

## Phần 2: Checklist cho Phúc khi ghép toàn bộ 18 Slide (tối 01/12)

| Cụm Slide | Người gửi nội dung | Người nói (02/12) | Điểm cần kiểm tra khi ghép |
|---|---|---|---|
| **Slide 1–3** | **Phúc** dựng | Mạnh | Đúng tên đề tài, sơ đồ nhân quả rõ, bảng so sánh FICO khớp số |
| **Slide 4–6** | **Nam** gửi | Nam | Dùng đúng ảnh `reports/figures/bn_expert_dag.png`, ghi rõ ranh giới nguồn gốc vs *giả định* |
| **Slide 7–8** | Mạnh / nhóm | Mạnh | Công thức `m-estimate`, calibrated noisy-OR, POCS, quy đổi điểm 300–850 & `do()` |
| **Slide 9–15** | **Khôi** gửi | Khôi | Hình lấy nguyên gốc từ `reports/figures/exp_*.png` (không vẽ lại), số khớp `results_summary.md` |
| **Slide 16–17** | **Phúc** dựng | **Phúc** | Đủ ảnh 6 tab demo (`demo_01`..`demo_06`) + link dự phòng, Bảng 10 LLM khớp tuyệt đối |
| **Slide 18** | **Phúc** dựng | Mạnh | Đủ 3 khối Kết luận – Hạn chế – Hướng phát triển cân đối trên 1 trang |

* **Đồng bộ thẩm mỹ:** Thống nhất 1 font không chân hỗ trợ tiếng Việt tốt (ví dụ *Segoe UI*, *Inter* hoặc *Roboto*), cỡ chữ nội dung $\ge 16\text{ pt}$, đánh số trang `x / 18` ở góc dưới để hội đồng dễ đặt câu hỏi theo số slide.
* **Kiểm tra bảo mật lần cuối trước khi xuất PDF/PPTX:** Đảm bảo không có ảnh chụp nào lộ chuỗi API key hoặc thông tin nhạy cảm; gửi file qua kênh trao đổi của nhóm, **không đưa file `.pptx`/`.pdf` vào Git**.
