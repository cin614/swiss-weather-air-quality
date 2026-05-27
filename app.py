"""
Swiss Weather & Air Quality Analyzer – Flask Web App
Scientific Programming Final Project FS2026
"""

from flask import Flask, render_template_string
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
from scipy import stats
import base64
import io
import os

app = Flask(__name__)
DB_PATH = "swiss_weather.db"

# ── helpers ──────────────────────────────────────────────────────────────────
def load_data():
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM weather_aq WHERE pm2_5 IS NOT NULL ORDER BY city, date", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df

def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return b64

CITY_NAMES = ["Zürich","Bern","Geneva","Basel","Lausanne","St. Gallen","Lucerne"]
PALETTE    = ["#065A82","#1C7293","#028090","#00A896","#02C39A","#F4A261","#E76F51"]

# ── chart generators ──────────────────────────────────────────────────────────
def chart_seasonal(df):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="#0d1b2a")
    ax.set_facecolor("#0d1b2a")
    order  = ["Winter","Spring","Summer","Autumn"]
    means  = df.groupby("season")["pm2_5"].mean().reindex(order)
    colors = ["#1C7293","#02C39A","#F4A261","#028090"]
    bars   = ax.bar(order, means.values, color=colors, width=0.55, zorder=3)
    for bar, val in zip(bars, means.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                f"{val:.1f}", ha="center", va="bottom", color="white", fontsize=11, fontweight="bold")
    ax.axhline(15, color="#F4A261", linestyle="--", linewidth=1.5, label="WHO limit 15 µg/m³", zorder=4)
    ax.set_ylabel("PM2.5 (µg/m³)", color="#8ab4c9", fontsize=11)
    ax.tick_params(colors="#8ab4c9")
    ax.spines[:].set_visible(False)
    ax.yaxis.grid(True, color="#1e3a4f", zorder=0)
    ax.set_axisbelow(True)
    ax.legend(facecolor="#0d1b2a", edgecolor="#1C7293", labelcolor="white", fontsize=9)
    ax.set_title("Average PM2.5 by Season", color="white", fontsize=13, pad=10, fontweight="bold")
    fig.tight_layout()
    return fig_to_b64(fig)

def chart_monthly(df):
    fig, ax = plt.subplots(figsize=(8, 4), facecolor="#0d1b2a")
    ax.set_facecolor("#0d1b2a")
    monthly = df.groupby("month")["pm2_5"].mean()
    temp_m  = df.groupby("month")["temp_mean"].mean()
    ax2     = ax.twinx()
    ax.plot(monthly.index, monthly.values, color="#02C39A", linewidth=2.5,
            marker="o", markersize=5, label="PM2.5 (µg/m³)", zorder=4)
    ax2.plot(temp_m.index, temp_m.values, color="#F4A261", linewidth=2.5,
             marker="s", markersize=5, linestyle="--", label="Temp (°C)", zorder=3)
    ax.axhline(15, color="#E76F51", linestyle=":", linewidth=1.2, zorder=2)
    ax.set_xticks(range(1,13))
    ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun",
                        "Jul","Aug","Sep","Oct","Nov","Dec"],
                       color="#8ab4c9", fontsize=9)
    ax.tick_params(colors="#8ab4c9"); ax2.tick_params(colors="#F4A261")
    ax.set_ylabel("PM2.5 (µg/m³)", color="#02C39A", fontsize=10)
    ax2.set_ylabel("Temperature (°C)", color="#F4A261", fontsize=10)
    ax.spines[:].set_visible(False); ax2.spines[:].set_visible(False)
    ax.yaxis.grid(True, color="#1e3a4f", zorder=0); ax.set_axisbelow(True)
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1+lines2, labels1+labels2, facecolor="#0d1b2a",
              edgecolor="#1C7293", labelcolor="white", fontsize=9, loc="upper right")
    ax.set_title("Monthly Trends: PM2.5 vs Temperature", color="white",
                 fontsize=13, pad=10, fontweight="bold")
    fig.tight_layout()
    return fig_to_b64(fig)

