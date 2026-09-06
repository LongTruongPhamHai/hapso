# HAPSO: Thuật Toán Lai A\*-PSO cho Lập Kế Hoạch Đường Bay UAV

## 📋 Tổng Quan Dự Án

Đây là đồ án tốt nghiệp **"Tối ưu hóa đường bay cho UAV trong môi trường có chướng ngại vật"**, thực hiện thuật toán lai **HAPSO (Hybrid A\*–PSO)** cho bài toán hoạch định quỹ đạo UAV an toàn, hiệu quả trong môi trường 2D tĩnh có chướng ngại vật, hướng đến ứng dụng vận chuyển logistics tự động (last-mile delivery, vận chuyển kho bãi, logistics đô thị).

- **Sinh viên thực hiện:** Trương Phạm Hải Long
- **Đơn vị:** Khoa Công nghệ Thông tin, Trường Đại học Thủy Lợi
- **GVHD:** ThS. Trần Thị Cẩm Giang
- **Bài báo liên quan:** _A Hybrid A–PSO Optimization Framework for Safe and Efficient UAV Path Planning in Autonomous Logistics Transportation_ — được chấp nhận trình bày tại **International Conference on Logistics and Transport (ICLT) 2026**.

Phần triển khai tham khảo và mở rộng ý tưởng từ bài báo nền tảng:

> C. Huang, Y. Zhao, M. Zhang and H. Yang, "APSO: An A\*-PSO Hybrid Algorithm for Mobile Robot Path Planning," in _IEEE Access_, vol. 11, pp. 43238-43256, 2023.

Dự án cung cấp môi trường mô phỏng toàn diện để xây dựng, huấn luyện, đánh giá và so sánh nhiều thuật toán lập kế hoạch đường đi, kèm khả năng trực quan hóa quỹ đạo và phân tích thống kê hiệu suất.

## 🎯 Tính Năng Chính

- **Thuật toán lai HAPSO**: A\* xây dựng quỹ đạo cơ sở an toàn → PSO cải tiến (SIW + TVAC + SOBL) tối ưu từng phân đoạn → làm mượt bằng đường cong Bezier.
- **Bộ lọc khoảng cách an toàn cho A\***: loại bỏ các điểm lân cận bám sát mép vật cản trong quá trình mở rộng nút.
- **Khởi tạo quần thể theo phân đoạn hình học**: cá thể PSO được sinh dọc theo hành lang nối hai điểm nút liên tiếp của quỹ đạo A\*, thay vì ngẫu nhiên toàn bản đồ, giúp hội tụ nhanh và tránh vị trí vô nghĩa.
- **Hàm thích nghi đa mục tiêu chuẩn hóa**: kết hợp chiều dài quỹ đạo, góc quay trung bình, góc quay lớn nhất và khoảng cách an toàn, với cơ chế phạt hai ngưỡng (va chạm / cận vật cản).
- **Đa thuật toán đối chứng**: A\*, PRM, RRT\*, HAPSO trên cùng bộ bản đồ và tiêu chí.
- **Giao diện trực quan bằng PyGame** và **biểu đồ so sánh bằng Matplotlib**.
- **Kiểm thử hàng loạt & thống kê**: chạy nhiều lần độc lập trên từng bản đồ, xuất Best/Worst/Mean/Median/Std Dev.
- **Trình quản lý bản đồ dạng lưới JSON**, hỗ trợ bản đồ tổng hợp và bản đồ mô phỏng từ ảnh vệ tinh/bản vẽ thực tế.

## 🏗️ Cấu Trúc Dự Án

```
hapso/
├── main.py                    # Ứng dụng chính
├── hapso.py                   # Thuật toán HAPSO (A* + PSO cải tiến + Bezier)
├── astar.py                   # Thuật toán A* với bộ lọc khoảng cách an toàn
├── prm.py                     # Thuật toán PRM (Probabilistic Roadmap)
├── rrt_star.py                 # Thuật toán RRT*
├── grid_map.py                # Quản lý bản đồ lưới, bảng băm vật cản
├── utils.py                   # Hàm tiện ích (hình học, khoảng cách, góc quay...)
├── visualization.py           # Trực quan hóa quỹ đạo và biểu đồ so sánh
├── requirements.txt           # Thư viện phụ thuộc
├── config/                    # Cấu hình
│   ├── colors.py              # Màu sắc hiển thị
│   ├── parameter.py           # Tham số thuật toán (xem bảng bên dưới)
│   └── ui.py                  # Hằng số giao diện
└── data/                      # Dữ liệu
    ├── maps/                  # File bản đồ JSON (KB01, KB02, KB03...)
    └── results/                # Kết quả thực nghiệm (Excel/CSV, biểu đồ)
```

## 🚀 Cài Đặt

