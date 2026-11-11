"""Analisis statistik dataset Premier League 2006/07–2017/18.
Jalankan dari folder proyek dengan: python analysis.py
Hasil tabel disimpan ke outputs/tables dan grafik ke outputs/figures.
"""
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Aman untuk menjalankan skrip dari terminal VS Code.
import matplotlib.pyplot as plt
import seaborn as sns

try:
    import plotly.express as px
except ImportError:
    px = None

warnings.filterwarnings("ignore", category=FutureWarning)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TABLE_DIR = BASE_DIR / "outputs" / "tables"
FIGURE_DIR = BASE_DIR / "outputs" / "figures"
TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook", font_scale=1.0)
plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "axes.titleweight": "bold",
    "axes.titlesize": 15,
    "axes.labelsize": 11,
    "font.family": "DejaVu Sans",
})

# -----------------------------------------------------------------------------
# 1. MEMBACA DATA
# -----------------------------------------------------------------------------
stats = pd.read_csv(DATA_DIR / "stats.csv")
results = pd.read_csv(DATA_DIR / "results.csv")

# Merapikan spasi dan format kategori; nilai numerik tidak diubah menjadi nol.
for col in ["team", "season"]:
    stats[col] = stats[col].astype("string").str.strip()
for col in ["home_team", "away_team", "season"]:
    results[col] = results[col].astype("string").str.strip()
results["result"] = results["result"].astype("string").str.strip().str.upper()

# -----------------------------------------------------------------------------
# 2. PEMERIKSAAN DAN CLEANING RINGAN
# -----------------------------------------------------------------------------
# Dataset yang diperiksa tidak memiliki baris duplikat maupun duplikat klub-musim.
# drop_duplicates tetap disediakan sebagai perlindungan bila sumber berubah.
stats = stats.drop_duplicates(subset=["team", "season"]).copy()
results = results.drop_duplicates().copy()

missing_summary = pd.DataFrame({
    "kolom": stats.columns,
    "jumlah_missing": [stats[c].isna().sum() for c in stats.columns],
    "persentase_missing": [stats[c].isna().mean() * 100 for c in stats.columns],
})
missing_summary = missing_summary[missing_summary["jumlah_missing"] > 0]
missing_summary.to_csv(TABLE_DIR / "missing_values_stats.csv", index=False)

# Memeriksa konsistensi label H/D/A terhadap skor aktual.
expected_result = pd.Series(
    np.where(results["home_goals"] > results["away_goals"], "H",
             np.where(results["home_goals"] == results["away_goals"], "D", "A")),
    index=results.index,
)
result_mismatches = int((results["result"] != expected_result).sum())

# Ringkasan kualitas data.
overview = pd.DataFrame({
    "dataset": ["stats.csv", "results.csv"],
    "jumlah_baris": [len(stats), len(results)],
    "jumlah_kolom": [stats.shape[1], results.shape[1]],
    "duplikat_baris_atau_kunci": [int(stats.duplicated(["team", "season"]).sum()), int(results.duplicated().sum())],
    "jumlah_missing": [int(stats.isna().sum().sum()), int(results.isna().sum().sum())],
})
overview.to_csv(TABLE_DIR / "data_overview.csv", index=False)

# -----------------------------------------------------------------------------
# 3. ANALISIS UNIVARIAT: STATISTIK KLUB PER MUSIM (stats.csv)
# -----------------------------------------------------------------------------
numeric_cols = stats.select_dtypes(include="number").columns.tolist()
descriptive = stats[numeric_cols].describe().T
# Tambahkan median, modus, dan skewness agar tabel lebih lengkap.
descriptive["median"] = stats[numeric_cols].median()
descriptive["mode"] = [
    stats[c].mode(dropna=True).iloc[0] if not stats[c].mode(dropna=True).empty else np.nan
    for c in numeric_cols
]
descriptive["skewness"] = stats[numeric_cols].skew()
descriptive = descriptive.rename(columns={
    "count": "jumlah_data", "mean": "mean", "std": "std_dev",
    "min": "minimum", "25%": "Q1", "50%": "Q2_median",
    "75%": "Q3", "max": "maksimum"
})
descriptive.to_csv(TABLE_DIR / "statistik_deskriptif_semua_variabel.csv", float_format="%.4f")

