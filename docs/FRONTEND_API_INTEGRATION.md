#  Tài Liệu Dành Cho Frontend: Tích hợp Google Auth & Phân Quyền Guest/Account

Tài liệu này hướng dẫn cách giao tiếp với các Endpoints mới phục vụ cho mục tiêu **Giới hạn lượt dùng** và **Cá nhân hóa (Personalization)**.

Mô hình hệ thống chia rẽ 2 loại trải nghiệm:
- **Guest (Miễn phí):** Dùng IP, tối đa 3 lượt/ngày, bắt buộc dùng Model Offline, không thể cá nhân hóa tính cách AI.
- **Account (Đăng nhập Google):** Dùng JWT, tối đa 20 lượt/ngày, có thể tinh chỉnh Persona của AI Rider.

---

## 1. Luồng Tích hợp Google Sign-in

### Bước 1: Lấy `id_token` từ Google
Sử dụng thư viện phổ biến ở Frontend (như `@react-oauth/google` cho React, hoặc JS SDK) để hiện popup đăng nhập tài khoản Google. Kết quả trả về cho Frontend sẽ là một đối tượng chứa `credential` (chính là JWT gốc chữ ký Google).

### Bước 2: Đổi Token lên Backend
Gửi token đó lên hệ thống Backend bằng API mới:

**`POST /api/v1/auth/google`**  
- **Body:** 
  ```json
  {
    "id_token": "chuỗi_credential_từ_google_trả_về"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI...", 
    "token_type": "bearer",
    "user": {
      "email": "user@gmail.com",
      "name": "Alex"
    }
  }
  ```
*(Hệ thống Backend sẽ tự động kiểm tra, tạo tài khoản mới nếu chưa tồn tại, và khởi tạo 1 file `UserPreferences` trống rỗng cho sau này).*

### Bước 3: Gọi API tiếp theo với Token
Kể từ bây giờ, mọi API muốn nhận diện User đều phải kẹp thêm Header:
```http
Authorization: Bearer <chuỗi_access_token>
```

*(Lưu ý: Môi trường Localhost testing. Nếu chưa thiết lập Key từ Google Cloud, bạn có thể truyền thẳng chuỗi `"test-bypass-token"` vào biến `id_token` để lách luật test thử API).*

---

## 2. API Cập Nhật Preferences & Xem Thông Tin Account

*Ghi chú: API này sẽ phục vụ cho trang "Settings / Personalization" ở phía giao diện Frontend.*

Việc gọi API bắt buộc phải kèm Token JWT ở `Authorization` Header. Khi có JWT, hệ thống sẽ biết đích xác mình đang làm việc với ai.

**`GET /api/v1/users/me`**  *(Đề xuất: Chờ code)*
- **Chức năng:** Tải về thông tin Avatar, Email, và thông tin `UserPreferences` bao gồm *Tone, Phong cách đọc, Trình độ*.
  
**`PUT /api/v1/users/me/preferences`** *(Đề xuất: Chờ code)*
- **Chức năng:** Cập nhật lại Role-play cho AI, ví dụ truyền lên:
  ```json
  {
    "reading_style": "detailed",
    "tone": "empathetic",
    "experience_level": "beginner"
  }
  ```

---

## 3. Tạo Quẻ Bài Tarot (Tích hợp Tier Limits)
Endpoint cũ `POST /api/v1/readings/` đã được thông minh hóa để chia làm 2 nhánh, hoàn toàn trong suốt với Client.

### Khi Gọi Không Có Token (Nhánh Guest)
- **Hành vi:** Hệ thống thu thập địa chỉ `IP`.
- **Nếu vượt quá 3 lần/ngày**, Backend sẽ trả về lỗi:
  ```json
  // HTTP 429 Too Many Requests
  "Daily quota exceeded. Limit is 3 readings per day for Guest users."
  ```
- **Giới hạn tính năng:** Bất kể bạn nhét `ai_model_used` là `gpt-4` hay truyền `user_context` (Cá nhân hóa) từ phía Client, Backend sẽ **tự động cắt bỏ** và ép Model thành mặc định (`qwen2.5:1.5b`).

### Khi Gọi Có Cài Token (Nhánh Account)
- **Hành vi:** Hệ thống sử dụng ID trong DB của User để đếm (chứ không đếm IP). Quota nâng lên thành **20 lần/ngày**.
- **Tính năng được Unlock:** Backend sẽ bảo lưu 100% Payload từ Frontend đẩy lên. Nếu bạn có config `user_context: { ... }` hoặc đổi mô hình, Backend sẽ tôn trọng và đưa vào `ai_service` để AI đọc giọng điệu mới.

---

### Mẹo Xử Lý Mã Lỗi Từ Frontend:
| Status Code | Xử Lý Phía UI (Frontend) |
|-------------|----------------------------|
| **401 Unauthorized** | Token đã hết hạn / Sai token. Frontend tự động Logout người dùng và đá về trang Login. |
| **429 Too Many Requests** | Hiện Popup: *"Bạn đã dùng hết lượt đọc bài trong ngày! Hãy Đăng Nhập bằng Google (nếu đang là Guest) hoặc Đợi đến ngày mai (nếu đã đăng nhập)."* |
| **403 Forbidden** | *(Tuỳ chọn)* Cấm truy cập tính năng Premium. Hiện nút: *"Nâng cấp tài khoản hoặc Đăng nhập"*. |