1. Sao chép repository
2. Tạo môi trường ảo: `python -m venv venv`
3. Kích hoạt:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Cài đặt thư viện: `pip install -r requirements.txt`

### Thư viện chính sử dụng

| Thư viện   | Vai trò                                        |
| ---------- | ---------------------------------------------- |
| NumPy      | Xử lý mảng đa chiều, tính toán hàm mục tiêu    |
| Pygame     | Mô phỏng, trực quan hóa quỹ đạo thời gian thực |
| Matplotlib | Vẽ biểu đồ phân tích, so sánh hiệu năng        |
| Pandas     | Thu thập, xử lý dữ liệu thực nghiệm dạng bảng  |
| Openpyxl   | Xuất kết quả tổng hợp sang Excel               |

Môi trường phát triển tham khảo: Python 3.10, Windows 11, CPU AMD Ryzen 7 8845HS, RAM 16GB, GPU AMD Radeon 780M.

## 📖 Sử Dụng

Chạy chương trình chính:

```bash
python main.py
```

## 🧠 Các Thuật Toán

1. **HAPSO** — Kiến trúc 2 tầng:
   - **Tầng 1 (A\*)**: tìm quỹ đạo cơ sở ngắn nhất, an toàn nhờ bộ lọc khoảng cách tới vật cản.
   - **Tầng 2 (PSO cải tiến)**: tối ưu từng phân đoạn 3 điểm liên tiếp bằng PSO tích hợp:
     - **SIW** (Stochastic Inertia Weight) – trọng số quán tính ngẫu nhiên, cân bằng khám phá/khai thác.
     - **TVAC** (Time-Varying Acceleration Coefficients) – hệ số học tập cá nhân/xã hội biến thiên theo thời gian.
     - **SOBL** (Stochastic Opposition-Based Learning) – học đối lập ngẫu nhiên, mở rộng không gian khám phá, tránh cực trị cục bộ.
   - **Làm mượt Bezier**: thay thế các góc cua vượt ngưỡng bằng đường cong Bezier bậc 2, kiểm tra lại an toàn trước khi chấp nhận.
2. **A\*** — Tìm kiếm trên lưới với hàm heuristic Euclidean, có bổ sung kiểm tra hành lang an toàn.
3. **PRM** — Lấy mẫu ngẫu nhiên xây dựng đồ thị lộ trình xác suất.
4. **RRT\*** — Cây tìm kiếm ngẫu nhiên mở rộng nhanh, có tối ưu lại chi phí nhánh.

### Tham số cấu hình mặc định của HAPSO

| Tham số                  | Ký hiệu           | Giá trị   | Ý nghĩa                                 |
| ------------------------ | ----------------- | --------- | --------------------------------------- |
| Khoảng cách nguy hiểm    | d_danger          | 0.0701    | Ngưỡng xác định va chạm                 |
| Khoảng cách an toàn      | d_min             | 1.0       | Khoảng cách tối thiểu tới vật cản       |
| Phạm vi tìm kiếm vật cản | M_cell            | 3         | Bán kính ô lưới quét vật cản xung quanh |
| Số vòng lặp dừng sớm     | patience          | 15        | Số vòng không cải thiện trước khi dừng  |
| Số lượng cá thể          | N_particles       | 20        | Kích thước quần thể PSO mỗi phân đoạn   |
| Số vòng lặp tối đa       | T_max             | 50        | Số vòng lặp tối ưu hóa mỗi phân đoạn    |
| Trọng số quán tính       | ω_min, ω_max      | 0.4 – 0.9 | Khoảng dao động SIW                     |
| Hệ số học tập cá nhân    | c1_i, c1_f        | 2.5 → 0.5 | TVAC – ưu tiên khám phá → khai thác     |
| Hệ số học tập tập thể    | c2_i, c2_f        | 0.5 → 2.5 | TVAC – ưu tiên khám phá → khai thác     |
| Phạt va chạm             | collision_penalty | 10        | Phạt khi quỹ đạo va chạm vật cản        |
| Phạt cận an toàn         | safety_penalty    | 5         | Phạt khi quỹ đạo sát mép vật cản        |
| Biên SOBL                | lb_i, ub_i        | 3         | Giới hạn tìm điểm đối lập               |
| Ngưỡng góc cua Bezier    | Bezier_threshold  | 30.0°     | Góc tối thiểu để áp dụng làm mượt       |
| Tỉ lệ Bezier             | r                 | 0.65      | Mức độ uốn cong quỹ đạo                 |
| Số điểm nội suy Bezier   | N                 | 7         | Số điểm trên mỗi đoạn cong              |

Bộ trọng số hàm thích nghi: `w1 = 0.3` (chiều dài), `w2 = 0.3` (góc quay trung bình), `w3 = 0.1` (góc quay lớn nhất), `w4 = 0.3` (khoảng cách an toàn).

