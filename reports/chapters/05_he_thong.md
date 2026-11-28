## 5. Hệ thống demo và LLM diễn giải

<!-- Ghi chú: Sau khi deploy xong (28/11), điền đường dẫn công khai của ứng dụng vào mục 5.4. -->

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

Hệ thống demo được thiết kế theo kiến trúc tách biệt rõ ràng giữa **tầng suy luận xác suất chính xác** và **tầng diễn đạt ngôn ngữ tự nhiên**, gồm bốn bước nối tiếp:

1. **Tiếp nhận và quy đổi đầu vào (`src/app/convert.py`).** Người dùng nhập hồ sơ bằng tiếng Việt theo đơn vị tiền tệ thực tế (triệu VND) trên ba nhóm thông tin: *Nghề nghiệp*, *Thu nhập & gia đình* và *Khoản vay & tín dụng*. Các biến liên tục được quy đổi sang trạng thái rời rạc của Mạng Bayes: thu nhập bình quân đầu người của hộ được xếp vào năm nhóm dựa trên trung điểm giữa mức trung bình hai ngũ phân vị kề nhau của GSO KSMS 2024 (*giả định* quy đổi do GSO không công bố cận phân vị); tỷ số trả góp trên thu nhập cá nhân (DSTI) và tổng dư nợ trên thu nhập năm (LTI) dùng ngưỡng nghiệp vụ cố định (`configs/discretize.yaml`); mức tự đánh giá lịch sử trả nợ và khu vực cư trú được ánh xạ sang ngũ phân vị điểm tín dụng ngoài và xếp hạng vùng của Home Credit (*giả định*). Nếu người dùng chọn trạng thái không đi làm, cả ngành và thâm niên đều tự động gán về `not_working`.
2. **Suy luận Mạng Bayes và đối sánh mô hình (`src/bn/`, `models/`).** Mô hình mặc định là `BN-Expert-Mono` (có thể chuyển sang `BN-Expert` trên thanh bên để quan sát tác động của ràng buộc đơn điệu). Từ tập bằng chứng hợp lệ, bộ suy luận chính xác tính xác suất vỡ nợ hậu nghiệm, quy đổi sang thang điểm 300–850, xác định mức đóng góp của từng yếu tố so với phân phối biên của quần thể, giải bài toán phản thực `do()` cùng hậu nghiệm ngược, đồng thời cập nhật phân phối khi kích hoạt các biến cố ở lớp tri thức. Để người dùng đối chiếu trực quan trên cùng một hồ sơ, hệ thống chấm song song bộ luật FICO tái hiện đề tài cũ (`src/baselines/fico.py`, AUC thực nghiệm {{num:auc.FICO}}) và mô hình hộp đen XGBoost trên cùng đầu vào rời rạc (`models/xgb_disc.json`, AUC {{num:auc.XGBoost-disc}}, so với {{num:auc.BN-Expert-Mono}} của `BN-Expert-Mono`).
3. **Đóng gói dữ kiện tất định (`src/llm/facts.py`).** Mọi đầu ra định lượng—điểm số, phân hạng rủi ro, xác suất vỡ nợ cá nhân và trung bình quần thể, danh sách trường chưa biết, ba yếu tố kéo điểm xuống mạnh nhất, ba yếu tố nâng điểm, biến động điểm what-if và các phương án cải thiện khả thi—được tổng hợp thành một cấu trúc JSON duy nhất làm nguồn sự thật cho bước sinh lời khuyên.
4. **Diễn giải bằng LLM và hậu kiểm tự động (`src/llm/client.py`, `src/llm/faithfulness.py`).** `LLMClient` gửi dữ kiện JSON tới nhà cung cấp được chọn (Gemini, Groq, Ollama hoặc mẫu tất định `template`), lưu đệm kết quả theo mã băm của prompt tại `.cache/llm/` và kiểm tra độ trung thành trước khi hiển thị lên giao diện.

### 5.2. Các màn hình
Giao diện ứng dụng (`src/app/streamlit_app.py`) gồm thanh cài đặt bên trái—cho phép chọn mô hình Mạng Bayes, nguồn sinh lời khuyên và nạp nhanh bộ hơn 50 hồ sơ mẫu giả lập trong `data/samples/profiles.csv` (bao phủ đủ các nhóm ngành, người hưu trí/thất nghiệp, hồ sơ không nợ, hồ sơ trả góp nặng trên 40% thu nhập và hồ sơ khuyết thông tin)—cùng biểu mẫu nhập liệu ba cột ở phần đầu trang. Điểm khác biệt cốt lõi so với biểu mẫu chấm điểm cứng là **mọi trường đầu vào đều có tùy chọn *"Không rõ"***: khi người dùng để trống nhiều thông tin, hệ thống vẫn tính được điểm hợp lệ nhờ Mạng Bayes lấy biên chính xác trên các biến ẩn theo phân phối xác suất, thay vì phải điền giá trị trung vị hay gán điểm trung tính tùy ý. Ngay dưới biểu mẫu, hộp mở rộng *"Trạng thái BN sau quy đổi"* công khai toàn bộ trạng thái rời rạc và các giả định quy đổi để đảm bảo tính minh bạch.

