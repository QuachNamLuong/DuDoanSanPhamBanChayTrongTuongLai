# 🚀 FastAPI Project – uv + Uvicorn + MySQL

Project sử dụng **FastAPI**, quản lý dependency bằng **uv (package manager)**,
cấu hình môi trường với **.env**, và chạy server bằng **uvicorn**.

---

## ⚡ Cài đặt uv (Python package manager)

Tài liệu chính thức của uv:
👉 [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

### Cài đặt uv bằng pip

```bash
pip install uv
```

### Kiểm tra phiên bản uv

```bash
uv --version
```

---

## 📁 Vào thư mục project

```bash
cd ./DuDoanSanPhamBanChayTrongTuongLai
```

---

## 📦 Cài đặt & cập nhật các package

Cài đặt toàn bộ dependency từ `pyproject.toml` bằng uv:

```bash
uv sync
```

---

## 🔐 Thiết lập biến môi trường (.env)

Tạo file `.env` tại **thư mục gốc của project** với nội dung sau:

```env
# Database MYSQL
DB_USER=root
DB_PASSWORD=root123
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smarthome_db
```

---

## ▶️ Chạy project

Chạy FastAPI bằng uvicorn thông qua uv:

```bash
uv run uvicorn app.main:app
```

### Chạy với chế độ reload (development)

```bash
uv run uvicorn app.main:app --reload
```

---

## ✅ TL;DR

```bash
pip install uv
cd ./DuDoanSanPhamBanChayTrongTuongLai
uv sync
uv run uvicorn app.main:app --reload
```
