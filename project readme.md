# ABBOTT Lead Gen Dashboard

Dashboard phân tích hiệu suất CPL (Cost Per Lead) cho sản phẩm Ensure theo từng platform.

## Tính năng
- Lọc theo Product, Platform, Channel
- Lọc theo khoảng ngày (Date Range)
- Biểu đồ CPL theo ngày và tháng
- Cảnh báo benchmark CPL > $20
- Authentication (đăng nhập bảo mật)

## Cài đặt

pip install -r requirements.txt
```bash


## Chạy local

python app_dash.py
```

Truy cập: http://localhost:8050

**Login:**
- Username: `admin` / Password: `password123`
- Username: `user1` / Password: `mypassword`

## Công nghệ sử dụng
- Python 3.9+
- Dash (Plotly)
- Pandas
- Dash-Auth

## Cấu trúc dự án
abbott-dashboard/
```
├── app_dash.py # File chính chạy dashboard
├── data_processing.py # Xử lý dữ liệu từ Excel
├── dashboard_CPL_daily.csv # Dữ liệu CPL theo ngày
├── dashboard_CPL_monthly.csv # Dữ liệu CPL theo tháng
├── requirements.txt # Danh sách thư viện
├── .gitignore # File loại trừ khi push GitHub
└── README.md # File này

## Tác giả
Vũ Thủy Tiên