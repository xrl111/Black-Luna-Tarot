# PHỤ LỤC: PHÂN TÍCH CHUYÊN SÂU CÁC KIẾN TRÚC LUỒNG DỮ LIỆU (FLOW DIAGRAMS) BẰNG SƠ ĐỒ KỸ THUẬT

Tài liệu này cung cấp các mô hình kiến trúc dạng khối (Mermaid) đi sâu vào hệ thống Black Luna Tarot theo cấp độ từ dễ (luồng Web cơ bản) đến cực khó (cơ chế đồng bộ hóa cụm Kafka-Spark Streaming). NotebookLM sẽ dựa vào các giản đồ này để học lại cấu trúc toàn bộ mã nguồn.

---

## 🟢 Cấp độ 1: Luồng Giao Tiếp Người Dùng & AI Cơ Bản (Level 100)

Sơ đồ này mô tả Vòng đời Request-Response tiêu chuẩn của một Người dùng khi họ tương tác với Giao diện ứng dụng.

```mermaid
sequenceDiagram
    autonumber
    actor U as Người Dùng (Client)
    participant UI as React Frontend
    participant API as FastAPI Backend
    participant DB as MongoDB (OLTP)
    participant LLM as Ollama (Qwen2.5)

    U->>UI: Đăng nhập & Chọn kiểu bốc 3 lá Bài
    UI->>API: POST /api/v1/readings
    
    API->>DB: Truy vấn Lịch sử & Context (Ngôn ngữ/Chủ đề)
    DB-->>API: Trả về Object User Preferences
    
    API->>API: Trộn Context vào Prompt gốc (Prompt Injection)
    
    API->>LLM: Gửi Prompt (Local Server Port 11434)
    Note over API, LLM: Kết nối Stream (Server-Sent Events)
    
    loop Từng dải Token
        LLM-->>API: Trả về Dòng Text (e.g. "Lá bài này...")
        API-->>UI: Forward Chunk Text liên tục đến Web
        UI-->>U: Tạo hiệu ứng gõ phím (Typewriter)
    end
    
    API->>DB: Ghi đè trạng thái 'Hoàn thành' + Kết quả Full Text
```

---

## 🟡 Cấp độ 2: Xử Lý Biến Đảo Dữ Liệu Nhân Khẩu Học (Level 200 - RDBMS Auth & CDC Pipeline)

Khi người dùng Đăng nhập Login bằng tài khoản Google, họ không tương tác với MongoDB. Toàn bộ logic Nhân khẩu học (Demographics) đã được vi dịch vụ (Microservice) hóa ra hệ cơ sở dữ liệu riêng.

```mermaid
graph TD
    classDef client fill:#f9f,stroke:#333,stroke-width:2px;
    classDef api fill:#bbf,stroke:#333,stroke-width:2px;
    classDef db fill:#2A3F54,stroke:#fff,color:#fff;
    classDef kafka fill:#d34c4c,stroke:#fff,color:#fff;

    O[OAuth2 Google SSO] -->|JWT Payload| F(FastAPI Login Route)
    F -->|Session.add| PG[(PostgreSQL\nBảng 'Users')]:::db
    
    subgraph Debezium_Core [Hệ Sinh Thái CDC]
        PG -->|Write-Ahead Log WAL Tracking| DBZ[Kafka Connect\nDebezium Watcher]
        DBZ -->|Bóc tách JSON\nBiến số Update| TopicU{{Kafka Topic:\ndbserver1.users}}:::kafka
    end
    
    TopicU -->|Lưu giữ Snapshot 7 ngày| Broker(Hệ thống Apache Kafka)
```
**Phân tích kỹ thuật (Technical Depth):**
Thay vì để FastAPI phải gọi thêm 1 lệnh `producer.send(...)` gửi trạng thái thay đổi thông tin User vào Kafka (Gây nguy cơ lỗi Distributed Transaction), Debezium gắn thẳng vào lõi ổ đĩa của hệ quản trị Postgres. Khi bất kỳ hàng nào trên Postgres biến đổi (Ví dụ: `updated_at`, đổi `experience_level`), log ổ đĩa sẽ kích hoạt một Message Kafka không bao giờ trễ. Hệ thống đạt độ siêu vẹn toàn dữ liệu (Data Integrity).

---

## 🟠 Cấp độ 3: Mẫu Thiết Kế Fire-And-Forget Qua Kafka (Level 300 - Event Driven Logging)

Khi Luồng AI (Cấp độ 1) sinh ra dữ liệu thẻ bài, yêu cầu của hệ thống là không bao giờ làm đường truyền UI bị giật lag nếu việc lưu trữ Big Data bị ngẽn.