## 📊 Chỉ Số Đánh Giá

- **Tỷ lệ thành công** (Success Rate)
- **Độ dài đường đi** (Distance) — càng nhỏ càng tốt
- **Góc quay trung bình** (Average Angle) — càng nhỏ, quỹ đạo càng mượt
- **Khoảng cách an toàn tối thiểu** (Min Clearance) — càng lớn càng an toàn
- **Thời gian tính toán** (Execution Time)
- **Giá trị hàm đánh giá tổng hợp** (Evaluation) — càng nhỏ càng tối ưu toàn diện

## 🗺️ Định Dạng Bản Đồ

File JSON gồm `width`, `height` và ma trận lưới với quy ước giá trị:

| Giá trị | Ý nghĩa                |
| ------- | ---------------------- |
| 0       | FREE – ô trống         |
| 1       | OBSTACLE – vật cản     |
| 2       | START – điểm xuất phát |
| 3       | GOAL – điểm đích       |

Tọa độ vật cản được lưu bằng bảng băm (hash set) để kiểm tra va chạm với độ phức tạp O(1).

### Bộ bản đồ thực nghiệm (30×30, 3 kịch bản)

| Bản đồ  | Tỷ lệ vật cản | Đặc trưng                                                      |
| ------- | ------------- | -------------------------------------------------------------- |
| KB01-ES | ≈11%          | Vật cản thưa, 3 cụm oval rải rác                               |
| KB01-MD | ≈28%          | Vật cản dày, lối đi hẹp đối xứng                               |
| KB01-HD | ≈26%          | Vật cản hình chữ U ở giữa bản đồ                               |
| KB02-MZ | ≈14%          | Dạng mê cung, nhiều vách ngăn dài                              |
| KB02-CL | ≈28%          | Cụm vật cản ngẫu nhiên, mô phỏng tự nhiên                      |
| KB03-ID | ≈45%          | Trong nhà (workshop), UAV bay ở độ cao 1.5m                    |
| KB03-OD | ≈55%          | Khu đô thị thực tế (phường Phúc Lợi, Hà Nội), bay ngang tầng 2 |

## 📈 Tóm Tắt Kết Quả Thực Nghiệm

- **Kịch bản 1** (thích nghi mật độ/hình học vật cản): HAPSO đạt **tỷ lệ thành công 100%** trên cả 3 bản đồ KB01-ES/MD/HD, độ lệch chuẩn chiều dài đường đi thấp (~0.17–0.20), thời gian tính toán trung bình dưới 1.4 giây.
- **Kịch bản 2** (so sánh với A\*, RRT\*, PRM trên KB02-MZ, KB02-CL): HAPSO cho **hàm đánh giá tốt nhất** trong cả hai bản đồ, đồng thời là thuật toán duy nhất cùng A\* đạt tỷ lệ thành công 100% mà vẫn đảm bảo khoảng cách an toàn tối thiểu — điều A\* và PRM không đáp ứng được (bị áp giá trị phạt).
- **Kịch bản 3** (bản đồ thực tế KB03-ID, KB03-OD): HAPSO duy trì tỷ lệ thành công 100%, góc quay trung bình thấp nhất trong số các thuật toán so sánh, cho thấy tiềm năng ứng dụng thực tiễn dù thời gian tính toán lớn hơn (do các bước tối ưu và làm mượt bổ sung).

Nhìn chung, so với A\*, RRT\* và PRM, HAPSO nhất quán tạo ra quỹ đạo **ngắn hơn hoặc tương đương, mượt hơn đáng kể (góc quay trung bình giảm rõ rệt) và an toàn hơn** (đảm bảo khoảng cách tối thiểu tới vật cản), đánh đổi bằng thời gian tính toán tăng — phù hợp với bài toán hoạch định đường bay ngoại tuyến.

## 🖼️ Hình Ảnh Kết Quả HAPSO

### KB01

<table>
  <tr>
    <td><img src="data/results/images/KB01-ES HAPSO 2026-08-07 070856.png" width="100%"></td>
    <td><img src="data/results/images/KB01-MD HAPSO 2026-08-07 071452.png" width="100%"></td>
    <td><img src="data/results/images/KB01-HD HAPSO 2026-08-07 072035.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">KB01-ES</td>
    <td align="center">KB01-MD</td>
    <td align="center">KB01-HD</td>
  </tr>
</table>

### KB02

<table>
  <tr>
    <td><img src="data/results/images/KB02-MZ HAPSO 2026-08-07 072836.png" width="100%"></td>
    <td><img src="data/results/images/KB02-CL HAPSO 2026-08-07 074857.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">KB02-MZ</td>
    <td align="center">KB02-CL</td>
  </tr>
</table>

### KB03

