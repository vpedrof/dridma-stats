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
    .block-container { padding-top: .65rem; padding-bottom: 1.4rem; max-width: 1100px; }
    header[data-testid="stHeader"] { background: #FFFFFF; }
    [data-testid="stToolbar"] { color: #09244D; }
    h1, h2, h3 { color: #09244D !important; }
    .dridma-subtitle { text-align: center; color: #52617A; font-size: .9rem; margin: 0 0 .6rem; }
    .dridma-topline { height: 5px; background: linear-gradient(90deg,#09244D 0%,#09244D 60%,#FF6500 60%,#FF6500 100%); border-radius: 4px; margin-bottom: 1.2rem; }
    .dridma-title { color: #09244D; text-align: center; font-weight: 900; font-size: clamp(1.35rem,4vw,2.15rem); letter-spacing: .02em; margin: .4rem 0 0; }
    .dridma-kpis { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 8px; margin: .7rem 0 .85rem; }
    .dridma-kpi { min-width: 0; background: #09244D; border-radius: 12px; padding: 10px 5px 9px; text-align: center; }
    .dridma-kpi-label { font-size: clamp(.64rem,2.5vw,.92rem); color: #FFFFFF; font-weight: 700; text-transform: uppercase; letter-spacing: .025em; white-space: nowrap; }
    .dridma-kpi-value { font-size: clamp(2rem,8vw,3.15rem); font-weight: 850; color: #FF6500; line-height: 1.15; margin-top: 3px; }
    div[data-testid="stTabs"] button { font-weight: 700; color: #09244D; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: #FF6500; }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: #FF6500; }
    [data-testid="stDataFrame"] { border: 1px solid #DDE4EE; border-radius: 10px; }
    .dridma-section { color: #09244D; font-weight: 800; font-size: 1.15rem; margin: .7rem 0 .4rem; }
    .dridma-scroll { overflow-x: auto; max-width: 100%; border: 1px solid #DDE4EE; border-radius: 10px; }
    .dridma-table { border-collapse: separate; border-spacing: 0; font-size: .88rem; width: max-content; min-width: 100%; color: #09244D; }
    .dridma-table th, .dridma-table td { padding: .55rem .65rem; border-bottom: 1px solid #E2E7EF; white-space: nowrap; text-align: right; }
    .dridma-table th { background: #F2F5FA; font-weight: 750; position: sticky; top: 0; z-index: 1; }
    .dridma-table td:first-child, .dridma-table th:first-child { position: sticky; left: 0; z-index: 2; text-align: left; background: #FFFFFF; box-shadow: 2px 0 3px #09244D15; }
    .dridma-table th:first-child { z-index: 3; background: #F2F5FA; }
    .dridma-table tr:nth-child(even) td { background: #F8FAFD; }
    .dridma-table tr:nth-child(even) td:first-child { background: #F8FAFD; }
    .dridma-game { border: 1px solid #DDE4EE; border-radius: 12px; padding: .8rem; margin-bottom: .7rem; background: #FFFFFF; }
    .dridma-game-top { display:flex; justify-content:space-between; gap: .5rem; font-size:.76rem; color:#63718A; margin-bottom:.6rem; }
    .dridma-game-score { display:grid; grid-template-columns: 1fr auto 1fr; gap:.5rem; align-items:center; }
    .dridma-team { text-align:center; min-width:0; overflow-wrap:anywhere; font-size:.88rem; font-weight:700; }
    .dridma-score { display:block; font-size:1.7rem; font-weight:850; color:#09244D; }
    .dridma-score-home { color:#FF6500; }
    .dridma-vs { font-size:.75rem; color:#63718A; }
    .dridma-game-result { text-align:center; margin-top:.55rem; font-size:.78rem; font-weight:800; }
    .dridma-win { color:#177245; } .dridma-loss { color:#B63838; }
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


def render_table(df: pd.DataFrame, columns: list[str], formats: dict[str, str] | None = None) -> None:
    """Tabla HTML con primera columna fija y desplazamiento horizontal."""
    formats = formats or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in columns:
            value = row[col]
            if pd.isna(value):
                display = "—"
            elif col in formats:
                display = format(value, formats[col])
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                display = f"{value:g}"
            else:
                display = str(value)
            cells.append(f"<td>{escape(display)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    html = ('<div class="dridma-scroll"><table class="dridma-table"><thead><tr>'
            + headers + '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>')
    st.markdown(html, unsafe_allow_html=True)


def render_games(df: pd.DataFrame) -> None:
    """Tarjetas legibles en móvil; usa códigos de equipo para identificar DRIDMA."""
    for _, game in df.iterrows():
        first_is_dri = str(game["Equipo 1"]).strip().upper() == "DRI"
        second_is_dri = str(game["Equipo 2"]).strip().upper() == "DRI"
        if not (first_is_dri or second_is_dri):
            continue
        our_score = game["Carreras"] if first_is_dri else game["Carreras2"]
        their_score = game["Carreras2"] if first_is_dri else game["Carreras"]
        opponent = game["Eq2"] if first_is_dri else game["Eq1"]
        opponent = str(opponent).strip() if pd.notna(opponent) else "Rival"
        if opponent.upper().startswith("DRI"):
            opponent = str(game["Equipo 2"] if first_is_dri else game["Equipo 1"])
        try:
            our_score, their_score = int(our_score), int(their_score)
        except (ValueError, TypeError):
            continue
        status = "Victoria" if our_score > their_score else "Derrota" if our_score < their_score else "Empate"
        status_class = "dridma-win" if our_score > their_score else "dridma-loss" if our_score < their_score else ""
        date = pd.to_datetime(game["Fecha"], errors="coerce")
        date_text = date.strftime("%d/%m/%Y") if pd.notna(date) else "Fecha no disponible"
        tournament = escape(str(game["TORNEO"]))
        st.markdown(f'''<div class="dridma-game">
          <div class="dridma-game-top"><span>{escape(date_text)}</span><span>{tournament}</span></div>
          <div class="dridma-game-score">
            <div class="dridma-team">DRIDMA RIVAS<span class="dridma-score dridma-score-home">{our_score}</span></div>
            <div class="dridma-vs">VS</div>
            <div class="dridma-team">{escape(opponent)}<span class="dridma-score">{their_score}</span></div>
          </div><div class="dridma-game-result {status_class}">{status}</div>
        </div>''', unsafe_allow_html=True)


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
    table = table.sort_values(["AVG", "H"], ascending=False)
    render_table(table, ["Jugador", "AVG", "OPS", "AB", "H", "R", "RBI", "BB", "K", "2B", "3B", "HR", "TB", "HBP", "SH", "SF", "IBB", "SB", "CS"], {"AVG": ".3f"})

with t2:
    fields = ["A", "PO", "E", "DP", "PB"]
    defense = numeric(defense, fields)
    table = defense.groupby("Jugador", as_index=False)[fields].sum()
    render_table(table.sort_values("PO", ascending=False), ["Jugador", "PO", "A", "E", "DP", "PB"])

with t3:
    fields = ["H", "R", "ER", "BB", "K", "Picheos", "Strikes"]
    pitching = numeric(pitching, fields + ["IP"])
    outs = (pitching["IP"].astype(int) * 3 + ((pitching["IP"] * 10).round().astype(int) % 10))
    pitching["OUTS"] = outs
    table = pitching.groupby("Jugador", as_index=False)[fields + ["OUTS"]].sum()
    table["IP"] = (table["OUTS"] // 3).astype(str) + "." + (table["OUTS"] % 3).astype(str)
    table["EFE"] = divide(7 * table["ER"], table["OUTS"] / 3).round(2)
    table = table[["Jugador", "IP", "H", "R", "ER", "BB", "K", "Picheos", "Strikes", "EFE"]]
    render_table(table.sort_values("K", ascending=False), ["Jugador", "IP", "EFE", "K", "H", "BB", "R", "ER", "Picheos", "Strikes"], {"EFE": ".2f"})

with t4:
    render_games(results.sort_values("Fecha"))

st.markdown('<div class="dridma-footer">DRIDMA RIVAS · Estadísticas del equipo</div>', unsafe_allow_html=True)