Kết quả phân tích được tổ chức thành sáu màn hình chuyên biệt:

- **Tab 1 – Kết quả.** Màn hình tổng hợp điểm tín dụng (300–850), mức phân loại rủi ro, xác suất vỡ nợ ước tính và tỷ lệ trường thông tin chưa biết của hồ sơ đang xét. Bảng đối sánh đặt kết quả của Mạng Bayes cạnh điểm FICO rule-based và XGBoost, đi kèm biểu đồ thanh ngang biểu diễn số điểm cộng/trừ của từng yếu tố so với một hồ sơ có cùng các đặc trưng khác nhưng yếu tố đó ở mức phổ biến trong quần thể.

{{fig:demo_01_ket_qua.png|Màn hình Kết quả: điểm tín dụng, đối sánh FICO/XGBoost và biểu đồ đóng góp từng yếu tố}}

- **Tab 2 – Đồ thị nhân quả.** Toàn bộ cấu trúc DAG 20 nút được trực quan hóa bằng Graphviz, phân biệt màu giữa 14 nút học từ dữ liệu (xanh), 5 nút tri thức chuyên gia (cam) và nút đích Vỡ nợ (hồng cam). Các nút đã có bằng chứng từ biểu mẫu được tô viền đậm, còn nhãn bên trong mỗi nút cập nhật trực tiếp trạng thái hoặc xác suất hậu nghiệm ứng với hồ sơ hiện tại, giúp người dùng theo dõi đường truyền tác động từ ngành nghề tới rủi ro vỡ nợ.

{{fig:demo_02_do_thi.png|Màn hình Đồ thị nhân quả với trạng thái bằng chứng (viền đậm) và xác suất hậu nghiệm trên từng nút}}

- **Tab 3 – Suy luận ngược.** Người dùng chọn mức điểm mục tiêu trên thanh trượt (400–800) để hệ thống duyệt lưới can thiệp `do()` trên 7 đòn bẩy có thể điều khiển (`configs/backward.yaml`) và liệt kê các phương án không bị trội có chi phí nỗ lực thấp nhất, hoặc thông báo mức điểm tối đa có thể đạt được nếu mục tiêu vượt quá giới hạn can thiệp ngắn và dài hạn. Phần dưới trình bày bảng *điều kiện cần* theo suy luận Bayes ngược (kèm hệ số nâng *lift*) đối với ba mục tiêu: không vỡ nợ, sở hữu nhà, hoặc sở hữu cả nhà và xe.

{{fig:demo_03_suy_luan_nguoc.png|Màn hình Suy luận ngược: phương án can thiệp phản thực do() và phân phối hậu nghiệm điều kiện cần}}

- **Tab 4 – What-if biến cố.** Màn hình cho phép bật giả lập các cú sốc ngoài dữ liệu lịch sử (mất việc, biến cố sức khỏe chi y tế lớn, lạm phát, kinh tế suy giảm, chi phí sinh hoạt tăng) để quan sát ngay mức sụt giảm điểm và xác suất hụt dòng tiền trung gian (trong thực nghiệm với $\lambda = 0{,}3$, biến cố mất việc làm giảm trung bình {{num:whatif_job}} điểm và biến cố sức khỏe làm giảm {{num:whatif_health}} điểm ở nhóm đang đi làm). Riêng với hồ sơ khai báo không đi làm, hộp kiểm *"Mất việc"* tự động bị khóa để ngăn bằng chứng bất khả ($P(e) = 0$) và giải thích rõ lý do trên giao diện.

{{fig:demo_04_what_if.png|Màn hình What-if biến cố: mô phỏng tác động của các cú sốc vĩ mô và cá nhân lên điểm tín dụng}}

- **Tab 5 – Lời khuyên (LLM).** Khi nhấn tạo tư vấn, hệ thống hiển thị văn bản bốn mục bằng tiếng Việt dễ hiểu cho người không chuyên, đi kèm thanh trạng thái hậu kiểm (`✅ Trung thành với dữ kiện` hoặc `⚠️ Có điểm chưa khớp dữ kiện`), thông tin nhà cung cấp/mô hình, tỷ lệ khớp số liệu và độ bao phủ dữ kiện. Người dùng hoặc kiểm thử viên có thể mở khung *"Dữ kiện gửi cho LLM (JSON)"* ngay bên dưới để đối chiếu từng con số trong lời khuyên với đầu ra gốc của Mạng Bayes.