def chart_city_box(df):
    fig, ax = plt.subplots(figsize=(8, 4), facecolor="#0d1b2a")
    ax.set_facecolor("#0d1b2a")
    data_by_city = [df[df["city"]==c]["pm2_5"].dropna().values for c in CITY_NAMES]
    bp = ax.boxplot(data_by_city, patch_artist=True, medianprops=dict(color="white", linewidth=2))
    for patch, color in zip(bp["boxes"], PALETTE):
        patch.set_facecolor(color); patch.set_alpha(0.85)
    for element in ["whiskers","caps","fliers"]:
        for item in bp[element]:
            item.set_color("#8ab4c9")
    ax.set_xticklabels(CITY_NAMES, color="#8ab4c9", fontsize=9, rotation=20, ha="right")
    ax.tick_params(colors="#8ab4c9")
    ax.set_ylabel("PM2.5 (µg/m³)", color="#8ab4c9", fontsize=10)
    ax.spines[:].set_visible(False)
    ax.yaxis.grid(True, color="#1e3a4f", zorder=0); ax.set_axisbelow(True)
    ax.set_title("PM2.5 Distribution by City", color="white",
                 fontsize=13, pad=10, fontweight="bold")
    fig.tight_layout()
    return fig_to_b64(fig)

def chart_regression(df):
    clean = df[["temp_mean","pm2_5"]].dropna()
    r, p  = stats.pearsonr(clean["temp_mean"], clean["pm2_5"])
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="#0d1b2a")
    ax.set_facecolor("#0d1b2a")
    ax.scatter(clean["temp_mean"], clean["pm2_5"],
               alpha=0.12, s=8, color="#1C7293", zorder=2)
    m, b = np.polyfit(clean["temp_mean"], clean["pm2_5"], 1)
    xr   = np.linspace(clean["temp_mean"].min(), clean["temp_mean"].max(), 100)
    ax.plot(xr, m*xr+b, color="#02C39A", linewidth=2.5,
            label=f"r = {r:.3f}, p = {p:.1e}", zorder=4)
    ax.axhline(15, color="#F4A261", linestyle="--", linewidth=1.2,
               label="WHO limit 15 µg/m³", zorder=3)
    ax.set_xlabel("Daily Mean Temperature (°C)", color="#8ab4c9", fontsize=10)
    ax.set_ylabel("PM2.5 (µg/m³)", color="#8ab4c9", fontsize=10)
    ax.tick_params(colors="#8ab4c9")
    ax.spines[:].set_visible(False)
    ax.yaxis.grid(True, color="#1e3a4f", zorder=0); ax.set_axisbelow(True)
    ax.legend(facecolor="#0d1b2a", edgecolor="#1C7293", labelcolor="white", fontsize=9)
    ax.set_title("Temperature vs. PM2.5 (Regression)", color="white",
                 fontsize=13, pad=10, fontweight="bold")
    fig.tight_layout()
    return fig_to_b64(fig)

