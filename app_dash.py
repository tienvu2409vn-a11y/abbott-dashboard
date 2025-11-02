import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_auth
import pandas as pd
import plotly.express as px
import secrets

# === DANH SÁCH USER/PASSWORD ===
VALID_USERS = {
    "admin": "password123",
    "user1": "mypassword"
}

# === 1️⃣ Load dữ liệu ===
daily = pd.read_csv("dashboard_CPL_daily.csv")
monthly = pd.read_csv("dashboard_CPL_monthly.csv")

# Đảm bảo định dạng ngày đúng
daily["Date"] = pd.to_datetime(daily["Date"], errors="coerce")

# === 2️⃣ Khởi tạo ứng dụng Dash ===
app = dash.Dash(__name__)
app.server.secret_key = secrets.token_hex(32)  # ← DÒNG MỚI: Tạo secret key tự động
app.title = "ABBOTT Lead Gen Dashboard"

# === BẬT AUTHENTICATION ===
auth = dash_auth.BasicAuth(app, VALID_USERS)

# === 3️⃣ Layout đầy đủ ===
app.layout = html.Div([
    html.H1("Ensure Performance Dashboard (Secured)", 
            style={'textAlign': 'center', 'color': '#1f77b4', 'marginBottom': 30}),
    
    # --- Bộ lọc ---
    html.Div([
        html.Div([
            html.Label("Chọn Product"),
            dcc.Dropdown(
                id="filter-product",
                options=[{"label": i, "value": i} for i in sorted(daily["Product"].unique())],
                value=[],
                multi=True
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '1%'}),
        
        html.Div([
            html.Label("Chọn Platform"),
            dcc.Dropdown(
                id="filter-platform",
                options=[{"label": i, "value": i} for i in sorted(daily["Platform"].unique())],
                value=[],
                multi=True
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '1%'}),
        
        html.Div([
            html.Label("Chọn Channel"),
            dcc.Dropdown(
                id="filter-channel",
                options=[{"label": i, "value": i} for i in sorted(daily["Channel"].unique())],
                value=[],
                multi=True
            )
        ], style={'width': '32%', 'display': 'inline-block'})
    ], style={'padding': 10}),
    
    html.Br(),
    
    # --- Bộ lọc thời gian ---
    html.Div([
        html.Label("Chọn Khoảng Ngày (Date Range):"),
        dcc.DatePickerRange(
            id="filter-date-range",
            min_date_allowed=daily["Date"].min(),
            max_date_allowed=daily["Date"].max(),
            start_date=daily["Date"].min(),
            end_date=daily["Date"].max(),
            display_format="YYYY-MM-DD"
        )
    ], style={'padding': 10}),
    
    html.Hr(),

    # --- Biểu đồ CPL theo ngày ---
    html.H3("Biểu đồ CPL Theo Ngày"),
    dcc.Graph(id="chart-daily-cpl"),
    
    html.Hr(),
    
    # --- Biểu đồ CPL trung bình theo tháng ---
    html.H3("Biểu đồ CPL Trung Bình Theo Tháng"),
    dcc.Graph(id="chart-monthly-cpl"),
    
    html.Hr(),
    
    # --- Cảnh báo benchmark ---
    html.Div(id="benchmark-alert", 
             style={'padding': 20, 'fontSize': 18, 'fontWeight': 'bold'})
])

# === 4️⃣ Callback xử lý filter + hover effect ===
@app.callback(
    [Output("chart-daily-cpl", "figure"),
     Output("chart-monthly-cpl", "figure"),
     Output("benchmark-alert", "children")],
    [Input("filter-product", "value"),
     Input("filter-platform", "value"),
     Input("filter-channel", "value"),
     Input("filter-date-range", "start_date"),
     Input("filter-date-range", "end_date")]
)
def update_dashboard(selected_product, selected_platform, selected_channel,
                     start_date, end_date):

    # --- DAILY filter ---
    filtered_daily = daily.copy()
    if selected_product:
        filtered_daily = filtered_daily[filtered_daily["Product"].isin(selected_product)]
    if selected_platform:
        filtered_daily = filtered_daily[filtered_daily["Platform"].isin(selected_platform)]
    if selected_channel:
        filtered_daily = filtered_daily[filtered_daily["Channel"].isin(selected_channel)]
    filtered_daily = filtered_daily[
        (filtered_daily["Date"] >= start_date) &
        (filtered_daily["Date"] <= end_date)
    ]

    # --- Biểu đồ DAILY ---
    fig_day = px.line(filtered_daily, x="Date", y="CPL", color="Platform",
                      title="CPL theo Ngày", markers=True)
    fig_day.update_traces(
        line=dict(width=2),
        marker=dict(size=8, line=dict(width=1, color="white")),
        hovertemplate="<b>%{x|%d-%b-%Y}</b><br>CPL: <b>$%{y:.2f}</b><extra></extra>",
        opacity=0.85
    )
    fig_day.update_layout(hovermode="x unified", template="plotly_white")

    # --- MONTHLY filter ---
    filtered_monthly = monthly.copy()
    if selected_product:
        filtered_monthly = filtered_monthly[filtered_monthly["Product"].isin(selected_product)]
    if selected_platform:
        filtered_monthly = filtered_monthly[filtered_monthly["Platform"].isin(selected_platform)]
    if selected_channel:
        filtered_monthly = filtered_monthly[filtered_monthly["Channel"].isin(selected_channel)]

    # --- Biểu đồ MONTHLY ---
    fig_month = px.bar(filtered_monthly, x="Month", y="Avg_CPL", color="Platform",
                       title="CPL Trung Bình Theo Tháng", barmode="group")
    fig_month.update_traces(
        hovertemplate="<b>Tháng %{x}</b><br>CPL: <b>$%{y:.2f}</b><extra></extra>",
        marker=dict(line=dict(width=1, color="white")),
        opacity=0.85
    )
    fig_month.update_layout(hovermode="x unified", template="plotly_white")

    # --- BENCHMARK ---
    benchmark = 20
    high_cpl = filtered_monthly[filtered_monthly["Avg_CPL"] > benchmark]
    if not high_cpl.empty:
        msg = f"⚠️ {len(high_cpl)} platform có CPL > ${benchmark}. Cần tối ưu lại chiến dịch."
        alert_color = "red"
    else:
        msg = f"✅ Tất cả platform CPL ≤ ${benchmark}. Hiệu suất ổn định."
        alert_color = "green"

    alert = html.Div(msg, style={"color": alert_color, "fontWeight": "bold"})
    return fig_day, fig_month, alert

# === 5️⃣ Chạy app ===
if __name__ == "__main__":
    app.run(debug=True, port=8050)
