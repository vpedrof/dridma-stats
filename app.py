from pathlib import Path
from html import escape
from numbers import Number
import re

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
    /* Pestañas compactas y adaptables a la pantalla. */
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        display: flex !important;
        width: 100% !important;
        min-width: 0 !important;
        gap: 0 !important;
        justify-content: stretch !important;
        overflow: visible !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab"] {
        flex: 1 1 auto !important;
        width: auto !important;
        min-width: 0 !important;
        max-width: auto !important;
        padding: .55rem 0 !important;
        justify-content: center !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab"] p {
        font-size: clamp(.58rem, 2.35vw, .85rem) !important;
        letter-spacing: -.025em !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-border"] { width: 100%; }
    div[data-testid="stTabs"] button[aria-label*="scroll" i],
    div[data-testid="stTabs"] button[aria-label*="previous" i],
    div[data-testid="stTabs"] button[aria-label*="next" i] {
        display: none !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: #FF6500; }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: #FF6500; }
    [data-testid="stDataFrame"] { border: 1px solid #DDE4EE; border-radius: 10px; }
    .dridma-player-name { font-size: 1.25rem; font-weight: 850; color: #09244D; margin: .6rem 0; }
    .dridma-section { color: #09244D; font-weight: 800; font-size: 1.15rem; margin: .7rem 0 .4rem; }
    .dridma-scroll { overflow-x: auto; max-width: 100%; border: 1px solid #DDE4EE; border-radius: 10px; }
    .dridma-table { border-collapse: separate; border-spacing: 0; font-size: .88rem; width: max-content; min-width: 100%; color: #09244D; }
    .dridma-table th, .dridma-table td { padding: .55rem .65rem; border-bottom: 1px solid #E2E7EF; white-space: nowrap; text-align: right; }
    .dridma-table th { background: #F2F5FA; font-weight: 750; position: sticky; top: 0; z-index: 1; }
    .dridma-table td:first-child, .dridma-table th:first-child { position: sticky; left: 0; z-index: 2; text-align: left; background: #FFFFFF; box-shadow: 2px 0 3px #09244D15; }
    .dridma-table th:first-child { z-index: 3; background: #F2F5FA; }
    .dridma-table tr:nth-child(even) td { background: #F8FAFD; }
    .dridma-table tr:nth-child(even) td:first-child { background: #F8FAFD; }
    /* Tablas compactas: menor espacio lateral, cifras alineadas y nombres cortos. */
    .dridma-table { font-size: .78rem; font-variant-numeric: tabular-nums; }
    .dridma-table th, .dridma-table td {
        padding: .34rem .32rem;
        line-height: 1.2;
        letter-spacing: -.01em;
    }
    .dridma-table th:first-child, .dridma-table td:first-child {
        min-width: 0;
        max-width: 118px;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    @media (max-width: 640px) {
        .dridma-scroll { border-radius: 8px; }
        .dridma-table { font-size: 11px; }
        .dridma-table th, .dridma-table td {
            padding: 7px 5px;
            line-height: 1.1;
            letter-spacing: -.015em;
        }
        .dridma-table th:first-child, .dridma-table td:first-child {
            max-width: 92px;
        }
    }

    .dridma-game { border: 1px solid #DDE4EE; border-radius: 12px; padding: .8rem; margin-bottom: .7rem; background: #FFFFFF; }
    .dridma-game-top { display:flex; justify-content:space-between; gap: .5rem; font-size:.76rem; color:#63718A; margin-bottom:.6rem; }
    .dridma-game-score { display:grid; grid-template-columns: 1fr auto 1fr; gap:.5rem; align-items:center; }
    .dridma-team { text-align:center; min-width:0; font-size:.88rem; font-weight:700; }
    .dridma-team-name { display:block; white-space:nowrap; font-size:clamp(.60rem, 2.5vw, .88rem); letter-spacing:-.025em; }
    .dridma-team-code { display:block; white-space:nowrap; font-size:.82rem; }
    .dridma-score { display:block; font-size:1.7rem; font-weight:850; color:#09244D; }
    .dridma-score-home { color:#FF6500; }
    .dridma-vs { font-size:.75rem; color:#63718A; }
    .dridma-game-result { text-align:center; margin-top:.55rem; font-size:.78rem; font-weight:800; }
    .dridma-win { color:#177245; } .dridma-loss { color:#B63838; }
    .dridma-profile { background: #09244D; color: #FFFFFF; border-radius: 14px; padding: 1rem; margin: .6rem 0 .8rem; }
    .dridma-profile-label { color: #FF8B3D; font-size: .73rem; font-weight: 800; letter-spacing: .07em; }
    .dridma-profile-name { color: #FFFFFF; font-size: clamp(1.3rem, 5vw, 1.8rem); font-weight: 850; margin: .25rem 0; }
    .dridma-profile-sub { color: #D8E3F4; font-size: .8rem; }
    .dridma-stat-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 7px; margin: .5rem 0 .85rem; }
    .dridma-stat { background: #F2F5FA; border: 1px solid #E2E7EF; border-radius: 10px; text-align: center; padding: .65rem .2rem; min-width: 0; }
    .dridma-stat-label { color: #53637C; font-size: .72rem; font-weight: 800; }
    .dridma-stat-value { color: #09244D; font-size: clamp(1.2rem, 5vw, 1.7rem); font-weight: 850; }
    .dridma-footer { margin-top: 2rem; border-top: 3px solid #FF6500; padding-top: .75rem; color: #66758B; font-size: .8rem; text-align: center; }
    @media (max-width: 640px) {
        .block-container { padding-left: .85rem; padding-right: .85rem; padding-top: .7rem; }
        .dridma-kpis { gap: 6px; }
        .dridma-kpi { border-radius: 9px; padding: 12px 3px; }
    }
    /* Ajuste fino V4.3: reducir separación entre pestañas. */
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0 !important;
        column-gap: 0 !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        padding: 8px 2px !important;
        margin: 0 !important;
        min-width: 0 !important;
        font-size: 11px !important;
        letter-spacing: -0.3px !important;
        white-space: nowrap !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"] p {
        font-size: 11px !important;
        letter-spacing: -0.3px !important;
        white-space: nowrap !important;
    }

    /* Distribución de AB: barras que crecen hacia la izquierda. */
    .dridma-count-table .dridma-ab-track {
        width: 108px; height: 13px; background: #EAF0F7;
        border-radius: 3px; display: flex; justify-content: flex-end;
        margin-left: auto; overflow: hidden;
    }
    .dridma-count-table .dridma-ab-fill {
        height: 100%; background: #4A90D9; border-radius: 3px;
    }
    .dridma-count-table .dridma-count-total td {
        font-weight: 750; border-top: 2px solid #AEBBD0;
    }
</style>
""", unsafe_allow_html=True)


EXCEL = DATA / "db_Dridma_Stats.xlsx"

# Adaptación del esquema HTML-to-Excel al esquema usado por la interfaz original.
COLUMNAS = {
    "db_Ofensiva": {"Torneo": "TORNEO", "ab": "AB", "h": "H", "bb": "BB", "r": "R", "rbi": "RBI", "so": "SO", "double": "2B", "triple": "3B", "hr": "HR", "tb": "TB", "hbp": "HBP", "sh": "SH", "sf": "SF", "ibb": "IBB", "sb": "SB", "cs": "CS"},
    "db_Defensiva": {"Torneo": "TORNEO", "field_a": "A", "field_po": "PO", "field_e": "E", "field_dp": "DP", "field_pb": "PB"},
    "db_Picheo": {"Torneo": "TORNEO", "pitch_ip": "IP", "pitch_h": "H", "pitch_r": "R", "pitch_er": "ER", "pitch_bb": "BB", "pitch_so": "K", "pitch_pitches": "Picheos", "pitch_strikes": "Strikes"},
}

@st.cache_data(show_spinner=False)
def read_data(name: str) -> pd.DataFrame:
    frame = pd.read_excel(EXCEL, sheet_name=name, engine="openpyxl")
    if name == "db_Nombres":
        return frame.rename(columns={"Nombre_original": "Jugador", "Nombre_limpio": "Nombre"})
    if name == "db_Resultados":
        return frame.rename(columns={
            "Equipo_Local_Codigo": "Equipo 1", "Equipo_Visitante_Codigo": "Equipo 2",
            "Equipo_Local": "Eq1", "Equipo_Visitante": "Eq2",
            "Carreras_Local": "Carreras", "Carreras_Visitante": "Carreras2",
        })
    if name in COLUMNAS:
        return frame.rename(columns=COLUMNAS[name])
    return frame


def numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def divide(a: pd.Series, b: pd.Series) -> pd.Series:
    return a / b.where(b.ne(0))


# Definiciones compartidas por el glosario y las ayudas en las cabeceras HTML.
STAT_HELP = {
    "G": "Partidos jugados", "AB": "Turnos oficiales al bate", "H": "Hits o imparables",
    "2B": "Dobles", "3B": "Triples", "HR": "Jonrones", "RBI": "Carreras impulsadas",
    "R": "Carreras anotadas o permitidas, según la tabla", "BB": "Bases por bolas",
    "SO": "Ponches", "K": "Ponches", "AVG": "Promedio de bateo: H / AB",
    "OPS": "OBP + SLG (en esta aplicación se presenta multiplicado por 1000)",
    "OBP": "Porcentaje de embasado", "SLG": "Promedio de bases totales por turno oficial",
    "TB": "Bases totales", "HBP": "Golpeado por lanzamiento", "SH": "Toque de sacrificio",
    "SF": "Elevado de sacrificio", "IBB": "Base por bolas intencional",
    "SB": "Bases robadas", "CS": "Atrapado intentando robar base",
    "PO": "Eliminaciones defensivas (putouts)", "A": "Asistencias defensivas",
    "E": "Errores defensivos", "DP": "Dobles plays", "PB": "Passed balls",
    "IP": "Entradas lanzadas (el decimal indica outs: .1 = 1 out; .2 = 2 outs)",
    "ER": "Carreras limpias permitidas", "EFE": "Efectividad: carreras limpias por 7 entradas (ERA)",
    "ERA": "Promedio de carreras limpias por 7 entradas",
    "Picheos": "Lanzamientos realizados", "Strikes": "Lanzamientos contabilizados como strike",
    "TORNEO": "Torneo de participación", "Equipo": "Código de tres letras del equipo rival",
    "Lanzador": "Lanzador rival (apellido e inicial)",
}

def short_player_name(full_name: str) -> str:
    """Nombre visual de DRIDMA basado en db_Nombres, sin alterar datos internos."""
    name = " ".join(str(full_name).split())
    if not name or name.lower() in ("nan", "desconocido", "total"):
        return name
    # El diccionario se construye con el nombre ORIGINAL, que distingue
    # inequívocamente apellidos en MAYÚSCULAS de nombres de pila.
    if name in PLAYER_SHORT_NAMES:
        return PLAYER_SHORT_NAMES[name]
    # Respaldo para nombres completos fuera de db_Nombres: Nombre Apellido.
    parts = name.split()
    if len(parts) < 2:
        return name
    return f"{parts[-1].capitalize()} {parts[0][0].upper()}."


def short_source_name(full_name: str) -> str:
    """WBSC: APELLIDO(S) Nombre(s) -> PrimerApellido N."""
    name = " ".join(str(full_name).split())
    if not name or name.lower() in ("nan", "desconocido", "total"):
        return name
    parts = name.split()
    first_given_idx = next((i for i, part in enumerate(parts)
                            if any(c.isalpha() for c in part) and not part.isupper()), None)
    if first_given_idx is None or first_given_idx == 0:
        return name
    return f"{parts[0].capitalize()} {parts[first_given_idx][0].upper()}."


# Se completa tras cargar db_Nombres. Evita inferir el orden de un
# nombre ya normalizado (por ejemplo, «Benitez Gabriel»).
PLAYER_SHORT_NAMES: dict[str, str] = {}


def render_table(df: pd.DataFrame, columns: list[str], formats: dict[str, str] | None = None) -> None:
    """Tabla HTML con primera columna fija y desplazamiento horizontal."""
    formats = formats or {}
    headers = "".join(f'<th title="{escape(STAT_HELP.get(str(c), str(c)), quote=True)}">{escape(str(c))}</th>' for c in columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in columns:
            value = row[col]
            if pd.isna(value):
                display = "—"
            elif col in formats:
                display = format(value, formats[col])
            elif isinstance(value, Number) and not isinstance(value, bool):
                display = f"{value:g}"
            else:
                display = str(value)
            if col == "Jugador" and display != "—":
                display = short_player_name(display)
            cells.append(f"<td>{escape(display)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    html = ('<div class="dridma-scroll"><table class="dridma-table"><thead><tr>'
            + headers + '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>')
    st.markdown(html, unsafe_allow_html=True)



def render_count_performance(df: pd.DataFrame) -> None:
    """Tabla por conteo con barras de AB alineadas a la derecha.

    Las barras se escalan respecto al máximo AB entre conteos individuales;
    TOTAL no tiene barra y mantiene sus valores numéricos.
    """
    headers = ["Conteo", "Distribución", "AB", "H", "AVG"]
    max_ab = pd.to_numeric(
        df.loc[df["Conteo"].astype(str).ne("TOTAL"), "AB"], errors="coerce"
    ).max()
    max_ab = float(max_ab) if pd.notna(max_ab) and max_ab > 0 else 0.0
    body = []
    for _, item in df.iterrows():
        count = str(item["Conteo"])
        total = count == "TOTAL"
        ab = item["AB"]
        hits = item["H"]
        avg = item["AVG"]
        width = (100.0 * float(ab) / max_ab) if max_ab and pd.notna(ab) and not total else 0.0
        bar = (f'<div class="dridma-ab-track"><div class="dridma-ab-fill" '
               f'style="width:{width:.2f}%"></div></div>') if not total else ""
        avg_text = f"{float(avg):.3f}" if pd.notna(avg) else "—"
        ab_text = f"{int(ab)}" if pd.notna(ab) else "—"
        hits_text = f"{int(hits)}" if pd.notna(hits) else "—"
        row_class = ' class="dridma-count-total"' if total else ""
        body.append(f'<tr{row_class}><td>{escape(count)}</td><td>{bar}</td>'
                    f'<td>{escape(ab_text)}</td><td>{escape(hits_text)}</td>'
                    f'<td>{escape(avg_text)}</td></tr>')
    th = "".join(f"<th>{escape(h)}</th>" for h in headers)
    html = ('<div class="dridma-scroll"><table class="dridma-table dridma-count-table">'
            '<thead><tr>' + th + '</tr></thead><tbody>' + "".join(body) +
            '</tbody></table></div>')
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
        opponent_code = str(game["Equipo 2"] if first_is_dri else game["Equipo 1"]).strip().upper()
        # El nombre del Excel puede incluir ya el código al final: «Equipo (CRO)».
        # Lo retiramos para que el código aparezca siempre en una segunda línea.
        opponent = re.sub(r"\s*\([A-Za-z]{3}\)\s*$", "", opponent).strip()
        if opponent.upper().startswith("DRI"):
            opponent = "Rival"
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
            <div class="dridma-team"><span class="dridma-team-name">Dridma Rivas</span><span class="dridma-team-code">(DRI)</span><span class="dridma-score dridma-score-home">{our_score}</span></div>
            <div class="dridma-vs">VS</div>
            <div class="dridma-team"><span class="dridma-team-name">{escape(opponent)}</span><span class="dridma-team-code">({escape(opponent_code)})</span><span class="dridma-score">{their_score}</span></div>
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
    turns = read_data("db_Turnos")
    pitches = read_data("db_Lanzamientos")
except (FileNotFoundError, ValueError, ImportError, OSError, KeyError) as exc:
    st.error(f"No se pudieron cargar los datos: {exc}")
    st.stop()

names = names.dropna(subset=["Jugador", "Nombre"])
mapping = dict(zip(names["Jugador"].astype(str).str.strip(), names["Nombre"].astype(str).str.strip()))
PLAYER_SHORT_NAMES = {
    clean: short_source_name(original)
    for original, clean in mapping.items()
}

def stat_cards(stats: list[tuple[str, str]]) -> None:
    blocks = "".join(
        '<div class="dridma-stat"><div class="dridma-stat-label">'
        + escape(label) + '</div><div class="dridma-stat-value">'
        + escape(str(value)) + '</div></div>'
        for label, value in stats
    )
    st.markdown(f'<div class="dridma-stat-grid">{blocks}</div>', unsafe_allow_html=True)


def short_tournament_name(name: str) -> str:
    """Etiqueta compacta para las tablas de estadísticas por torneo."""
    original = str(name)
    year = re.search(r"\b(?:19|20)\d{2}\b", original)
    if not year:
        return original
    if re.search(r"\bsuper\s*cup\b", original, flags=re.IGNORECASE):
        return "SC" + year.group(0)[-2:]
    if re.search(r"\bmasters?\s*cup\b", original, flags=re.IGNORECASE):
        return "MC" + year.group(0)[-2:]
    return original


def player_tournament_table(source: pd.DataFrame, player: str, fields: list[str], kind: str) -> pd.DataFrame:
    rows = source.loc[source["Jugador"] == player]
    if rows.empty:
        return pd.DataFrame()
    grouped = rows.groupby("TORNEO", as_index=False)[fields].sum()
    if kind == "offense":
        grouped["AVG"] = divide(grouped["H"], grouped["AB"]).round(3)
        obp = divide(grouped["H"] + grouped["BB"] + grouped["HBP"],
                     grouped["AB"] + grouped["BB"] + grouped["HBP"] + grouped["SF"])
        slg = divide(grouped["TB"], grouped["AB"])
        grouped["OPS"] = ((obp.fillna(0) + slg.fillna(0)) * 1000).round().astype(int)
        grouped = grouped.rename(columns={"SO": "K"})
        return grouped[["TORNEO", "AVG", "OPS", "AB", "H", "R", "RBI", "HR", "BB", "K"]]
    if kind == "pitching":
        grouped["IP"] = (grouped["OUTS"] // 3).astype(str) + "." + (grouped["OUTS"] % 3).astype(str)
        grouped["EFE"] = divide(7 * grouped["ER"], grouped["OUTS"] / 3).round(2)
        return grouped[["TORNEO", "IP", "EFE", "K", "H", "BB", "R", "ER"]]
    return grouped[["TORNEO", "PO", "A", "E", "DP", "PB"]]


def plate_discipline_by_tournament(turns_df: pd.DataFrame, pitches_df: pd.DataFrame,
                                   player: str, name_map: dict[str, str]) -> pd.DataFrame:
    """P/PA y swing en el primer lanzamiento, solo PA confirmadas de DRI.

    Cada PA cuenta una vez (Turno_ID). Los lanzamientos se enlazan por Turno_ID,
    y las tasas globales se calculan con numeradores/denominadores agregados.
    """
    required_turns = {"Turno_ID", "TORNEO", "Equipo_Bateador", "Bateador", "PA_Confirmada", "Resultado", "B2_Inicial", "B3_Inicial"}
    required_pitches = {"Turno_ID", "Pitch_No", "Tipo_Evento", "Evento"}
    if not required_turns.issubset(turns_df.columns) or not required_pitches.issubset(pitches_df.columns):
        return pd.DataFrame(columns=["TORNEO", "P/PA", "1st Pitch Swing%", "AVG", "AVG RISP"])
    turns = turns_df.copy()
    turns = turns.loc[turns["Equipo_Bateador"].astype(str).str.strip().str.upper().eq("DRI")]
    normalized = turns["Bateador"].astype(str).str.strip()
    normalized = normalized.map(name_map).fillna(normalized)
    turns = turns.loc[normalized.eq(player) & turns["PA_Confirmada"].astype(str).str.lower().isin(["true", "1", "yes"])].copy()
    turns = turns.drop_duplicates(subset=["Turno_ID"])
    if turns.empty:
        return pd.DataFrame(columns=["TORNEO", "P/PA", "1st Pitch Swing%", "AVG", "AVG RISP"])

    pitches = pitches_df.loc[pitches_df["Turno_ID"].isin(turns["Turno_ID"])].copy()
    pitches["Pitch_No"] = pd.to_numeric(pitches["Pitch_No"], errors="coerce")
    pitches = pitches.dropna(subset=["Pitch_No"]).drop_duplicates(subset=["Turno_ID", "Pitch_No"])
    counts = pitches.groupby("Turno_ID").size().rename("Pitches")
    first = pitches.loc[pitches["Pitch_No"].eq(1)].copy()
    # Un swing puede resultar en foul, swing fallido o pelota puesta en juego.
    # No contar strikes cantados, bolas, HBP ni lanzamientos sin evidencia de swing.
    event = first["Tipo_Evento"].fillna("").astype(str).str.lower() + " " + first["Evento"].fillna("").astype(str).str.lower()
    swing = event.str.contains(r"swing|foul|abanic|batazo|en juego|in play|hit into play|single|double|triple|home run|ground|fly|line|pop", regex=True)
    first = first.assign(Swing=swing).set_index("Turno_ID")["Swing"]
    turns = turns.join(counts, on="Turno_ID").join(first, on="Turno_ID")
    # No usar PA sin un primer lanzamiento registrado para evitar denominadores sesgados.
    turns = turns.dropna(subset=["Pitches", "Swing"])
    if turns.empty:
        return pd.DataFrame(columns=["TORNEO", "P/PA", "1st Pitch Swing%", "AVG", "AVG RISP"])
    turns["Swing"] = turns["Swing"].astype(bool).astype(int)
    # El estado de las bases corresponde al INICIO de la aparición.
    # Se clasifican únicamente los resultados oficiales interpretables.
    stats = turns["Resultado"].map(lambda value: offensive_event_stats(value, True))
    turns["AB"] = stats.map(lambda v: v[0] if v is not None else 0)
    turns["H"] = stats.map(lambda v: v[1] if v is not None else 0)
    b2 = pd.to_numeric(turns["B2_Inicial"], errors="coerce").fillna(0)
    b3 = pd.to_numeric(turns["B3_Inicial"], errors="coerce").fillna(0)
    turns["RISP"] = b2.gt(0) | b3.gt(0)
    turns["AB_RISP"] = turns["AB"].where(turns["RISP"], 0)
    turns["H_RISP"] = turns["H"].where(turns["RISP"], 0)
    totals = turns.groupby("TORNEO", as_index=False).agg(PA=("Turno_ID", "size"),
                                                         Pitches=("Pitches", "sum"),
                                                         FirstSwings=("Swing", "sum"),
                                                         AB=("AB", "sum"), H=("H", "sum"),
                                                         AB_RISP=("AB_RISP", "sum"), H_RISP=("H_RISP", "sum"))
    total = pd.DataFrame([{"TORNEO": "TOTAL", "PA": totals["PA"].sum(),
                           "Pitches": totals["Pitches"].sum(),
                           "FirstSwings": totals["FirstSwings"].sum(),
                           "AB": totals["AB"].sum(), "H": totals["H"].sum(),
                           "AB_RISP": totals["AB_RISP"].sum(), "H_RISP": totals["H_RISP"].sum()}])
    totals = pd.concat([totals, total], ignore_index=True)
    totals["P/PA"] = (totals["Pitches"] / totals["PA"]).round(2)
    totals["1st Pitch Swing%"] = (100 * totals["FirstSwings"] / totals["PA"]).map(lambda x: f"{x:.1f}%")
    totals["AVG"] = divide(totals["H"], totals["AB"]).round(3)
    totals["AVG RISP"] = divide(totals["H_RISP"], totals["AB_RISP"]).round(3)
    totals["TORNEO"] = totals["TORNEO"].map(lambda t: "TOTAL" if t == "TOTAL" else short_tournament_name(t))
    return totals[["TORNEO", "P/PA", "1st Pitch Swing%", "AVG", "AVG RISP"]]


def offensive_count_performance(turns_df: pd.DataFrame, pitches_df: pd.DataFrame,
                                player: str, name_map: dict[str, str]) -> pd.DataFrame:
    """AB y hits por conteo previo al último lanzamiento de cada AB confirmado.

    Se excluyen bases por bolas, pelotazos y sacrificios sin AB. Los resultados
    no clasificables no se cuentan como outs ni como turnos oficiales.
    """
    columns = ["Conteo", "AB", "H", "AVG"]
    required_t = {"Turno_ID", "Equipo_Bateador", "Bateador", "PA_Confirmada", "Resultado"}
    required_p = {"Turno_ID", "Pitch_No", "Bolas_Antes", "Strikes_Antes"}
    if not required_t.issubset(turns_df.columns) or not required_p.issubset(pitches_df.columns):
        return pd.DataFrame(columns=columns)
    t = turns_df.copy()
    player_names = t["Bateador"].astype(str).str.strip()
    player_names = player_names.map(name_map).fillna(player_names)
    t = t.loc[t["Equipo_Bateador"].astype(str).str.strip().str.upper().eq("DRI")
              & player_names.eq(player)
              & t["PA_Confirmada"].astype(str).str.lower().isin(["true", "1", "yes"])].copy()
    t = t.drop_duplicates("Turno_ID")
    if t.empty:
        return pd.DataFrame(columns=columns)
    p = pitches_df.loc[pitches_df["Turno_ID"].isin(t["Turno_ID"])].copy()
    for col in ["Pitch_No", "Bolas_Antes", "Strikes_Antes"]:
        p[col] = pd.to_numeric(p[col], errors="coerce")
    p = p.dropna(subset=["Pitch_No", "Bolas_Antes", "Strikes_Antes"])
    p = p.sort_values("Pitch_No").drop_duplicates("Turno_ID", keep="last")
    t = t.merge(p[["Turno_ID", "Bolas_Antes", "Strikes_Antes"]], on="Turno_ID", how="inner")
    t = t.loc[t["Bolas_Antes"].between(0, 3) & t["Strikes_Antes"].between(0, 2)].copy()
    if t.empty:
        return pd.DataFrame(columns=columns)
    t["Conteo"] = t["Bolas_Antes"].astype(int).astype(str) + "-" + t["Strikes_Antes"].astype(int).astype(str)
    parsed = t["Resultado"].map(lambda result: offensive_event_stats(result, True))
    # AB es el indicador oficial del evento: las PA sin AB no participan.
    t["AB"] = parsed.map(lambda v: v[0] if v is not None else 0)
    t["H"] = parsed.map(lambda v: v[1] if v is not None else 0)
    t = t.loc[t["AB"].eq(1)].copy()
    if t.empty:
        return pd.DataFrame(columns=columns)
    group = t.groupby("Conteo", as_index=False).agg(AB=("AB", "sum"), H=("H", "sum"))
    group["AVG"] = divide(group["H"], group["AB"]).round(3)
    # Ordenar por AB descendente; desempatar por H y luego por conteo.
    group = group.sort_values(["AB", "H", "Conteo"], ascending=[False, False, True])
    total_ab = int(group["AB"].sum())
    total_h = int(group["H"].sum())
    total = {"Conteo": "TOTAL", "AB": total_ab, "H": total_h,
             "AVG": round(total_h / total_ab, 3) if total_ab else float("nan")}
    return pd.concat([group[columns], pd.DataFrame([total], columns=columns)], ignore_index=True)


def offensive_event_stats(result: str, confirmed: bool) -> tuple[int, int, int, int, int] | None:
    """AB, H, HR, BB, SO for a confirmed plate appearance."""
    if not confirmed or not isinstance(result, str) or not result.strip():
        return None
    text = result.lower()
    # Walks count as BB but not AB; strikeouts count as AB and SO.
    if re.search(r"\bwalks?\b|\bintentional(?:ly)? walked\b", text):
        return (0, 0, 0, 1, 0)
    if re.search(r"\bstrikes? out\b|\bstruck out\b", text):
        return (1, 0, 0, 0, 1)
    # HBP, sacrifices and interference do not count as AB or BB.
    if (re.search(r"\bhit by pitch\b|\bhit by a pitch\b|\bcatcher.s interference\b", text)
        or re.search(r"\bsacrific(?:e|es|ed|ing)\b|\bsac fly\b|\bsac bunt\b", text)):
        return (0, 0, 0, 0, 0)
    if re.search(r"\bhomers?\b|\bhome runs?\b", text):
        return (1, 1, 1, 0, 0)
    if re.search(r"\bsingles?\b|\bdoubles?\b|\btriples?\b", text):
        return (1, 1, 0, 0, 0)
    # Reached on error / fielder's choice are official AB, not hits.
    if re.search(r"\breaches? on\b|\bfielder.s choice\b|\bstrikes? out\b|\bgrounds? out\b|\bflies? out\b|\blines? out\b|\bpops? out\b|\bfouls? out\b|\bdouble play\b|\btriple play\b", text):
        return (1, 0, 0, 0, 0)
    return None


def short_pitcher_name(full_name: str) -> str:
    """Formato visual común para lanzadores y jugadores."""
    return short_source_name(full_name)


def offense_by_pitcher(turns_df: pd.DataFrame, player: str, name_map: dict[str, str]) -> tuple[pd.DataFrame, int]:
    """Aggregate offensive outcomes by opposing pitcher, using the selected tournaments."""
    required = {"Bateador", "Lanzador", "Lanzador_ID", "Equipo_Bateador", "Resultado", "PA_Confirmada", "Equipo_Lanzador"}
    if not required.issubset(turns_df.columns):
        return pd.DataFrame(columns=["Lanzador", "Equipo", "AB", "H", "HR", "RBI", "BB", "SO", "AVG"]), 0
    data = turns_df.loc[turns_df["Equipo_Bateador"].astype(str).str.strip().str.upper().eq("DRI")].copy()
    data["Bateador_normalizado"] = data["Bateador"].astype(str).str.strip().map(name_map).fillna(data["Bateador"].astype(str).str.strip())
    data = data.loc[data["Bateador_normalizado"].eq(player)]
    if data.empty:
        return pd.DataFrame(columns=["Lanzador", "Equipo", "AB", "H", "HR", "RBI", "BB", "SO", "AVG"]), 0
    records = []
    unresolved = 0
    for _, row in data.iterrows():
        confirmed = str(row["PA_Confirmada"]).strip().lower() in ("true", "1", "yes")
        stats = offensive_event_stats(row["Resultado"], confirmed)
        if stats is None:
            unresolved += 1
            continue
        pitcher_id = str(row["Lanzador_ID"]).strip() if pd.notna(row["Lanzador_ID"]) else ""
        pitcher_name = str(row["Lanzador"]).strip() if pd.notna(row["Lanzador"]) else "Desconocido"
        records.append({"Lanzador_ID": pitcher_id or pitcher_name, "Lanzador": pitcher_name, "Equipo": str(row["Equipo_Lanzador"]).strip().upper() if pd.notna(row["Equipo_Lanzador"]) else "",
                        "AB": stats[0], "H": stats[1], "HR": stats[2], "RBI": int(re.search(r"\b(\d+)\s+RBI\b", row["Resultado"], re.IGNORECASE).group(1)) if isinstance(row["Resultado"], str) and re.search(r"\b(\d+)\s+RBI\b", row["Resultado"], re.IGNORECASE) else 0, "BB": stats[3], "SO": stats[4]})
    if not records:
        return pd.DataFrame(columns=["Lanzador", "Equipo", "AB", "H", "HR", "RBI", "BB", "SO", "AVG"]), unresolved
    summary = pd.DataFrame(records).groupby(["Lanzador_ID", "Equipo"], as_index=False).agg(
        {"Lanzador": "first", "AB": "sum", "H": "sum", "HR": "sum", "RBI": "sum", "BB": "sum", "SO": "sum"})
    summary["Lanzador"] = summary["Lanzador"].map(short_pitcher_name)
    summary["AVG"] = divide(summary["H"], summary["AB"]).round(3)
    summary = summary.sort_values(["AB", "H", "Lanzador"], ascending=[False, False, True])
    return summary[["Lanzador", "Equipo", "AB", "H", "HR", "RBI", "BB", "SO", "AVG"]], unresolved



# ETAPA 2: navegación y fichas individuales por categoría.
def tournament_filter(key: str, available: list[str]) -> list[str]:
    """Filtro independiente; botones y casillas coherentes entre reruns de Streamlit."""
    available = list(available)
    state_key = f"{key}_selected"
    if state_key not in st.session_state:
        st.session_state[state_key] = available.copy()
    st.session_state[state_key] = [t for t in st.session_state[state_key] if t in available]

    def choose_all():
        st.session_state[state_key] = available.copy()
        for t in available:
            st.session_state[f"{key}_check_{t}"] = True

    def choose_none():
        st.session_state[state_key] = []
        for t in available:
            st.session_state[f"{key}_check_{t}"] = False

    def change_check(t):
        current = set(st.session_state[state_key])
        if st.session_state[f"{key}_check_{t}"]:
            current.add(t)
        else:
            current.discard(t)
        st.session_state[state_key] = [item for item in available if item in current]

    with st.expander(f"Seleccionar torneos · {len(st.session_state[state_key])} de {len(available)}", expanded=False):
        a, b = st.columns(2)
        a.button("Todos", key=f"{key}_all", use_container_width=True, on_click=choose_all)
        b.button("Ninguno", key=f"{key}_none", use_container_width=True, on_click=choose_none)
        for t in available:
            widget_key = f"{key}_check_{t}"
            if widget_key not in st.session_state:
                st.session_state[widget_key] = t in st.session_state[state_key]
            st.checkbox(str(t), key=widget_key, on_change=change_check, args=(t,))
    return list(st.session_state[state_key])


def aggregate_tables(offense: pd.DataFrame, defense: pd.DataFrame, pitching: pd.DataFrame):
    """Conserva las fórmulas y las columnas de las tablas originales."""
    offense_fields = ["AB", "H", "BB", "R", "RBI", "SO", "2B", "3B", "HR", "TB", "HBP", "SH", "SF", "IBB", "SB", "CS"]
    defense_fields = ["A", "PO", "E", "DP", "PB"]
    pitching_fields = ["H", "R", "ER", "BB", "K", "Picheos", "Strikes"]
    offense = numeric(offense, offense_fields)
    offense_table = offense.groupby("Jugador", as_index=False)[offense_fields].sum()
    offense_table["AVG"] = divide(offense_table["H"], offense_table["AB"]).round(3)
    obp = divide(offense_table["H"] + offense_table["BB"] + offense_table["HBP"],
                 offense_table["AB"] + offense_table["BB"] + offense_table["HBP"] + offense_table["SF"])
    slg = divide(offense_table["TB"], offense_table["AB"])
    offense_table["OPS"] = ((obp.fillna(0) + slg.fillna(0)) * 1000).round().astype(int)
    offense_table = offense_table.rename(columns={"SO": "K"})
    defense = numeric(defense, defense_fields)
    defense_table = defense.groupby("Jugador", as_index=False)[defense_fields].sum()
    pitching = numeric(pitching, pitching_fields + ["IP"])
    whole_innings = pitching["IP"].astype(int)
    partial_outs = ((pitching["IP"] - whole_innings) * 10).round().astype(int)
    if not partial_outs.isin([0, 1, 2]).all():
        st.error("Hay valores de IP no válidos en db_Picheo.")
        st.stop()
    pitching["OUTS"] = whole_innings * 3 + partial_outs
    pitching_table = pitching.groupby("Jugador", as_index=False)[pitching_fields + ["OUTS"]].sum()
    pitching_table["IP"] = (pitching_table["OUTS"] // 3).astype(str) + "." + (pitching_table["OUTS"] % 3).astype(str)
    pitching_table["EFE"] = divide(7 * pitching_table["ER"], pitching_table["OUTS"] / 3).round(2)
    return offense, defense, pitching, offense_table, defense_table, pitching_table, offense_fields, defense_fields, pitching_fields


for frame in (offense, defense, pitching):
    frame["Jugador"] = frame["Jugador"].astype(str).str.strip()
    frame["Jugador"] = frame["Jugador"].map(mapping).fillna(frame["Jugador"])

tournaments = sorted(results["TORNEO"].dropna().unique().tolist())
all_players = sorted(set(offense["Jugador"]) | set(defense["Jugador"]) | set(pitching["Jugador"]))
def save_team_tab():
    st.session_state["dridma_team_tab_saved"] = st.session_state["dridma_team_tab"]

def save_player_tab():
    st.session_state["dridma_player_tab_saved"] = st.session_state["dridma_player_tab"]

main = st.segmented_control("Sección", ["Equipo", "Jugadores"], default="Equipo",
                            key="dridma_main_menu", label_visibility="collapsed")

# Glosario único y global.
with st.expander("❔ ¿Qué significan las abreviaturas?", expanded=False):
    st.caption("Consulta las abreviaturas utilizadas en las tablas.")
    glossary_groups = {
        "Ofensiva": ["AB", "H", "2B", "3B", "HR", "RBI", "R", "BB", "SO", "K", "AVG", "OBP", "SLG", "OPS", "TB", "HBP", "SH", "SF", "IBB", "SB", "CS"],
        "Defensiva": ["PO", "A", "E", "DP", "PB"],
        "Picheo": ["IP", "H", "R", "ER", "BB", "K", "EFE", "Picheos", "Strikes"],
    }
    for group_name, abbreviations in glossary_groups.items():
        st.markdown(f"**{group_name}**")
        glossary_df = pd.DataFrame({"Abreviatura": abbreviations,
                                    "Significado": [STAT_HELP[abbr] for abbr in abbreviations]})
        st.dataframe(glossary_df, hide_index=True, use_container_width=True,
                     column_config={"Abreviatura": st.column_config.TextColumn(width="small"),
                                    "Significado": st.column_config.TextColumn(width="large")})
    st.markdown("**Torneos**")
    st.dataframe(pd.DataFrame({"Código": ["SC25", "SC26", "MC25", "MC26"],
                               "Torneo": ["Super Cup 2025", "Super Cup 2026", "Masters Cup 2025", "Masters Cup 2026"]}),
                 hide_index=True, use_container_width=True)


if main == "Equipo":
    selected = tournament_filter("dridma_team", tournaments)
    if not selected:
        st.info("Selecciona al menos un torneo para visualizar las estadísticas.")
    else:
        o = offense.loc[offense["TORNEO"].isin(selected)].copy()
        d = defense.loc[defense["TORNEO"].isin(selected)].copy()
        p = pitching.loc[pitching["TORNEO"].isin(selected)].copy()
        r = results.loc[results["TORNEO"].isin(selected)].copy()
        o, d, p, offense_table, defense_table, pitching_table, offense_fields, defense_fields, pitching_fields = aggregate_tables(o, d, p)
        r[["Carreras", "Carreras2"]] = r[["Carreras", "Carreras2"]].apply(pd.to_numeric, errors="coerce")
        wins = ((r["Equipo 1"].eq("DRI") & (r["Carreras"] > r["Carreras2"])) |
                (r["Equipo 2"].eq("DRI") & (r["Carreras2"] > r["Carreras"]))).sum()
        losses = ((r["Equipo 1"].eq("DRI") & (r["Carreras"] < r["Carreras2"])) |
                  (r["Equipo 2"].eq("DRI") & (r["Carreras2"] < r["Carreras"]))).sum()
        items = "".join(
            f'<div class="dridma-kpi"><div class="dridma-kpi-label">{escape(label)}</div>'
            f'<div class="dridma-kpi-value">{value}</div></div>'
            for label, value in [("Partidos", len(r)), ("Victorias", int(wins)), ("Derrotas", int(losses))]
        )
        st.markdown(f'<div class="dridma-kpis">{items}</div>', unsafe_allow_html=True)
        if "dridma_team_tab" not in st.session_state:
            st.session_state["dridma_team_tab"] = st.session_state.get("dridma_team_tab_saved", "Ofensiva")
        tab = st.segmented_control("Estadísticas del equipo",
                 ["Ofensiva", "Defensiva", "Picheo", "Scores"], default="Ofensiva",
                 key="dridma_team_tab", label_visibility="collapsed", on_change=save_team_tab)
        if tab == "Ofensiva":
            render_table(offense_table.sort_values(["AVG", "H"], ascending=False),
                ["Jugador", "AVG", "OPS", "AB", "H", "R", "RBI", "BB", "K", "2B", "3B", "HR", "TB", "HBP", "SH", "SF", "IBB", "SB", "CS"], {"AVG": ".3f"})
        elif tab == "Defensiva":
            render_table(defense_table.sort_values("PO", ascending=False), ["Jugador", "PO", "A", "E", "DP", "PB"])
        elif tab == "Picheo":
            render_table(pitching_table.sort_values("K", ascending=False),
                ["Jugador", "IP", "EFE", "K", "H", "BB", "R", "ER", "Picheos", "Strikes"], {"EFE": ".2f"})
        else:
            render_games(r.sort_values("Fecha"))
else:
    def remember_player():
        st.session_state["dridma_player_saved"] = st.session_state["dridma_player"]

    if "dridma_player" not in st.session_state:
        st.session_state["dridma_player"] = st.session_state.get("dridma_player_saved")
    player = st.selectbox("Buscar jugador", all_players, index=None,
                          placeholder="Escribe para buscar un jugador...", key="dridma_player",
                          on_change=remember_player)
    if player is None:
        st.caption("Selecciona un jugador para consultar sus estadísticas.")
    else:
        available = sorted(set(offense.loc[offense["Jugador"].eq(player), "TORNEO"]) |
                           set(defense.loc[defense["Jugador"].eq(player), "TORNEO"]) |
                           set(pitching.loc[pitching["Jugador"].eq(player), "TORNEO"]))
        if st.session_state.get("dridma_previous_player") != player:
            st.session_state["dridma_player_tournaments_selected"] = list(available)
            st.session_state["dridma_previous_player"] = player
            # Sincronizar widgets de casillas antes de crearlos.
            for t in tournaments:
                st.session_state[f"dridma_player_tournaments_check_{t}"] = t in available
        selected = tournament_filter("dridma_player_tournaments", available)
        if not selected:
            st.info("Selecciona al menos un torneo para visualizar las estadísticas.")
        else:
            player_offense = offense.loc[offense["TORNEO"].isin(selected)].copy()
            player_defense = defense.loc[defense["TORNEO"].isin(selected)].copy()
            player_pitching = pitching.loc[pitching["TORNEO"].isin(selected)].copy()
            player_turns = turns.loc[turns["TORNEO"].isin(selected)].copy()
            player_pitches = pitches.loc[pitches["TORNEO"].isin(selected)].copy()
            player_offense, player_defense, player_pitching, offense_table, defense_table, pitching_table, offense_fields, defense_fields, pitching_fields = aggregate_tables(
                player_offense, player_defense, player_pitching
            )
            o = offense_table.loc[offense_table["Jugador"] == player]
            d = defense_table.loc[defense_table["Jugador"] == player]
            p = pitching_table.loc[pitching_table["Jugador"] == player]
            available_tabs = [name for name, frame in [("Ofensiva", o), ("Defensiva", d), ("Picheo", p)] if not frame.empty]
            if not available_tabs:
                st.info("No hay estadísticas disponibles para este jugador en los torneos seleccionados.")
            else:
                previous_tab = st.session_state.get("dridma_player_tab", st.session_state.get("dridma_player_tab_saved"))
                if previous_tab not in available_tabs:
                    previous_tab = available_tabs[0]
                st.session_state["dridma_player_tab"] = previous_tab
                st.markdown(
                    '<div class="dridma-profile">'
                    '<div class="dridma-profile-label">DRIDMA RIVAS · JUGADORES</div>'
                    f'<div class="dridma-profile-name">{escape(player)}</div>'
                    f'<div class="dridma-profile-sub">{len(selected)} torneo(s) seleccionado(s)</div>'
                    '</div>', unsafe_allow_html=True
                )
                tab = st.segmented_control("Estadísticas del jugador", available_tabs,
                                           key="dridma_player_tab", label_visibility="collapsed", on_change=save_player_tab)
                if tab == "Ofensiva":
                    r = o.iloc[0]
                    stat_cards([("AVG", f'{r["AVG"]:.3f}' if pd.notna(r["AVG"]) else "—"),
                                ("OPS", str(int(r["OPS"]))), ("HR", str(int(r["HR"])))])
                    render_table(o, ["Jugador", "AB", "H", "R", "RBI", "BB", "K", "2B", "3B", "TB", "HBP", "SH", "SF", "IBB", "SB", "CS"])
                    detail = player_tournament_table(player_offense, player, offense_fields, "offense")
                    if not detail.empty:
                        with st.expander("Ofensiva por torneo"):
                            detail_display = detail.copy()
                            detail_display["TORNEO"] = detail_display["TORNEO"].map(short_tournament_name)
                            render_table(detail_display, list(detail_display.columns), {"AVG": ".3f"})
                    # Ambos detalles parten de los mismos turnos confirmados de DRIDMA.
                    versus, unresolved = offense_by_pitcher(player_turns, player, mapping)
                    total_cols = ["AB", "H", "HR", "RBI", "BB", "SO"]

                    def add_total_row(frame: pd.DataFrame, label_column: str) -> pd.DataFrame:
                        totals = frame[total_cols].sum()
                        total_ab, total_h = int(totals["AB"]), int(totals["H"])
                        total_row = {col: int(totals[col]) for col in total_cols}
                        total_row[label_column] = "TOTAL"
                        if label_column == "Lanzador":
                            total_row["Equipo"] = ""
                        total_row["AVG"] = round(total_h / total_ab, 3) if total_ab else float("nan")
                        return pd.concat([frame, pd.DataFrame([total_row])], ignore_index=True)

                    with st.expander("Detalle contra equipos"):
                        if versus.empty:
                            st.caption("No hay turnos confirmados contra equipos rivales en los torneos seleccionados.")
                        else:
                            by_team = versus.groupby("Equipo", as_index=False)[total_cols].sum()
                            by_team["AVG"] = divide(by_team["H"], by_team["AB"]).round(3)
                            by_team = by_team.sort_values(["AB", "H", "Equipo"], ascending=[False, False, True])
                            team_display = add_total_row(by_team, "Equipo")
                            render_table(team_display, ["Equipo", *total_cols, "AVG"], {"AVG": ".3f"})
                        if unresolved:
                            st.caption(f"{unresolved} aparición(es) sin resultado confirmado o clasificable, excluidas de esta tabla.")

                    with st.expander("Detalle contra lanzadores"):
                        if versus.empty:
                            st.caption("No hay turnos confirmados contra lanzadores en los torneos seleccionados.")
                        else:
                            versus_display = add_total_row(versus, "Lanzador")
                            render_table(versus_display, ["Lanzador", "Equipo", *total_cols, "AVG"], {"AVG": ".3f"})
                        if unresolved:
                            st.caption(f"{unresolved} aparición(es) sin resultado confirmado o clasificable, excluidas de esta tabla.")

                    with st.expander("Disciplina al plato por torneo", expanded=False):
                        discipline = plate_discipline_by_tournament(player_turns, player_pitches, player, mapping)
                        if discipline.empty:
                            st.caption("No hay apariciones confirmadas con lanzamientos registrados para este jugador.")
                        else:
                            render_table(discipline, ["TORNEO", "P/PA", "1st Pitch Swing%", "AVG", "AVG RISP"], {"P/PA": ".2f", "AVG": ".3f", "AVG RISP": ".3f"})

                    with st.expander("Rendimiento ofensivo según conteo", expanded=False):
                        count_table = offensive_count_performance(player_turns, player_pitches, player, mapping)
                        if count_table.empty:
                            st.caption("No hay apariciones confirmadas con conteo final disponible.")
                        else:
                            render_count_performance(count_table)
                            st.caption("Solo turnos oficiales al bate (AB), agrupados por el conteo anterior al lanzamiento final. Se excluyen bases por bolas, pelotazos y sacrificios sin AB.")

                elif tab == "Defensiva":
                    r = d.iloc[0]
                    stat_cards([("PO", str(int(r["PO"]))), ("A", str(int(r["A"]))), ("E", str(int(r["E"])))])
                    render_table(d, ["Jugador", "PO", "A", "E", "DP", "PB"])
                    detail = player_tournament_table(player_defense, player, defense_fields, "defense")
                    if not detail.empty:
                        with st.expander("Defensiva por torneo"):
                            detail_display = detail.copy()
                            detail_display["TORNEO"] = detail_display["TORNEO"].map(short_tournament_name)
                            render_table(detail_display, list(detail_display.columns))

                elif tab == "Picheo":
                    r = p.iloc[0]
                    stat_cards([("IP", str(r["IP"])),
                                ("EFE", f'{r["EFE"]:.2f}' if pd.notna(r["EFE"]) else "—"),
                                ("K", str(int(r["K"])))])
                    render_table(p, ["Jugador", "IP", "EFE", "K", "H", "BB", "R", "ER", "Picheos", "Strikes"], {"EFE": ".2f"})
                    detail = player_tournament_table(player_pitching, player, pitching_fields + ["OUTS"], "pitching")
                    if not detail.empty:
                        with st.expander("Picheo por torneo"):
                            render_table(detail, list(detail.columns), {"EFE": ".2f"})
st.markdown('<div class="dridma-footer">DRIDMA RIVAS · Estadísticas del equipo</div>', unsafe_allow_html=True)
