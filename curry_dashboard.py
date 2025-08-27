import streamlit as st
import pandas as pd
import plotly.express as px
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# Função para buscar ID do jogador
def get_player_id(name):
    player = [p for p in players.get_players() if p['full_name'] == name]
    return player[0]['id'] if player else None

# Função para buscar estatísticas de carreira
def get_stats(player_name):
    player_id = get_player_id(player_name)
    if not player_id:
        return None
    stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = stats.get_data_frames()[0]
    df = df[df['LEAGUE_ID'] == '00']  # Apenas NBA
    df['FG%'] = df['FG_PCT'] * 100
    df['3P%'] = df['FG3_PCT'] * 100
    df['Season'] = df['SEASON_ID'].str[:4] + '-' + df['SEASON_ID'].str[6:]
    return df

# Título
st.title("🏀 Curry vs. Lillard: Arremessos na NBA")

# Carregando dados
with st.spinner("Buscando dados da NBA..."):
    curry_df = get_stats("Stephen Curry")
    lillard_df = get_stats("Damian Lillard")

# Seleção de métrica
metric = st.selectbox("Escolha a métrica para comparar:", ["FG%", "3P%", "PTS"])

temporadas = sorted(list(set(curry_df['Season'])))
selecionadas = st.multiselect("Filtrar temporadas:", temporadas, default=temporadas)

curry_df = curry_df[curry_df['Season'].isin(selecionadas)]
lillard_df = lillard_df[lillard_df['Season'].isin(selecionadas)]

# Gráfico comparativo
fig = px.line(
    pd.concat([
        curry_df[['Season', metric]].assign(Player='Stephen Curry'),
        lillard_df[['Season', metric]].assign(Player='Damian Lillard')
    ]),
    x='Season', y=metric, color='Player',
    markers=True, title=f"{metric} por temporada"
)
st.plotly_chart(fig, use_container_width=True)

# Tabela de estatísticas
st.subheader("📋 Estatísticas resumidas")
st.dataframe(
    pd.concat([
        curry_df[['Season', 'GP', 'PTS', 'FG%', '3P%']].assign(Player='Stephen Curry'),
        lillard_df[['Season', 'GP', 'PTS', 'FG%', '3P%']].assign(Player='Damian Lillard')
    ]).sort_values(by='Season', ascending=False)
)


from nba_api.stats.endpoints import shotchartdetail
import matplotlib.pyplot as plt
import seaborn as sns

# Função para buscar dados de arremesso
@st.cache_data
def get_shot_data(player_id, season='2022-23'):
    shots = shotchartdetail.ShotChartDetail(
        team_id=0,
        player_id=player_id,
        season_type_all_star='Regular Season',
        season_nullable=season,
        context_measure_simple='FGA'
    )
    df = shots.get_data_frames()[0]
    return df

# Função para desenhar a quadra
def draw_court(ax=None, color='black', lw=2):
    from matplotlib.patches import Circle, Rectangle, Arc
    if ax is None:
        ax = plt.gca()
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)
    paint = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
    free_throw = Circle((0, 142.5), radius=60, linewidth=lw, color=color, fill=False)
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)
    ax.add_patch(hoop)
    ax.add_patch(backboard)
    ax.add_patch(paint)
    ax.add_patch(free_throw)
    ax.add_patch(three_arc)
    return ax