# Statistik kuartil, desil, dan persentil jumlah gol.
goals = stats["goals"].dropna()
quantile_probs = sorted(set([0.10, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.90]))
quantile_table = pd.DataFrame({
    "probabilitas": quantile_probs,
    "ukuran": [
        "P10", "D2", "Q1", "D3", "D4", "Q2 / D5", "D6", "D7", "Q3", "D8", "D9"
    ],
    "nilai_jumlah_gol": [goals.quantile(q) for q in quantile_probs],
})
quantile_table.to_csv(TABLE_DIR / "kuartil_desil_persentil_goals.csv", index=False, float_format="%.3f")

# Grafik 1: Histogram distribusi jumlah gol.
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(goals, bins=15, kde=True, color="#287D5A", edgecolor="white", linewidth=0.8, ax=ax)
ax.axvline(goals.mean(), color="#D97706", linestyle="--", linewidth=2, label=f"Mean = {goals.mean():.2f}")
ax.axvline(goals.median(), color="#2563EB", linestyle=":", linewidth=2, label=f"Median = {goals.median():.2f}")
ax.set(title="Distribusi Jumlah Gol Klub per Musim", xlabel="Jumlah gol dalam satu musim", ylabel="Frekuensi klub-musim")
ax.legend(frameon=True)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "01_histogram_distribusi_gol.png", bbox_inches="tight")
plt.close(fig)

# Grafik 2: Boxplot jumlah gol.
fig, ax = plt.subplots(figsize=(10, 3.8))
sns.boxplot(x=goals, color="#70B8A0", width=0.45, ax=ax)
ax.set(title="Sebaran Jumlah Gol Klub per Musim", xlabel="Jumlah gol")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "02_boxplot_jumlah_gol.png", bbox_inches="tight")
plt.close(fig)

# Grafik 3: 10 klub-musim dengan gol terbanyak.
top10 = stats.nlargest(10, "goals").copy()
top10["label"] = top10["team"] + " (" + top10["season"].str[-4:] + ")"
top10 = top10.sort_values("goals", ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=top10, x="goals", y="label", color="#287D5A", ax=ax)
for container in ax.containers:
    ax.bar_label(container, fmt="%.0f", padding=4, fontsize=9)
ax.set(title="10 Klub-Musim dengan Jumlah Gol Terbanyak", xlabel="Jumlah gol", ylabel="Klub dan musim")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "03_top10_jumlah_gol.png", bbox_inches="tight")
plt.close(fig)
top10[["team", "season", "goals"]].sort_values("goals", ascending=False).to_csv(TABLE_DIR / "top10_jumlah_gol.csv", index=False)

# -----------------------------------------------------------------------------
# 4. ANALISIS UNIVARIAT: HASIL PERTANDINGAN (results.csv)
# -----------------------------------------------------------------------------
result_labels = {"H": "Menang kandang", "D": "Seri", "A": "Menang tandang"}
result_counts = results["result"].value_counts().reindex(["H", "D", "A"], fill_value=0)
result_summary = pd.DataFrame({
    "hasil": [result_labels[k] for k in ["H", "D", "A"]],
    "jumlah": result_counts.values,
    "persentase": (result_counts / len(results) * 100).values,
})
result_summary.to_csv(TABLE_DIR / "distribusi_hasil_pertandingan.csv", index=False, float_format="%.4f")

fig, ax = plt.subplots(figsize=(8.5, 5.5))
sns.barplot(data=result_summary, x="hasil", y="jumlah", color="#287D5A", ax=ax)
for container in ax.containers:
    ax.bar_label(container, fmt="%.0f", padding=4)