{{fig:demo_05_llm.png|Màn hình Lời khuyên LLM kèm nhãn kiểm tra độ trung thành tự động và dữ kiện JSON gốc}}

- **Tab 6 – Tri thức & CPT.** Màn hình tra cứu phục vụ kiểm toán mô hình: cho phép chọn bất kỳ nút nào trong mạng để xem lớp thuộc tính (dữ liệu hay chuyên gia), danh sách nút cha, trích dẫn nguồn xây dựng CPT và bảng xác suất có điều kiện chi tiết (với các nút có kích thước bảng vừa phải). Cuối trang tổng hợp danh mục toàn bộ cạnh nhân quả kèm lý do/bằng chứng đã được nhóm phê duyệt và bảng đối chiếu nguyên lý giữa đề tài FICO rule-based cũ với Mạng Bayes hiện tại.

{{fig:demo_06_tri_thuc.png|Màn hình Tri thức & CPT: tra cứu bảng xác suất có điều kiện, nguồn tri thức và lý do từng cạnh}}

### 5.3. LLM diễn giải và kiểm tra độ trung thành
Nguy cơ lớn nhất khi tích hợp LLM vào hệ thống hỗ trợ quyết định tài chính là hiện tượng **ảo giác số liệu** (tự bịa xác suất, tính nhẩm sai chênh lệch điểm) hoặc diễn giải ngược chiều tác động nhân quả. Để kiểm soát rủi ro này, nhóm áp dụng nguyên tắc thiết kế xuyên suốt: **LLM không tự tính xác suất mà chỉ diễn đạt lại dữ kiện đã được Mạng Bayes tính sẵn**.

Cụ thể, prompt hệ thống (`src/llm/prompt.py`) đặt sáu ràng buộc cứng: (1) chỉ sử dụng đúng các con số xuất hiện trong JSON dữ kiện, không tự ước lượng hay làm tròn khác đi; (2) không suy diễn nguyên nhân ngoài danh sách yếu tố đã cho và tuyệt đối không đề cập thuộc tính nhạy cảm (giới tính, dân tộc, tôn giáo); (3) trình bày tiếng Việt tôn trọng, ngắn gọn (không quá 220 từ); (4) tuân thủ đúng bốn mục tiêu đề in đậm gồm **Tóm tắt**, **Yếu tố chính**, **Nên làm gì**, **Lưu ý**; (5) phần khuyến nghị hành động chỉ được dựa trên danh sách `ke_hoach` phản thực và kịch bản `what_if` trong dữ kiện; (6) nêu rõ đây là mô hình minh họa học từ dữ liệu công khai, không phải quyết định cấp tín dụng chính thức.

Sau khi LLM trả lời, mô-đun `src/llm/faithfulness.py` tự động kiểm tra từng văn bản trên ba tiêu chí định lượng:
- **Độ chính xác con số (`number_precision`):** tỷ lệ con số xuất hiện trong văn bản khớp với tập số liệu cho phép trích từ JSON dữ kiện (hỗ trợ cả định dạng dấu phẩy thập phân và dấu chấm phân tách hàng nghìn kiểu Việt Nam, đồng thời loại trừ các nhãn thứ tự như *"kế hoạch 2"*, *"phương án 1"* để tránh bắt nhầm).
- **Độ bao phủ dữ kiện bắt buộc (`fact_coverage`):** kiểm tra văn bản có nêu đầy đủ điểm số ước tính, mức phân hạng rủi ro và tên yếu tố kéo điểm xuống mạnh nhất (nếu hồ sơ có yếu tố bất lợi) hay không.
- **Đúng hướng tác động (`direction_ok`):** kiểm tra heuristic từng câu trong phần mô tả hiện trạng (trước mục khuyến nghị) nhằm phát hiện lỗi gọi nhầm yếu tố kéo điểm xuống thành *"điểm mạnh / giúp tăng điểm"* hoặc ngược lại.

Một lời khuyên chỉ được gắn nhãn **trung thành (`faithful`)** khi đạt tuyệt đối cả ba tiêu chí trên. Để xác nhận bộ kiểm tra thực sự phát hiện được lỗi thay vì luôn cho qua, nhóm xây dựng thêm nguồn **đối chứng âm (`template_corrupted`)** bằng cách lấy lời khuyên chuẩn từ `template` rồi cố ý thay đổi điểm số và đảo ngược từ khóa hướng tác động của một yếu tố.