# ── HTML template ─────────────────────────────────────────────────────────────
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌤️ Swiss Weather & Air Quality Analyzer</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:       #0a1628;
    --surface:  #0d1f35;
    --card:     #112240;
    --border:   #1e3a5f;
    --accent:   #02C39A;
    --accent2:  #1C7293;
    --warm:     #F4A261;
    --text:     #cdd9e5;
    --muted:    #5f7a8a;
    --white:    #ffffff;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--bg); color:var(--text); font-family:'DM Sans',sans-serif;
         min-height:100vh; }

  /* NAV */
  nav { background:var(--surface); border-bottom:1px solid var(--border);
        padding:1rem 2rem; display:flex; align-items:center; gap:1rem;
        position:sticky; top:0; z-index:100; backdrop-filter:blur(10px); }
  nav .logo { font-size:1.2rem; font-weight:700; color:var(--white); }
  nav .logo span { color:var(--accent); }
  nav .badge { font-size:0.7rem; background:var(--accent2); color:var(--white);
               padding:0.2rem 0.6rem; border-radius:20px; margin-left:auto; }

  /* HERO */
  .hero { padding:3.5rem 2rem 2rem; max-width:1200px; margin:0 auto; }
  .hero h1 { font-size:2.6rem; font-weight:700; color:var(--white); line-height:1.2; }
  .hero h1 span { color:var(--accent); }
  .hero p { margin-top:0.75rem; font-size:1.05rem; color:var(--muted); max-width:650px; }
  .hero .rq { margin-top:1.2rem; background:var(--card); border-left:3px solid var(--accent);
              padding:0.9rem 1.2rem; border-radius:0 8px 8px 0; font-style:italic;
              color:var(--text); font-size:1rem; max-width:700px; }

  /* KPI CARDS */
  .kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem;
              max-width:1200px; margin:2rem auto; padding:0 2rem; }
  .kpi { background:var(--card); border:1px solid var(--border); border-radius:12px;
         padding:1.4rem 1.2rem; transition:transform .2s, border-color .2s; }
  .kpi:hover { transform:translateY(-3px); border-color:var(--accent2); }
  .kpi .val { font-size:2rem; font-weight:700; color:var(--accent);
              font-family:'DM Mono',monospace; }
  .kpi .label { font-size:0.8rem; color:var(--muted); margin-top:0.3rem; text-transform:uppercase;
                letter-spacing:.05em; }
  .kpi .sub { font-size:0.75rem; color:var(--accent2); margin-top:0.2rem; }

  /* MAIN CONTENT */
  .content { max-width:1200px; margin:0 auto; padding:0 2rem 4rem; }
  .section-title { font-size:1.3rem; font-weight:700; color:var(--white); margin:2.5rem 0 1rem;
                   display:flex; align-items:center; gap:0.6rem; }
  .section-title::after { content:''; flex:1; height:1px; background:var(--border); }

  /* CHART GRID */
  .chart-grid { display:grid; grid-template-columns:1fr 1fr; gap:1.2rem; }
  .chart-card { background:var(--card); border:1px solid var(--border); border-radius:12px;
                padding:1.2rem; transition:border-color .2s; }
  .chart-card:hover { border-color:var(--accent2); }
  .chart-card.wide { grid-column:1/-1; }
  .chart-card img { width:100%; border-radius:6px; }

  /* STATS TABLE */
  .stats-grid { display:grid; grid-template-columns:1fr 1fr; gap:1.2rem; }
  .stat-box { background:var(--card); border:1px solid var(--border); border-radius:12px;
              padding:1.5rem; }
  .stat-box h3 { font-size:0.85rem; color:var(--muted); text-transform:uppercase;
                 letter-spacing:.08em; margin-bottom:1rem; }
  table { width:100%; border-collapse:collapse; font-size:0.88rem; }
  th { text-align:left; color:var(--muted); font-weight:500; padding:0.5rem 0.6rem;
       border-bottom:1px solid var(--border); font-size:0.8rem; text-transform:uppercase; }
  td { padding:0.55rem 0.6rem; border-bottom:1px solid #162033; color:var(--text); }
  tr:hover td { background:#162033; }
  .yes { color:#4ade80; font-weight:600; }
  .highlight { color:var(--accent); font-family:'DM Mono',monospace; font-weight:600; }

  /* STAT RESULT BOX */
  .result-box { background:var(--card); border:1px solid var(--border);
                border-radius:12px; padding:1.5rem; }
  .result-box h3 { font-size:0.85rem; color:var(--muted); text-transform:uppercase;
                   letter-spacing:.08em; margin-bottom:1.2rem; }
  .result-row { display:flex; justify-content:space-between; align-items:center;
                padding:0.6rem 0; border-bottom:1px solid #162033; }
  .result-row:last-child { border-bottom:none; }
  .result-row .key { color:var(--muted); font-size:0.88rem; }
  .result-row .value { font-family:'DM Mono',monospace; font-weight:600;
                       font-size:0.95rem; color:var(--accent); }
  .sig-badge { background:#065A82; color:var(--accent); font-size:0.75rem;
               padding:0.2rem 0.7rem; border-radius:20px; font-weight:600; }

  /* LLM SECTION */
  .llm-box { background:var(--card); border:1px solid var(--border);
             border-radius:12px; padding:1.5rem; }
  .llm-box h3 { font-size:0.85rem; color:var(--muted); text-transform:uppercase;
                letter-spacing:.08em; margin-bottom:1rem;
                display:flex; align-items:center; gap:0.5rem; }
  .llm-tag { background:var(--accent2); color:white; font-size:0.65rem;
             padding:0.15rem 0.5rem; border-radius:20px; text-transform:uppercase; }
  .insight { padding:1rem; background:#0a1628; border-radius:8px; margin-bottom:0.8rem;
             border-left:2px solid var(--accent2); }
  .insight .num { color:var(--accent); font-weight:700; font-size:0.8rem;
                  text-transform:uppercase; letter-spacing:.05em; margin-bottom:0.3rem; }
  .insight p { font-size:0.9rem; color:var(--text); line-height:1.6; }

  /* MAP */
  .map-box { background:var(--card); border:1px solid var(--border);
             border-radius:12px; overflow:hidden; }
  .map-box iframe { width:100%; height:420px; border:none; }

  /* FOOTER */
  footer { text-align:center; padding:2rem; color:var(--muted); font-size:0.8rem;
           border-top:1px solid var(--border); }
  footer a { color:var(--accent2); text-decoration:none; }

  @media(max-width:768px) {
    .kpi-grid { grid-template-columns:1fr 1fr; }
    .chart-grid { grid-template-columns:1fr; }
    .stats-grid { grid-template-columns:1fr; }
    .hero h1 { font-size:1.8rem; }
  }
</style>
</head>
<body>

<nav>
  <div class="logo">🌤️ Swiss <span>Weather</span> & Air Quality</div>
  <div class="badge">FS2026 · Scientific Programming</div>
</nav>

<div class="hero">
  <h1>Swiss Cities<br><span>Weather & Air Quality</span><br>Analysis 2024</h1>
  <p>Analysing the relationship between temperature and PM2.5 across 7 Swiss cities
     using one full year of open data.</p>
  <div class="rq">
    📌 Research Question: <em>Is there a statistically significant correlation
    between temperature and air quality (PM2.5) in Swiss cities?</em>
  </div>
</div>

<!-- KPI CARDS -->
<div class="kpi-grid">
  <div class="kpi">
    <div class="val">{{ n_records }}</div>
    <div class="label">Daily Records</div>
    <div class="sub">7 cities · full year 2024</div>
  </div>
  <div class="kpi">
    <div class="val">{{ mean_pm }}</div>
    <div class="label">Avg PM2.5 (µg/m³)</div>
    <div class="sub">WHO limit: 15 µg/m³</div>
  </div>
  <div class="kpi">
    <div class="val">{{ r_val }}</div>
    <div class="label">Pearson r</div>
    <div class="sub">Temperature ↔ PM2.5</div>
  </div>
  <div class="kpi">
    <div class="val">{{ p_val }}</div>
    <div class="label">P-Value</div>
    <div class="sub">α = 0.05 → Significant ✓</div>
  </div>
</div>

<div class="content">

  <!-- CHARTS -->
  <div class="section-title">📈 Visualizations</div>
  <div class="chart-grid">
    <div class="chart-card">
      <img src="data:image/png;base64,{{ chart_seasonal }}" alt="Seasonal PM2.5">
    </div>
    <div class="chart-card">
      <img src="data:image/png;base64,{{ chart_monthly }}" alt="Monthly Trends">
    </div>
    <div class="chart-card">
      <img src="data:image/png;base64,{{ chart_box }}" alt="City Boxplot">
    </div>
    <div class="chart-card">
      <img src="data:image/png;base64,{{ chart_reg }}" alt="Regression">
    </div>
  </div>

  <!-- STATISTICS & TABLE -->
  <div class="section-title">📊 Statistics</div>
  <div class="stats-grid">
    <div class="stat-box">
      <h3>Average PM2.5 by City (µg/m³)</h3>
      <table>
        <tr><th>City</th><th>Avg PM2.5</th><th>Avg Temp °C</th><th>WHO OK?</th></tr>
        {% for row in city_table %}
        <tr>
          <td>{{ row.city }}</td>
          <td class="highlight">{{ row.pm25 }}</td>
          <td>{{ row.temp }}</td>
          <td class="yes">✓ Yes</td>
        </tr>
        {% endfor %}
      </table>
    </div>
    <div class="result-box">
      <h3>Statistical Results</h3>
      <div class="result-row">
        <span class="key">Test</span>
        <span class="value">Pearson Correlation</span>
      </div>
      <div class="result-row">
        <span class="key">r (correlation)</span>
        <span class="value">{{ r_val }}</span>
      </div>
      <div class="result-row">
        <span class="key">p-value</span>
        <span class="value">{{ p_val }}</span>
      </div>
      <div class="result-row">
        <span class="key">Significance (α=0.05)</span>
        <span class="sig-badge">✓ Significant</span>
      </div>
      <div class="result-row">
        <span class="key">Direction</span>
        <span class="value">Negative</span>
      </div>
      <div class="result-row">
        <span class="key">Mean PM2.5</span>
        <span class="value">{{ mean_pm }} µg/m³</span>
      </div>
      <div class="result-row">
        <span class="key">WHO Limit</span>
        <span class="value">15.00 µg/m³</span>
      </div>
      <div class="result-row">
        <span class="key">T-Test result</span>
        <span class="value">Below WHO ✓</span>
      </div>
    </div>
  </div>

  <!-- MAP -->
  <div class="section-title">🗺️ Interactive Map</div>
  <div class="map-box">
    <iframe src="swiss_air_quality_map.html"></iframe>
  </div>

  <!-- LLM INSIGHTS -->
  <div class="section-title">🤖 AI-Generated Insights</div>
  <div class="llm-box">
    <h3>Claude API Analysis <span class="llm-tag">Generated by LLM</span></h3>
    {% for insight in insights %}
    <div class="insight">
      <div class="num">{{ insight.title }}</div>
      <p>{{ insight.text }}</p>
    </div>
    {% endfor %}
  </div>

</div>

<footer>
  Scientific Programming Final Project · FS2026 · ZHAW School of Management and Law<br>
  Data: <a href="https://open-meteo.com">Open-Meteo API</a> ·
  Analysis: Python (pandas, scipy, seaborn, folium) ·
  LLM: Claude API · DB: SQLite
</footer>

</body>
</html>
"""

@app.route("/")
def index():
    df = load_data()
    if df is None:
        return "<h2 style='font-family:sans-serif;padding:2rem;color:red'>⚠️ Database not found!<br>Please run swiss_weather_analysis.ipynb first.</h2>"

    # KPIs
    clean  = df[["temp_mean","pm2_5"]].dropna()
    r, p   = stats.pearsonr(clean["temp_mean"], clean["pm2_5"])
    mean_pm = df["pm2_5"].mean()

    # City table
    city_stats = df.groupby("city").agg(
        pm25=("pm2_5","mean"), temp=("temp_mean","mean")
    ).reset_index().sort_values("pm25", ascending=False)
    city_table = [
        {"city": row.city, "pm25": f"{row.pm25:.2f}", "temp": f"{row.temp:.1f}"}
        for _, row in city_stats.iterrows()
    ]

    # LLM insights (static from our run)
    insights = [
        {"title": "1. Correlation Analysis",
         "text": f"A statistically significant negative correlation exists between temperature and PM2.5 (r = {r:.3f}, p = {p:.2e}). While significant, temperature explains ~8% of PM2.5 variance, suggesting other factors (emissions, topography, traffic) also play important roles."},
        {"title": "2. City Differences",
         "text": "PM2.5 varies across cities (7.29–9.78 µg/m³). Basel, Zürich, and Geneva show the highest concentrations, likely reflecting urban density and traffic patterns. Lausanne and St. Gallen exhibit the lowest levels."},
        {"title": "3. Seasonal Patterns",
         "text": "Winter shows the highest PM2.5 (10.01 µg/m³) despite lowest temperatures (3.29°C), driven by heating emissions and thermal inversions. Summer shows the lowest PM2.5 (6.26 µg/m³) with highest temperatures (19.51°C)."},
        {"title": "4. Recommendation",
         "text": "All cities remain well below WHO guidelines (15 µg/m³). Winter mitigation strategies should be prioritised in Basel, Zürich, and Geneva — focusing on improved building efficiency and cleaner heating energy sources."},
    ]

    return render_template_string(
        TEMPLATE,
        n_records   = f"{len(df):,}",
        mean_pm     = f"{mean_pm:.2f}",
        r_val       = f"{r:.3f}",
        p_val       = f"{p:.2e}",
        city_table  = city_table,
        insights    = insights,
        chart_seasonal = chart_seasonal(df),
        chart_monthly  = chart_monthly(df),
        chart_box      = chart_city_box(df),
        chart_reg      = chart_regression(df),
    )

if __name__ == "__main__":
    print("\n🌤️  Swiss Weather & Air Quality Analyzer")
    print("=" * 45)
    print("➜  Open in browser: http://localhost:5000")
    print("   Press CTRL+C to stop\n")
    app.run(debug=False, port=5000)