ax.set(title="Distribusi Hasil 4.560 Pertandingan", xlabel="Hasil pertandingan", ylabel="Jumlah pertandingan")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "04_distribusi_hasil_pertandingan.png", bbox_inches="tight")
plt.close(fig)

home_away_summary = pd.DataFrame({
    "jenis": ["Gol kandang", "Gol tandang"],
    "total_gol": [results["home_goals"].sum(), results["away_goals"].sum()],
    "rata_rata_per_laga": [results["home_goals"].mean(), results["away_goals"].mean()],
    "median_per_laga": [results["home_goals"].median(), results["away_goals"].median()],
})
home_away_summary.to_csv(TABLE_DIR / "perbandingan_gol_kandang_tandang.csv", index=False, float_format="%.4f")

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=home_away_summary, x="jenis", y="rata_rata_per_laga", color="#287D5A", ax=ax)
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", padding=4)
ax.set(title="Rata-rata Gol Kandang dan Tandang per Pertandingan", xlabel="Jenis gol", ylabel="Rata-rata gol per pertandingan")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "05_rata_rata_gol_kandang_tandang.png", bbox_inches="tight")
plt.close(fig)

# -----------------------------------------------------------------------------
# 5. ANALISIS BIVARIAT: KORELASI DAN SCATTER PLOT (stats.csv)
# -----------------------------------------------------------------------------
corr_cols = ["goals", "total_scoring_att", "ontarget_scoring_att", "wins", "goals_conceded", "clean_sheet"]
corr_data = stats[corr_cols].dropna()
corr = corr_data.corr(method="pearson")
corr.to_csv(TABLE_DIR / "matriks_korelasi_pearson.csv", float_format="%.4f")

fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlBu_r", center=0, vmin=-1, vmax=1,
            square=True, linewidths=0.7, cbar_kws={"shrink": 0.8}, ax=ax)
ax.set(title="Matriks Korelasi Pearson Statistik Klub")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "06_heatmap_korelasi_pearson.png", bbox_inches="tight")
plt.close(fig)

# Grafik 6: Tembakan tepat sasaran vs jumlah gol.
x, y = "ontarget_scoring_att", "goals"
r_xy = corr.loc[x, y]
fig, ax = plt.subplots(figsize=(9, 6))
sns.regplot(data=corr_data, x=x, y=y, ci=95,
            scatter_kws={"alpha": 0.65, "s": 48}, line_kws={"color": "#D97706", "linewidth": 2.2}, ax=ax)
ax.text(0.04, 0.95, f"Pearson r = {r_xy:.3f}\nn = {len(corr_data)} klub-musim",
        transform=ax.transAxes, va="top", ha="left",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "alpha": 0.9, "edgecolor": "#bbbbbb"})
ax.set(title="Hubungan Tembakan Tepat Sasaran dengan Jumlah Gol",
       xlabel="Tembakan tepat sasaran", ylabel="Jumlah gol")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "07_scatter_shots_on_target_vs_goals.png", bbox_inches="tight")
plt.close(fig)

# Grafik 7: Kebobolan vs kemenangan.
x, y = "goals_conceded", "wins"
r_xy = corr.loc[x, y]
fig, ax = plt.subplots(figsize=(9, 6))
sns.regplot(data=corr_data, x=x, y=y, ci=95,
            scatter_kws={"alpha": 0.65, "s": 48}, line_kws={"color": "#D97706", "linewidth": 2.2}, ax=ax)
ax.text(0.04, 0.95, f"Pearson r = {r_xy:.3f}\nn = {len(corr_data)} klub-musim",
        transform=ax.transAxes, va="top", ha="left",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "alpha": 0.9, "edgecolor": "#bbbbbb"})
ax.set(title="Hubungan Jumlah Kebobolan dengan Kemenangan",
       xlabel="Jumlah gol kebobolan", ylabel="Jumlah kemenangan")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "08_scatter_goals_conceded_vs_wins.png", bbox_inches="tight")
