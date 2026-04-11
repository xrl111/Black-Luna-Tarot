#  Black Luna Tarot - Frontend

Dự án giao diện React dành cho hệ thống Black Luna Tarot AI. 
Giao diện được xây dựng bằng Vite, React 19, TypeScript và Shadcn/UI (Tailwind CSS).

##  Tính năng Giao Diện

- **Giao diện trải nghiệm thân thiện mượt mà**: Hiệu ứng lật thẻ bài, chọn bài được animete bằng `framer-motion`.
- **Text Streaming**: Hiển thị kết quả AI Streaming theo thời gian thực (Giống ChatGPT).
- **Dark Mode / Light Mode**: Hỗ trợ chuyển đổi Theme sáng/tối tự động.
- **Tích hợp Google OAuth2**: Nút đăng nhập bảo mật qua Google để phân biệt quyền Guest và Account.
- **Quản lý Persona (Personalization)**: Trang Settings riêng để định hình phong cách đọc Tarot của AI.
- **Xử lý Error State & Rate Limits**: Tự động hiển thị tin nhắn Toast hoặc Modal khi User bị báo lỗi mã `429 Too Many Requests` (hết lượt dùng).

##  Kiến trúc thư mục Frontend

```
frontend/
├── src/
│   ├── assets/              # Hình ảnh, Fonts, Assets...
│   ├── components/          # UI Components tái sử dụng (Navbar, LLMSettingsModal, ui/* của shadcn).
│   ├── contexts/            # Quản lý Global State (AuthContext - Quản lý JWT Token).
│   ├── lib/                 # Các tiện ích chung (Cấu hình Axios API calls. interceptors).
│   ├── pages/               # Các Route/Trang màn hình lớn (Home, About, Readings, Settings).
│   ├── App.tsx             # Entry Point Router & Providers.
│   └── main.tsx            # React Mount.
├── .env.example             # Biến môi trường mẫu.
├── tailwind.config.js       # Cấu hình UI, màu sắc giao diện.
└── package.json             # Khai báo thư viện (npm).
```

##  Cài đặt & Chạy Local

### 1. Cài đặt thư viện

Bạn cần NodeJS 18+ trở lên.

```bash
npm install
```

### 2. Cấu hình biến môi trường

Tạo file `.env` dựa theo file `.env.example`:

```bash
# Trỏ đến địa chỉ Backend (Ví dụ FastAPI chạy ở cổng 8000)
VITE_API_ORIGIN=http://localhost:8000

# Client ID của Google (Dùng cho chức năng Login phân quyền)
# Lấy từ Google Cloud Console (APIs & Services -> Credentials)
VITE_GOOGLE_CLIENT_ID="thu-tu-chu-so-client.apps.googleusercontent.com"
```

> **Mẹo bypass cho Developer**: Nếu chưa kịp thiết lập `VITE_GOOGLE_CLIENT_ID`, hãy truyền chuỗi: `test-bypass-token` vào mã Code (trong `App.tsx` hoặc `.env`) để test giao diện gọi về Backend bằng tài khoản test nội bộ (Fake Authentication).

### 3. Chạy Server Development

```bash
npm run dev
```

Project sẽ thường xuyên chạy tại `http://localhost:5173`.

##  Biên dịch cho Production

Khi ứng dụng đã sẵn sàng triển khai lên VPS hoặc các nền tảng như Vercel, Netlify, Cloudflare Pages:

```bash
npm run build
```

Biên dịch sẽ xuất ra thư mục `dist/`. Thư mục này là các file tĩnh (HTML, CSS, JS) hoàn toàn có thể được phục vụ bằng Nginx hoặc các loại Web Server Caching.

##  Kiến trúc API Interceptor (Bảo mật JWT)

Trong file `src/lib/api.ts`:
- Tất cả các thao tác GET / POST gửi lên Backend (url: `/api/v1/...`) sẽ được axios tự động `Interceptor` thêm chuỗi Header: `Authorization: Bearer <token_tu_localstorage>`.
- Nếu Backend trả về mã lỗi HTTP 401 (Lỗi Token ớn/ hết hạn), Frontend sẽ tự động đăng xuất.
- Nếu Backend trả về mã lỗi HTTP 429 (Hết lượt đọc Tarot), Frontend sẽ tung Error Message cho hàm Catch hứng và render Popup báo hết hạn mức cho thẻ Account/Guest.

---

> Được tối ưu cho quá trình Luận văn Thạc Sĩ - Black Luna Tarot.
