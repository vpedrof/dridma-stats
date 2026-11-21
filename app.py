from pathlib import Path
from html import escape

import pandas as pd
import streamlit as st

st.set_page_config(page_title="DRIDMA RIVAS | Estadísticas", page_icon="🥎", layout="wide", initial_sidebar_state="collapsed")

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
LOGO = BASE / "assets" / "logo_Dridma.png"

NAVY = "#09244D"
ORANGE = "#FF6500"

st.markdown("""
<style>
    .stApp { background: #FFFFFF; color: #09244D; }
    .block-container { padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1100px; }
    header[data-testid="stHeader"] { background: #FFFFFF; }
    [data-testid="stToolbar"] { color: #09244D; }
    h1, h2, h3 { color: #09244D !important; }
    .dridma-subtitle { text-align: center; color: #52617A; font-size: .9rem; margin: .1rem 0 1.3rem; }
    .dridma-topline { height: 5px; background: linear-gradient(90deg,#09244D 0%,#09244D 60%,#FF6500 60%,#FF6500 100%); border-radius: 4px; margin-bottom: 1.2rem; }
    .dridma-title { color: #09244D; text-align: center; font-weight: 900; font-size: clamp(1.35rem,4vw,2.15rem); letter-spacing: .02em; margin: .4rem 0 0; }
    .dridma-kpis { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 8px; margin: 1.1rem 0 1.3rem; }
    .dridma-kpi { min-width: 0; background: #09244D; border-radius: 12px; padding: 14px 5px 12px; text-align: center; }
    .dridma-kpi-label { font-size: clamp(.64rem,2.5vw,.92rem); color: #FFFFFF; font-weight: 700; text-transform: uppercase; letter-spacing: .025em; white-space: nowrap; }
    .dridma-kpi-value { font-size: clamp(2rem,8vw,3.15rem); font-weight: 850; color: #FF6500; line-height: 1.15; margin-top: 8px; }
    div[data-testid="stTabs"] button { font-weight: 700; color: #09244D; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: #FF6500; }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: #FF6500; }
    [data-testid="stDataFrame"] { border: 1px solid #DDE4EE; border-radius: 10px; }
    .dridma-section { color: #09244D; font-weight: 800; font-size: 1.15rem; margin: .7rem 0 .4rem; }
    .dridma-footer { margin-top: 2rem; border-top: 3px solid #FF6500; padding-top: .75rem; color: #66758B; font-size: .8rem; text-align: center; }
    @media (max-width: 640px) {
        .block-container { padding-left: .85rem; padding-right: .85rem; padding-top: .7rem; }
        .dridma-kpis { gap: 6px; }
        .dridma-kpi { border-radius: 9px; padding: 12px 3px; }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def read_data(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}.csv", encoding="utf-8-sig")


def numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def divide(a: pd.Series, b: pd.Series) -> pd.Series:
    return a / b.where(b.ne(0))


st.markdown('<div class="dridma-topline"></div>', unsafe_allow_html=True)
if LOGO.is_file():
    left, center, right = st.columns([1, 3, 1], vertical_alignment="center")
    with center:
        st.image(str(LOGO), use_container_width=True)
else:
    st.markdown('<div class="dridma-title">DRIDMA RIVAS</div>', unsafe_allow_html=True)
st.markdown('<div class="dridma-subtitle">ESTADÍSTICAS DEL EQUIPO</div>', unsafe_allow_html=True)

try:
    offense = read_data("db_Ofensiva")
    defense = read_data("db_Defensiva")
    pitching = read_data("db_Picheo")
    results = read_data("db_Resultados")
    names = read_data("db_Nombres")
except (FileNotFoundError, pd.errors.EmptyDataError) as exc:
    st.error(f"No se pudieron cargar los datos: {exc}")
    st.stop()

mapping = dict(zip(names["Jugador"], names["Nombre"]))
tournaments = sorted(results["TORNEO"].dropna().unique().tolist())
selected = st.multiselect("Torneos", tournaments, default=tournaments)
if not selected:
    st.info("Selecciona al menos un torneo.")
    st.stop()

offense = offense[offense["TORNEO"].isin(selected)].copy()
defense = defense[defense["TORNEO"].isin(selected)].copy()
pitching = pitching[pitching["TORNEO"].isin(selected)].copy()
results = results[results["TORNEO"].isin(selected)].copy()

for frame in (offense, defense, pitching):
    frame["Jugador"] = frame["Jugador"].map(mapping).fillna(frame["Jugador"])

wins = ((results["Equipo 1"].eq("DRI") & (results["Carreras"] > results["Carreras2"])) |
        (results["Equipo 2"].eq("DRI") & (results["Carreras2"] > results["Carreras"]))).sum()
losses = ((results["Equipo 1"].eq("DRI") & (results["Carreras"] < results["Carreras2"])) |
          (results["Equipo 2"].eq("DRI") & (results["Carreras2"] < results["Carreras"]))).sum()

kpis = [("Partidos", len(results)), ("Victorias", int(wins)), ("Derrotas", int(losses))]
items = "".join(
    f'<div class="dridma-kpi"><div class="dridma-kpi-label">{escape(label)}</div>'
    f'<div class="dridma-kpi-value">{value}</div></div>'
    for label, value in kpis
)
st.markdown(f'<div class="dridma-kpis">{items}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["Ofensiva", "Defensiva", "Picheo", "Resultados"])

with t1:
    fields = ["AB", "H", "BB", "R", "RBI", "SO", "2B", "3B", "HR", "TB", "HBP", "SH", "SF", "IBB", "SB", "CS"]
    offense = numeric(offense, fields)
    table = offense.groupby("Jugador", as_index=False)[fields].sum()
    table["AVG"] = divide(table["H"], table["AB"]).round(3)
    obp = divide(table["H"] + table["BB"] + table["HBP"], table["AB"] + table["BB"] + table["HBP"] + table["SF"])
    slg = divide(table["TB"], table["AB"])
    table["OPS"] = ((obp.fillna(0) + slg.fillna(0)) * 1000).round().astype(int)
    table = table.rename(columns={"SO": "K"})
    st.dataframe(table.sort_values(["AVG", "H"], ascending=False), hide_index=True, use_container_width=True)

with t2:
    fields = ["A", "PO", "E", "DP", "PB"]
    defense = numeric(defense, fields)
    table = defense.groupby("Jugador", as_index=False)[fields].sum()
    st.dataframe(table.sort_values("PO", ascending=False), hide_index=True, use_container_width=True)

with t3:
    fields = ["H", "R", "ER", "BB", "K", "Picheos", "Strikes"]
    pitching = numeric(pitching, fields + ["IP"])
    outs = (pitching["IP"].astype(int) * 3 + ((pitching["IP"] * 10).round().astype(int) % 10))
    pitching["OUTS"] = outs
    table = pitching.groupby("Jugador", as_index=False)[fields + ["OUTS"]].sum()
    table["IP"] = (table["OUTS"] // 3).astype(str) + "." + (table["OUTS"] % 3).astype(str)
    table["EFE"] = divide(7 * table["ER"], table["OUTS"] / 3).round(2)
    table = table[["Jugador", "IP", "H", "R", "ER", "BB", "K", "Picheos", "Strikes", "EFE"]]
    st.dataframe(table.sort_values("K", ascending=False), hide_index=True, use_container_width=True)

with t4:
    results["Fecha"] = pd.to_datetime(results["Fecha"], errors="coerce").dt.strftime("%d/%m/%Y")
    cols = ["TORNEO", "Fecha", "Eq1", "Carreras", "Eq2", "Carreras2"]
    st.dataframe(results[cols], hide_index=True, use_container_width=True)

st.markdown('<div class="dridma-footer">DRIDMA RIVAS · Estadísticas del equipo</div>', unsafe_allow_html=True)