plt.close(fig)

# Tabel pasangan korelasi yang mudah dibaca untuk bahan slide.
correlation_pairs = pd.DataFrame([
    {"variabel_x": "Tembakan tepat sasaran", "variabel_y": "Jumlah gol", "pearson_r": corr.loc["ontarget_scoring_att", "goals"], "n": len(corr_data)},
    {"variabel_x": "Jumlah kebobolan", "variabel_y": "Jumlah kemenangan", "pearson_r": corr.loc["goals_conceded", "wins"], "n": len(corr_data)},
    {"variabel_x": "Total percobaan tembakan", "variabel_y": "Jumlah gol", "pearson_r": corr.loc["total_scoring_att", "goals"], "n": len(corr_data)},
    {"variabel_x": "Jumlah gol", "variabel_y": "Jumlah kemenangan", "pearson_r": corr.loc["goals", "wins"], "n": len(corr_data)},
])
correlation_pairs.to_csv(TABLE_DIR / "pasangan_korelasi_utama.csv", index=False, float_format="%.4f")

# Grafik Plotly interaktif (HTML) bila paket plotly tersedia.
if px is not None:
    fig_interactive = px.scatter(
        corr_data, x="ontarget_scoring_att", y="goals", color="wins",
        hover_data=["goals_conceded", "clean_sheet"],
        trendline="ols",
        title="Interaktif: Tembakan Tepat Sasaran vs Jumlah Gol",
        labels={"ontarget_scoring_att": "Tembakan tepat sasaran", "goals": "Jumlah gol", "wins": "Kemenangan"},
        color_continuous_scale="Viridis",
    )
    fig_interactive.update_layout(template="plotly_white", font={"family": "Arial", "size": 13})
    fig_interactive.write_html(FIGURE_DIR / "09_scatter_interaktif_plotly.html", include_plotlyjs="cdn")

# -----------------------------------------------------------------------------
# 6. RINGKASAN VALIDASI DAN HASIL DI TERMINAL
# -----------------------------------------------------------------------------
print("=" * 68)
print("ANALISIS DATA PREMIER LEAGUE SELESAI")
print("=" * 68)
print(f"stats.csv   : {stats.shape[0]} baris x {stats.shape[1]} kolom")
print(f"results.csv : {results.shape[0]} baris x {results.shape[1]} kolom")
print(f"Musim       : {stats['season'].nunique()} | Klub unik: {stats['team'].nunique()}")
print(f"Duplikat klub-musim: {stats.duplicated(['team', 'season']).sum()}")
print(f"Missing value stats: {stats.isna().sum().sum()} | results: {results.isna().sum().sum()}")
print(f"Ketidaksesuaian label hasil vs skor: {result_mismatches}")
print("\nStatistik jumlah gol:")
print(f"Mean={goals.mean():.2f} | Median={goals.median():.2f} | Modus={goals.mode().iloc[0]:.0f} | SD={goals.std():.2f}")
print(f"Min={goals.min():.0f} | Q1={goals.quantile(.25):.0f} | Q2={goals.quantile(.50):.0f} | Q3={goals.quantile(.75):.0f} | Max={goals.max():.0f}")
print("\nKorelasi utama (Pearson):")
print(f"Tembakan tepat sasaran vs gol : r={corr.loc['ontarget_scoring_att','goals']:.3f}")
print(f"Kebobolan vs kemenangan       : r={corr.loc['goals_conceded','wins']:.3f}")
print(f"Total tembakan vs gol         : r={corr.loc['total_scoring_att','goals']:.3f}")
print("\nHasil pertandingan (%):")
print(result_summary.to_string(index=False, formatters={"persentase": "{:.2f}%".format}))
print(f"\nRata-rata gol kandang={results['home_goals'].mean():.3f}; tandang={results['away_goals'].mean():.3f}")
print(f"\nTabel tersimpan di: {TABLE_DIR}")
print(f"Grafik tersimpan di: {FIGURE_DIR}")
