import pandas as pd

# === STEP 1: Load dữ liệu từ các sheet ===
excel_file = "ABBOTT _ LEAD GEN DASHBOARD 2024-2025.xlsx"
sheet_names = ["ENS raw data daily Q1", "ENS META daily Q2", "ENS GG daily"]

dfs = []
for sheet in sheet_names:
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet)
        print(f"✅ Đã đọc sheet: {sheet} ({len(df)} dòng)")
        dfs.append(df)
    except Exception as e:
        print(f"❌ Lỗi khi đọc sheet {sheet}: {e}")

if not dfs:
    print("❌ Không có dữ liệu nào được đọc.")
    exit(1)

data = pd.concat(dfs, ignore_index=True)
print(f"📊 Tổng cộng {len(data)} dòng dữ liệu từ tất cả sheet.")

# === STEP 2: Chuẩn hóa cột ngày ===
# Đổi tên cột "Day" thành "Date" cho đồng nhất
if "Day" in data.columns:
    data.rename(columns={"Day": "Date"}, inplace=True)
else:
    print("⚠️ Không tìm thấy cột 'Day' — đảm bảo file có cột này!")

data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
data["Year"] = data["Date"].dt.year
data["Month"] = data["Date"].dt.month

# === STEP 3: Tạo cột phân loại từ UTM Campaign ===
def detect_channel(x):
    if pd.isna(x): return "Other"
    x = str(x).lower()
    if "goo" in x: return "Google"
    elif "fb" in x: return "Facebook"
    return "Other"

def detect_platform(x):
    if pd.isna(x): return "Other"
    x = str(x).lower()
    if "form" in x: return "Lead Form"
    elif "web" in x: return "Lead Web"
    return "Other"

def detect_product(x):
    if pd.isna(x): return "Other"
    x = str(x).lower()
    if "sucfr" in x: return "Sucrose"
    elif "life" in x: return "Life"
    elif "dairy" in x: return "Dairy"
    return "Other"

data["Channel"] = data["UTM Campaign"].apply(detect_channel)
data["Platform"] = data["UTM Campaign"].apply(detect_platform)
data["Product"] = data["UTM Campaign"].apply(detect_product)

# === STEP 4: Tính CPL theo ngày ===
daily_cpl = (
    data.groupby(["Date", "Product", "Channel", "Platform"])
        .agg({"Spend": "sum", "Lead": "sum", "Clicks": "sum", "Impressions": "sum"})
        .reset_index()
)
daily_cpl["CPL"] = daily_cpl["Spend"] / daily_cpl["Lead"].replace(0, 1)
daily_cpl["CTR"] = (daily_cpl["Clicks"] / daily_cpl["Impressions"].replace(0, 1)) * 100
daily_cpl["Conversion_Rate"] = (daily_cpl["Lead"] / daily_cpl["Clicks"].replace(0, 1)) * 100

# === STEP 5: Tính CPL theo tháng ===
monthly_cpl = (
    data.groupby(["Year", "Month", "Product", "Channel", "Platform"])
        .agg({"Spend": "sum", "Lead": "sum", "Clicks": "sum", "Impressions": "sum"})
        .reset_index()
)
monthly_cpl["Avg_CPL"] = monthly_cpl["Spend"] / monthly_cpl["Lead"].replace(0, 1)
monthly_cpl["Avg_CTR"] = (monthly_cpl["Clicks"] / monthly_cpl["Impressions"].replace(0, 1)) * 100

# === STEP 6: Áp dụng benchmark và khuyến nghị ===
BENCHMARK = 20
monthly_cpl["Variance"] = monthly_cpl["Avg_CPL"] - BENCHMARK
monthly_cpl["CPL_Status"] = monthly_cpl["Avg_CPL"].apply(
    lambda x: "Above Benchmark" if x > BENCHMARK else "Below Benchmark"
)

monthly_cpl["CTR_Change"] = monthly_cpl.groupby(
    ["Product", "Channel", "Platform"]
)["Avg_CTR"].pct_change()

def recommend(row):
    if row["Avg_CPL"] <= BENCHMARK:
        return "✓ CPL ổn định - tiếp tục theo dõi"
    if row["CTR_Change"] < -0.10:
        return "⚠️ CTR giảm >10% - cần thay nội dung quảng cáo"
    elif abs(row["CTR_Change"]) <= 0.10:
        return "🎯 CTR ổn định - nên thử nhóm audience mới"
    else:
        return "✓ Theo dõi thêm kỳ tới"

monthly_cpl["Recommendation"] = monthly_cpl.apply(recommend, axis=1)

# === STEP 7: Xuất file CSV cho app Dash hoặc Streamlit ===
daily_cpl.to_csv("dashboard_CPL_daily.csv", index=False)
monthly_cpl.to_csv("dashboard_CPL_monthly.csv", index=False)

print("\n✅ ĐÃ TẠO:")
print(" - dashboard_CPL_daily.csv")
print(" - dashboard_CPL_monthly.csv")
