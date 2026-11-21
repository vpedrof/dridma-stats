import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title='Dridma Rivas Stats', page_icon='🥎', layout='wide')
ROOT = Path(__file__).parent / 'data'

@st.cache_data
def read_data(name):
    return pd.read_csv(ROOT / f'{name}.csv', encoding='utf-8-sig')

def numeric(df, cols):
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

def divide(a, b):
    return a / b.where(b.ne(0))

st.title('🥎 DRIDMA RIVAS')
st.caption('Estadísticas oficiales del equipo · Prototipo de consulta')
try:
    offense = read_data('db_Ofensiva')
    defense = read_data('db_Defensiva')
    pitching = read_data('db_Picheo')
    results = read_data('db_Resultados')
    names = read_data('db_Nombres')
except (FileNotFoundError, pd.errors.EmptyDataError) as exc:
    st.error(f'No se pudieron cargar los datos: {exc}')
    st.stop()

mapping = dict(zip(names['Jugador'], names['Nombre']))
tournaments = sorted(results['TORNEO'].dropna().unique())
selected = st.multiselect('Torneos', tournaments, default=tournaments)
if not selected:
    st.info('Selecciona al menos un torneo.')
    st.stop()

offense = offense[offense['TORNEO'].isin(selected)].copy()
defense = defense[defense['TORNEO'].isin(selected)].copy()
pitching = pitching[pitching['TORNEO'].isin(selected)].copy()
results = results[results['TORNEO'].isin(selected)].copy()
for frame in (offense, defense, pitching):
    frame['Jugador'] = frame['Jugador'].map(mapping).fillna(frame['Jugador'])

wins = ((results['Equipo 1'].eq('DRI') & (results['Carreras'] > results['Carreras2'])) |
        (results['Equipo 2'].eq('DRI') & (results['Carreras2'] > results['Carreras']))).sum()
losses = ((results['Equipo 1'].eq('DRI') & (results['Carreras'] < results['Carreras2'])) |
          (results['Equipo 2'].eq('DRI') & (results['Carreras2'] < results['Carreras']))).sum()
a,b,c = st.columns(3)
a.metric('Partidos', len(results)); b.metric('Victorias', int(wins)); c.metric('Derrotas', int(losses))

t1,t2,t3,t4 = st.tabs(['Ofensiva', 'Defensiva', 'Picheo', 'Resultados'])
with t1:
    fields = ['AB','H','BB','R','RBI','SO','2B','3B','HR','TB','HBP','SH','SF','IBB','SB','CS']
    offense = numeric(offense, fields)
    table = offense.groupby('Jugador', as_index=False)[fields].sum()
    table['AVG'] = divide(table['H'], table['AB']).round(3)
    obp = divide(table['H'] + table['BB'] + table['HBP'], table['AB'] + table['BB'] + table['HBP'] + table['SF'])
    slg = divide(table['TB'], table['AB'])
    table['OPS'] = ((obp.fillna(0) + slg.fillna(0)) * 1000).round().astype(int)
    table = table.rename(columns={'SO':'K'})
    st.dataframe(table.sort_values(['AVG','H'], ascending=False), hide_index=True, use_container_width=True)
with t2:
    fields = ['A','PO','E','DP','PB']
    defense = numeric(defense, fields)
    table = defense.groupby('Jugador', as_index=False)[fields].sum()
    st.dataframe(table.sort_values('PO', ascending=False), hide_index=True, use_container_width=True)
with t3:
    fields = ['H','R','ER','BB','K','Picheos','Strikes']
    pitching = numeric(pitching, fields + ['IP'])
    # IP notation: 4.1 = 4 + 1/3; 4.2 = 4 + 2/3.
    outs = (pitching['IP'].astype(int) * 3 + ((pitching['IP'] * 10).round().astype(int) % 10))
    pitching['OUTS'] = outs
    table = pitching.groupby('Jugador', as_index=False)[fields + ['OUTS']].sum()
    table['IP'] = (table['OUTS'] // 3).astype(str) + '.' + (table['OUTS'] % 3).astype(str)
    table['EFE'] = divide(7 * table['ER'], table['OUTS'] / 3).round(2)
    table = table[['Jugador','IP','H','R','ER','BB','K','Picheos','Strikes','EFE']]
    st.dataframe(table.sort_values('K', ascending=False), hide_index=True, use_container_width=True)
with t4:
    results['Fecha'] = pd.to_datetime(results['Fecha'], errors='coerce').dt.strftime('%d/%m/%Y')
    cols = ['TORNEO','Fecha','Eq1','Carreras','Eq2','Carreras2']
    st.dataframe(results[cols], hide_index=True, use_container_width=True)

st.caption('Los indicadores se calculan sobre los registros filtrados. Datos publicados en el repositorio; no hay conexión automática con OneDrive todavía.')