{{table:llm}}

Kết quả đánh giá tự động trên 50 hồ sơ kiểm thử (Bảng 10) xác nhận `template` đạt độ trung thành {{num:llm_faithful.template}}, trong khi đối chứng âm `template_corrupted` giảm về {{num:llm_faithful.template_corrupted}}, chứng minh bộ lọc bắt được hoàn toàn các ca sai lệch cố ý. Trên hai mô hình thực tế chạy qua Groq API, `qwen3.8-27b` đạt tỷ lệ trung thành {{num:llm_faithful.groq:qwen3.8-27b}} (không bịa bất kỳ con số nào ngoài dữ kiện, chỉ có {{num:llm_n_wrong_dir.groq:qwen3.8-27b}} trường hợp vướng cảnh báo hướng heuristic), vượt xa mô hình có quy mô tham số lớn hơn là `gpt-oss-120b` ({{num:llm_faithful.groq:gpt-oss-120b}}, do {{num:llm_n_bad_numbers.groq:gpt-oss-120b}}/50 lời khuyên tự thực hiện phép cộng trừ điểm dù prompt đã cấm). Từ bằng chứng thực nghiệm này, hệ thống chốt `qwen/qwen3.8-27b` làm mô hình Groq mặc định cho demo (`configs/llm.yaml`), đồng thời tự động chuyển về lời khuyên tất định `template` nếu gặp lỗi kết nối hoặc hết hạn mức truy cập sau khi đã thử lại (HTTP 429 retry).

Vì quy tắc kiểm tra hướng `direction_ok` dựa trên khớp từ khóa nên vẫn có giới hạn với câu ghép phức tạp, nhóm kết hợp thêm bước **đánh giá thủ công độc lập** của ba thành viên trên bộ 150 lời khuyên (`experiments/llm_faithfulness/samples_for_rating.csv`, gồm 3 nguồn × 50 hồ sơ; mỗi người chấm 15 hồ sơ riêng và 5 hồ sơ chung để đo độ đồng thuận) theo thang điểm Rubric 1–5 (`docs/handoff/llm_rating_rubric.md`) trên ba khía cạnh: *Đúng dữ kiện*, *Dễ hiểu* và *Hữu ích*.

<!-- Mạnh sẽ tổng hợp bảng điểm chấm tay trung bình & độ đồng thuận của Nam, Khôi, Phúc sau ngày 30/11 để đối chiếu bổ sung với Chương 4. -->

### 5.4. Triển khai
Ứng dụng được đóng gói gọn nhẹ để vận hành hoàn toàn trên hạ tầng miễn phí mà **không cần tải tập dữ liệu gốc Home Credit** lên máy chủ (`docs/DEPLOY.md`). Toàn bộ tham số cần thiết cho suy luận trực tuyến đã được xuất sẵn ra định dạng văn bản JSON đặt trong thư mục `models/` (gồm `bn_expert_mono.json`, `bn_expert.json`, `discretizer.json` và mô hình đối sánh `xgb_disc.json` khoảng vài trăm KB), kết hợp cùng `configs/`, `knowledge_base/` và `data/samples/profiles.csv`. Tệp phụ thuộc riêng `src/app/requirements.txt` chỉ giữ các thư viện phục vụ giao diện và suy luận nhẹ (`streamlit`, `numpy`, `pandas`, `pyyaml`, `altair`, `graphviz`, `xgboost`), loại bỏ các thư viện huấn luyện/kiểm định nặng như `lightgbm`, `optuna`, `shap` hay `pgmpy` để rút ngắn thời gian khởi tạo container.

Hệ thống được triển khai công khai trên **Streamlit Community Cloud** (Python 3.12, điểm vào `src/app/streamlit_app.py`, với Hugging Face Spaces làm phương án dự phòng). Về bảo mật, khóa API (`GROQ_API_KEY`, `GEMINI_API_KEY`) tuyệt đối không lưu trong mã nguồn hay lịch sử Git mà chỉ nạp qua biến môi trường `.env` khi chạy cục bộ hoặc qua kho **Secrets** (`st.secrets`) trên đám mây; khóa Gemini được truyền qua HTTP header `x-goog-api-key` thay vì gắn vào URL, và thông báo lỗi trên giao diện chỉ hiển thị loại sự cố mà không làm lộ thông tin xác thực. Ngay cả khi triển khai ở môi trường không cấu hình khóa API, toàn bộ sáu màn hình của demo vẫn hoạt động đầy đủ với chế độ lời khuyên `template`.

<!-- Điền link sau khi deploy (28/11): Địa chỉ truy cập bản demo trực tuyến: https://...streamlit.app -->
