"""Dashboard Air Quality Dataset (Streamlit).

Membaca dashboard/main_data.csv, yaitu data bersih hasil notebook.ipynb: rata-rata PM2.5 HARIAN per stasiun
(hanya hari dengan minimal 18 jam PM2.5 valid), periode 1 Mar 2013 - 28 Feb 2017, 12 stasiun pemantau di Beijing.

Jalankan:  cd dashboard  ->  streamlit run dashboard.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Air Quality Dashboard", page_icon="🌫️", layout="wide")

DATA_PATH = Path(__file__).resolve().parent / "main_data.csv"
SEASONS = ["Winter", "Spring", "Summer", "Autumn"]
MONTHS = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"}
AQI = ["Excellent", "Good", "Lightly Polluted", "Moderately Polluted", "Heavily Polluted", "Severely Polluted"]
AQI_COLORS = dict(zip(AQI, ["#1a9850", "#a6d96a", "#fee08b", "#fdae61", "#f46d43", "#a50026"]))
WIND = ["<= 1 m/s (tenang)", "1-2 m/s", "2-3 m/s", "> 3 m/s"]
COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

BQ1 = ("Perbandingan Kualitas Udara Antar Stasiun",
       "Stasiun pemantau mana yang memiliki rata-rata PM2.5 harian tertinggi dan terendah, berapa selisihnya, dan berapa persen hari yang melampaui batas harian di setiap stasiun?")
BQ2 = ("Pola Musiman dan Tren Tahunan PM2.5",
       "Bagaimana pola bulanan dan musiman rata-rata PM2.5 harian, bulan dan musim mana yang terburuk, dan bagaimana perubahan rata-rata antar periode tahunan (Maret–Februari)?")
BQ3 = ("Pengaruh Kondisi Cuaca (Angin, Hujan, Arah Angin) terhadap PM2.5",
       "Bagaimana hubungan kecepatan angin, hujan, dan arah angin dengan PM2.5 harian, dan berapa persen lebih rendah PM2.5 pada hari berangin (> 3 m/s) dibanding hari tenang (<= 1 m/s)?")


@st.cache_data
def load_data() -> pd.DataFrame:
    d = pd.read_csv(DATA_PATH, parse_dates=["date"])
    d["season"] = pd.Categorical(d["season"], categories=SEASONS, ordered=True)
    d["aqi_category"] = pd.Categorical(d["aqi_category"], categories=AQI, ordered=True)
    d["wind_class"] = pd.Categorical(d["wind_class"], categories=WIND, ordered=True)
    return d


def idn(x, nd=0):
    """Format angka gaya Indonesia (titik ribuan, koma desimal)."""
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct_signed(v, nd=1):
    return ("+" if v >= 0 else "-") + idn(abs(v), nd) + "%"


df = load_data()

# Ringkasan pada DATA PENUH (tanpa filter), dihitung dari main_data.csv; dipakai sebagai pembanding pada insight.
_st = df.groupby("station")["pm25_mean"].mean().sort_values(ascending=False)
FULL = {"st_top": (_st.index[0], _st.iloc[0]), "st_bot": (_st.index[-1], _st.iloc[-1])}
_m = df.groupby("month")["pm25_mean"].mean()
FULL["m_worst"] = (MONTHS[int(_m.idxmax())], _m.max())
_w = df.groupby("wind_class", observed=True)["pm25_mean"].mean()
FULL["wind_drop"] = (_w.iloc[-1] / _w.iloc[0] - 1) * 100

# ------------------------------------------------------------------ header
st.title("🌫️ Air Quality Dashboard")
st.caption(
    "Analisis PM2.5 dari 12 stasiun pemantau kualitas udara di Beijing (Air Quality Dataset). Satuan analisis: **rata-rata PM2.5 harian per stasiun** "
    f"(hari dengan minimal 18 jam data valid), **{df['date'].min():%d %b %Y} – {df['date'].max():%d %b %Y}**. Data identik dengan hasil pembersihan pada notebook."
)
st.caption("💡 Gunakan filter di sidebar (periode, stasiun, musim) dan slider batas PM2.5. KPI, grafik, dan insight ikut berubah.")

with st.expander("Dataset overview"):
    a, b, c, d = st.columns(4)
    a.metric("Hari-stasiun valid", idn(len(df)))
    b.metric("Stasiun", idn(df["station"].nunique()))
    c.metric("Tanggal unik", idn(df["date"].nunique()))
    d.metric("Rata-rata PM2.5 (µg/m³)", idn(df["pm25_mean"].mean(), 2))
    st.write("Struktur `main_data.csv`: 1 baris per stasiun per hari valid. Contoh 10 baris pertama:")
    st.dataframe(df.head(10), width="stretch")

# ------------------------------------------------------------------ filter
st.sidebar.header("Filter")
min_d, max_d = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Periode tanggal", (min_d, max_d), min_value=min_d, max_value=max_d)
all_st = sorted(df["station"].unique())
sel_st = st.sidebar.multiselect("Stasiun", all_st, default=all_st)
sel_season = st.sidebar.multiselect("Musim", SEASONS, default=SEASONS)
thr = st.sidebar.slider("Batas PM2.5 harian (µg/m³)", 35, 150, 75, step=5)
st.sidebar.caption("Batas 75 µg/m³ = batas harian Grade II (GB 3095-2012), dipakai pada notebook.")

if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.info("Pilih tanggal awal dan tanggal akhir pada filter periode.")
    st.stop()

mask = ((df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])
        & df["station"].isin(sel_st) & df["season"].isin(sel_season))
f = df[mask]
if f.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Longgarkan filter di sidebar.")
    st.stop()

# ------------------------------------------------------------------ KPI
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Hari-stasiun", idn(len(f)))
k2.metric("Rata-rata PM2.5 harian", f"{idn(f['pm25_mean'].mean(), 2)} µg/m³")
k3.metric(f"Hari > {thr} µg/m³", f"{idn((f['pm25_mean'] > thr).mean() * 100, 1)}%")
k4.metric("Hari Heavily/Severely Polluted", f"{idn((f['pm25_mean'] > 150).mean() * 100, 1)}%", help="PM2.5 harian > 150 µg/m³ (kategori HJ 633-2012).")
k5.metric("Stasiun terpilih", idn(f["station"].nunique()))
st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📍 BQ1: Antar Stasiun", "📅 BQ2: Musim & Tren", "🌬️ BQ3: Cuaca", "🧮 Kategori Kualitas Udara"])

# ------------------------------------------------------------------ BQ1
with tab1:
    st.subheader(f"Business Question 1: {BQ1[0]}")
    st.markdown(f"**Pertanyaan bisnis:** {BQ1[1]}")
    stt = f.groupby("station").agg(rata2=("pm25_mean", "mean"), hari=("pm25_mean", "size"),
                                   over=("pm25_mean", lambda s: (s > thr).mean() * 100)).sort_values("rata2", ascending=False).reset_index()
    c1, c2 = st.columns(2)
    f1 = px.bar(stt.sort_values("rata2"), x="rata2", y="station", orientation="h", text=stt.sort_values("rata2")["rata2"].round(1),
                labels={"rata2": "Rata-rata PM2.5 harian (µg/m³)", "station": "Stasiun"}, color_discrete_sequence=["#d62728"], hover_data=["hari"])
    f1.update_layout(title="Rata-rata PM2.5 harian per stasiun")
    c1.plotly_chart(f1)
    f2 = px.bar(stt.sort_values("over"), x="over", y="station", orientation="h", text=stt.sort_values("over")["over"].round(1),
                labels={"over": f"Hari dengan PM2.5 > {thr} µg/m³ (%)", "station": "Stasiun"}, color_discrete_sequence=["#ff7f0e"], hover_data=["hari"])
    f2.update_layout(title=f"Persentase hari di atas {thr} µg/m³")
    c2.plotly_chart(f2)
    hi, lo = stt.iloc[0], stt.iloc[-1]
    msg = f"**Insight (sesuai filter):** tertinggi **{hi['station']}** ({idn(hi['rata2'], 2)} µg/m³; {idn(hi['over'], 1)}% hari > {thr}), "
    msg += f"terendah **{lo['station']}** ({idn(lo['rata2'], 2)} µg/m³; {idn(lo['over'], 1)}%)" if len(stt) > 1 else "satu stasiun terpilih"
    if len(stt) > 1:
        msg += f", selisih **{idn(hi['rata2'] - lo['rata2'], 2)} µg/m³**"
    msg += f". Pada data penuh: tertinggi {FULL['st_top'][0]} ({idn(FULL['st_top'][1], 2)}), terendah {FULL['st_bot'][0]} ({idn(FULL['st_bot'][1], 2)}); perbedaan di antara stasiun teratas kecil (lihat uji sensitivitas di notebook)."
    st.info(msg)

# ------------------------------------------------------------------ BQ2
with tab2:
    st.subheader(f"Business Question 2: {BQ2[0]}")
    st.markdown(f"**Pertanyaan bisnis:** {BQ2[1]}")
    mt = f.groupby("month")["pm25_mean"].mean().reindex(range(1, 13)).dropna().reset_index()
    mt["bulan"] = mt["month"].map(MONTHS)
    mt["musim"] = mt["month"].map(lambda m: SEASONS[0] if m in (12, 1, 2) else SEASONS[1] if m in (3, 4, 5) else SEASONS[2] if m in (6, 7, 8) else SEASONS[3])
    c1, c2 = st.columns([1.6, 1])
    fm = px.bar(mt, x="bulan", y="pm25_mean", color="musim", text=mt["pm25_mean"].round(0), category_orders={"bulan": list(MONTHS.values()), "musim": SEASONS},
                labels={"bulan": "Bulan kalender", "pm25_mean": "Rata-rata PM2.5 harian (µg/m³)", "musim": "Musim"})
    fm.update_layout(title="Rata-rata PM2.5 harian menurut bulan")
    c1.plotly_chart(fm)
    pt = f.groupby("period").agg(rata2=("pm25_mean", "mean"), hari=("pm25_mean", "size")).reset_index()
    fp = px.bar(pt, x="period", y="rata2", text=pt["rata2"].round(1), hover_data=["hari"], color_discrete_sequence=["#4c72b0"],
                labels={"period": "Periode tahunan (Mar-Feb)", "rata2": "Rata-rata PM2.5 harian (µg/m³)"})
    fp.update_layout(title="Rata-rata PM2.5 harian per periode")
    c2.plotly_chart(fp)
    wm = mt.loc[mt["pm25_mean"].idxmax()]; bm = mt.loc[mt["pm25_mean"].idxmin()]
    msg = f"**Insight (sesuai filter):** bulan terburuk **{wm['bulan']}** ({idn(wm['pm25_mean'], 1)} µg/m³), terbaik **{bm['bulan']}** ({idn(bm['pm25_mean'], 1)})."
    sm = f.groupby("season", observed=True)["pm25_mean"].mean()
    if len(sm) > 1:
        msg += f" Musim tertinggi **{sm.idxmax()}** ({idn(sm.max(), 1)}), terendah **{sm.idxmin()}** ({idn(sm.min(), 1)})."
    if len(pt) > 1:
        msg += f" Perubahan periode {pt.iloc[0]['period']} → {pt.iloc[-1]['period']}: {pct_signed((pt.iloc[-1]['rata2'] / pt.iloc[0]['rata2'] - 1) * 100)}."
    msg += f" Pada data penuh, bulan terburuk {FULL['m_worst'][0]} ({idn(FULL['m_worst'][1], 1)} µg/m³)."
    st.info(msg)

# ------------------------------------------------------------------ BQ3
with tab3:
    st.subheader(f"Business Question 3: {BQ3[0]}")
    st.markdown(f"**Pertanyaan bisnis:** {BQ3[1]}")
    wt = f.groupby("wind_class", observed=True).agg(rata2=("pm25_mean", "mean"), hari=("pm25_mean", "size")).reindex(WIND).dropna().reset_index()
    rain = f.dropna(subset=["rain_day"]).copy()
    rain["kondisi"] = np.where(rain["rain_day"] == 1, "Ada hujan", "Tanpa hujan")
    rt = rain.groupby(["season", "kondisi"], observed=True)["pm25_mean"].mean().reset_index()
    dt = f.dropna(subset=["wd_dominant"]).groupby("wd_dominant")["pm25_mean"].agg(["mean", "size"]).reindex(COMPASS).dropna().reset_index()
    dt.columns = ["arah", "rata2", "hari"]
    c1, c2, c3 = st.columns([1, 1.1, 1.5])
    fw = px.bar(wt, x="wind_class", y="rata2", text=wt["rata2"].round(1), hover_data=["hari"], color_discrete_sequence=["#1a9850"],
                labels={"wind_class": "Kecepatan angin rata-rata harian", "rata2": "Rata-rata PM2.5 harian (µg/m³)"})
    fw.update_layout(title="PM2.5 menurut kecepatan angin")
    c1.plotly_chart(fw)
    if not rt.empty:
        fr = px.bar(rt, x="season", y="pm25_mean", color="kondisi", barmode="group", text=rt["pm25_mean"].round(0), category_orders={"season": SEASONS},
                    color_discrete_map={"Tanpa hujan": "#bdbdbd", "Ada hujan": "#3182bd"},
                    labels={"season": "Musim", "pm25_mean": "Rata-rata PM2.5 harian (µg/m³)", "kondisi": "Kondisi"})
        fr.update_layout(title="PM2.5 hari hujan vs tanpa hujan per musim")
        c2.plotly_chart(fr)
    else:
        c2.caption("Data hujan tidak tersedia pada filter ini.")
    fd = px.bar(dt, x="arah", y="rata2", text=dt["rata2"].round(0), hover_data=["hari"], color_discrete_sequence=["#6a51a3"], category_orders={"arah": COMPASS},
                labels={"arah": "Arah angin dominan harian", "rata2": "Rata-rata PM2.5 harian (µg/m³)"})
    fd.update_layout(title="PM2.5 menurut arah angin dominan")
    c3.plotly_chart(fd)
    msg = "**Insight (sesuai filter):** "
    if {"<= 1 m/s (tenang)", "> 3 m/s"} <= set(wt["wind_class"].astype(str)):
        a_, b_ = wt.set_index("wind_class").loc["<= 1 m/s (tenang)", "rata2"], wt.set_index("wind_class").loc["> 3 m/s", "rata2"]
        msg += f"hari tenang {idn(a_, 1)} µg/m³ vs hari berangin > 3 m/s {idn(b_, 1)} ({pct_signed((b_ / a_ - 1) * 100)}). "
    else:
        msg += "pilih rentang yang memuat hari tenang dan hari berangin untuk membandingkan. "
    if len(dt) >= 3:
        s_ = dt.sort_values("rata2", ascending=False)
        msg += f"Arah dominan dengan PM2.5 tertinggi: {', '.join(s_['arah'].head(3))}; terendah: {', '.join(s_['arah'].tail(3))}. "
    msg += f"Pada data penuh, hari berangin {pct_signed(FULL['wind_drop'])} dibanding hari tenang. Pengaruh hujan tidak konsisten antarmusim; seluruh hubungan adalah asosiasi, bukan sebab-akibat."
    st.info(msg)

# ------------------------------------------------------------------ Kategori
with tab4:
    st.subheader("Kategori Kualitas Udara Harian (Analisis Lanjutan: Binning)")
    st.caption("Batas kategori PM2.5 24 jam mengikuti skema HJ 633-2012: Excellent (0–35), Good (35–75), Lightly (75–115), Moderately (115–150), Heavily (150–250), Severely (> 250 µg/m³).")
    c1, c2 = st.columns(2)
    ds = f["aqi_category"].value_counts().reindex(AQI).fillna(0).rename("hari").reset_index()
    ds.columns = ["kategori", "hari"]
    ds["persen"] = ds["hari"] / ds["hari"].sum() * 100
    fk = px.bar(ds, x="kategori", y="persen", color="kategori", color_discrete_map=AQI_COLORS, text=ds["persen"].round(1), category_orders={"kategori": AQI},
                labels={"kategori": "Kategori", "persen": "Proporsi hari (%)"})
    fk.update_layout(showlegend=False, title="Distribusi kategori kualitas udara")
    c1.plotly_chart(fk)
    cs = (pd.crosstab(f["season"], f["aqi_category"], normalize="index") * 100).reindex(columns=AQI).reset_index().melt(id_vars="season", var_name="kategori", value_name="persen")
    fs = px.bar(cs, x="season", y="persen", color="kategori", color_discrete_map=AQI_COLORS, category_orders={"kategori": AQI, "season": SEASONS},
                labels={"season": "Musim", "persen": "Proporsi hari (%)", "kategori": "Kategori"})
    fs.update_layout(title="Komposisi kategori per musim")
    c2.plotly_chart(fs)
    hs = (f["pm25_mean"] > 150).mean() * 100
    st.info(f"**Insight (sesuai filter):** {idn(ds.loc[ds['kategori'] == 'Excellent', 'persen'].iloc[0], 1)}% hari berkategori Excellent dan {idn(hs, 1)}% Heavily/Severely Polluted. "
            "Pada data penuh, risiko tinggi terkonsentrasi pada musim dingin dan hari tanpa angin (lihat notebook).")

st.caption("Sumber data: Air Quality Dataset (Beijing Multi-Site, 12 stasiun). Dikerjakan oleh M Fahril Luthfi.")