```mermaid
sequenceDiagram
    autonumber
    participant API as FastAPI (readings.py)
    participant BG as BackgroundTasks (Thread)
    participant Kafka as Kafka Producer (Port 9092)
    participant Disk as Kafka Log Segment
    
    API->>API: Sinh Reading JSON (user_id = 1, cards=...)
    API->>BG: Khởi tạo tiến trình chạy ngầm (Non-blocking)
    Note over API, BG: API Response trả về cho UI NGAY LẬP TỨC
    
    BG->>Kafka: json.dumps(message)
    Kafka->>Disk: Phân bổ dữ liệu theo Partition
    Disk-->>Kafka: ACK (Acknowledge = all)
    Kafka-->>BG: Xác nhận Topic tarot-events đã lưu
```
**Phân tích Kỹ thuật (Technical Depth):**
Thuật toán nhúng `BackgroundTasks` trong FastAPI (Tương đương Outbox Pattern siêu gọn) giúp chuyển giao nhiệm vụ chịu tải mạng (Network Overhead) sang các luồng con (Thread pool). Bằng phương thức `ACK=ALL`, cụm Kafka Broker cam kết gói dữ liệu bốc bài sẽ nằm vĩnh viễn trên RAM/Disk của Broker kể cả khi sập nguồn điện.

---

## 🔴 Cấp độ 4: Cơ Chế Khớp Nối Phân Tán In-Memory (Level 400 - Structured Streaming JOINs)

Đây là rào cản Kỹ thuật khó nhất của toàn bộ codebase (`spark_jobs/tarot_streaming.py`). Apache Spark phải đọc đồng thời 2 vòi xả dữ liệu khác biệt từ Kafka, tiền xử lý và gộp chúng lại với nhau (Denormalization).

```mermaid
graph TD
    classDef source fill:#d34c4c,stroke:#eee,color:#fff;
    classDef flat fill:#fdcb6e,stroke:#333;
    classDef cache fill:#00b894,stroke:#fff,color:#fff;
    classDef hdfs fill:#0984e3,stroke:#fff,color:#fff;
    
    K1{{Topic: tarot-events Bốc Bài}}:::source -->|Sự kiện Nhanh| S1[Spark Micro-batch 5s]
    K2{{Topic: dbserver1.users Hồ sơ Profile}}:::source -->|Sự kiện Chậm| S2[Spark Topic Listener]
    
    subgraph Data_Flattening [Rã cấu trúc Nested JSON]
        S1 --> E1(1 Event Bốc Bài \nMạng 3 LÁ BÀI)
        E1 -->|Lenh explode| E2(3 Rows Độc lập \nCho mỗi Lá Bài):::flat
        E2 --> E3[Extract user_id = 1, card_name = The Fool]
    end
    
    subgraph Debezium_Payload_Parser [Tiền xử lý chuỗi CDC Thô]
        S2 --> P1(Rút trích Payload \n'after' object)
        P1 --> P2[Loại bỏ Tombstone \nDelete Cột Null]
        P2 --> P3[(In-memory \nUser Cache State)]:::cache
    end
    
    E3 -->|Triggers JOIN| Joiner{LEFT JOIN \ntarot.user_id = user.id}
    P3 -->|Đổ dữ liệu Profile| Joiner
    
    Joiner -->|Handle NULL| Cond{user_id == Null}
    Cond -->|Yes| Guest[Gắn cờ is_anonymous = True \nChừa trống Profile]
    Cond -->|No| Mapper[Dán chồng \nKinh Nghiệm + Tâm Linh \n+ Tổng Số Lượt]
    
    Guest --> Sink[Hadoop Sink]
    Mapper --> Sink
    
    Sink -->|Lưu Trữ Columnar| HDFS[(HDFS Hadoop \nFile .parquet)]:::hdfs
```

**Phân tích Kỹ thuật Đặc Thù (Hardcore Engineering):**
1. **Toán tử `explode()`**: Biến 1 lượt rút 3 lá bài (1 Object duy nhất) thành 3 Rows sự kiện rải phẳng. Điều kiện kiên quyết của Data Engineering nhằm giúp bảng tính BI có thể Count (Đếm) số lần ra mặt của từng lá dễ dàng sau này.
2. **Debezium Tombstone Filtering**: Debezium không nhả Text thuần mà nhả dạng Payload CDC bướu (Tức là cấu trúc `{"before":..., "after":...}`). Spark Codebase đã dùng hàm `.getField("after")` để lấy được trạng thái cuối cùng, đồng thời lọc sạch dòng nào rác (Dòng Xóa bảng Delete).
3. **Left JOIN trên Fast Data Streaming**: Spark phải giữ "Trạng thái bảng Users" dưới dạng Dataframe động dưới Memory. Mỗi khi Event lá bài bay sát qua, nó khớp đúng ID và dán vào thành dòng Parquet khổng lồ gồm cả (Thẻ Bài + Trình độ Xem Bài của Khách). Bất kỳ User nào lật bài nhưng không Đăng nhập qua Postgres, kỹ thuật Left Join vẫn ưu tiên Insert thẻ bài theo danh tính *Ghost/Tombstone*, giúp Hệ thống đạt chuẩn bảo mật Privacy cao.

---
*(Bản tấu Kỹ thuật này bao quát tới 95% sự tinh tế trong Logical Flow của Repository.)*