<table>
  <tr>
    <td><img src="data/results/images/KB03-ID HAPSO 2026-08-07 091843.png" width="100%"></td>
    <td><img src="data/results/images/KB03-OD HAPSO 2026-08-07 092145.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">KB03-ID</td>
    <td align="center">KB03-OD</td>
  </tr>
</table>

### OT

<table>
  <tr>
    <td><img src="data/results/images/OT01 HAPSO 2026-07-04 095938.png" width="100%"></td>
    <td><img src="data/results/images/OT02 HAPSO 2026-07-04 102505.png" width="100%"></td>
    <td><img src="data/results/images/OT03 HAPSO 2026-07-04 110428.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">OT01</td>
    <td align="center">OT02</td>
    <td align="center">OT03</td>
  </tr>
  <tr>
    <td><img src="data/results/images/OT04 HAPSO 2026-07-05 211246.png" width="100%"></td>
    <td><img src="data/results/images/OT05 HAPSO 2026-07-05 213538.png" width="100%"></td>
    <td></td>
  </tr>
  <tr>
    <td align="center">OT04</td>
    <td align="center">OT05</td>
    <td></td>
  </tr>
</table>

## ⚠️ Hạn Chế & Hướng Phát Triển

**Hạn chế hiện tại:**

- Chỉ hoạch định trong không gian 2D với vật cản tĩnh, chưa xử lý độ cao và vật cản động.
- Không gian tìm kiếm PSO phụ thuộc vào kết quả khởi tạo từ A\*.
- Ngưỡng an toàn cố định có thể loại bỏ nhầm một số lộ trình tối ưu.
- Hàm thích nghi và bước làm mượt Bezier tách biệt, có nguy cơ quỹ đạo lấn hành lang an toàn sau khi làm mượt.

**Hướng phát triển:**

- Mở rộng sang không gian 3D và xử lý vật cản động.
- Ứng dụng học máy/học tăng cường để tự động cấu hình tham số.
- Tích hợp trực tiếp bộ lọc làm mượt vào hàm thích nghi của PSO.
- Triển khai lên bo mạch điều khiển UAV thực tế và thử nghiệm bay ngoài thực địa.

## 📚 Tài Liệu Tham Khảo Chính

1. Huang, C., Zhao, Y., Zhang, M., & Yang, H. (2023). APSO: An A\*-PSO Hybrid Algorithm for Mobile Robot Path Planning. _IEEE Access_, 11, 43238-43256.
2. Mohsan, S. A. H., Othman, N. Q. H., Li, Y., Alsharif, M. H., & Khan, M. A. (2023). Unmanned aerial vehicles (UAVs): Practical aspects, applications, open challenges, security issues, and future trends. _Intelligent Service Robotics_, 16(1), 109-137.
3. Russell, S., & Norvig, P. (1995). _Artificial Intelligence: A Modern Approach_. Prentice-Hall.
4. Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization. _Proceedings of ICNN'95_, Vol. 4, 1942-1948.
5. Cai, M. (2022). An improved particle swarm optimization algorithm and its application to the extreme value optimization problem of multivariable function. _Computational Intelligence and Neuroscience_, 2022, 1935272.
6. Xiang, J., Xie, J., & Chen, J. (2024). Learning-accelerated A\* search for risk-aware path planning. _AIAA SCITECH 2024 Forum_.
7. Ratnaweera, A., Halgamuge, S. K., & Watson, H. C. (2004). Self-organizing hierarchical particle swarm optimizer with time-varying acceleration coefficients. _IEEE Transactions on Evolutionary Computation_, 8(3), 240-255.
8. Tizhoosh, H. R. (2005). Opposition-based learning: a new scheme for machine intelligence. _CIMCA-IAWTIC'06_, Vol. 1, 695-701.
9. Satai, H. A., Zahra, M. M. A., Rasool, Z. I., Abd-Ali, R. S., & Pruncu, C. I. (2021). Bézier curves-based optimal trajectory design for multirotor UAVs with any-angle pathfinding algorithms. _Sensors_, 21(7), 2460.
10. Zhang, Z. (2024). A review of unmanned aerial vehicle path planning techniques. _Applied and Computational Engineering_, 33, 234-241.
11. Ericson, C. (2004). _Real-Time Collision Detection_. CRC Press.

## 📝 Trích Dẫn

Nếu sử dụng dự án này cho nghiên cứu, vui lòng trích dẫn:

```
Trương Phạm Hải Long (2026). Tối ưu hóa đường bay cho UAV trong môi trường có
chướng ngại vật. Đồ án tốt nghiệp, Trường Đại học Thủy Lợi.

A Hybrid A–PSO Optimization Framework for Safe and Efficient UAV Path Planning
in Autonomous Logistics Transportation. ICLT 2026.
```
