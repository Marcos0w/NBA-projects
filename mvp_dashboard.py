import streamlit as st
import pandas as pd
import plotly.express as px
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog

# Título estilizado com Bootstrap
st.markdown("""
    <div style='background-color:#1f77b4;padding:10px;border-radius:10px'>
        <h2 style='color:white;text-align:center;'>Corrida do MVP da NBA 🏀</h2>
    </div>
""", unsafe_allow_html=True)

# Menu lateral com streamlit-option-menu
from streamlit_option_menu import option_menu

with st.sidebar:
    escolha = option_menu("Menu", ["Estatísticas", "Comparar Jogadores", "Ranking"],
                          icons=["bar-chart", "people", "trophy"],
                          menu_icon="cast", default_index=0)

# Lista de candidatos
candidatos = ["Nikola Jokic", "Luka Doncic", "Giannis Antetokounmpo", "Jayson Tatum"]

# Função para buscar dados
def buscar_dados(nome):
    try:
        jogador_info = players.find_players_by_full_name(nome)[0]
        log = playergamelog.PlayerGameLog(player_id=jogador_info['id'], season='2024-25')
        df = log.get_data_frames()[0]
        df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
        df = df.sort_values('GAME_DATE')
        return df
    except:
        return pd.DataFrame()

# Seção: Estatísticas
if escolha == "Estatísticas":
    jogador = st.selectbox("Selecione um jogador:", candidatos)
    df = buscar_dados(jogador)

    if df.empty:
        st.warning("Sem dados disponíveis para este jogador.")
    else:
        estatistica = st.selectbox("Escolha a estatística:", ['PTS', 'REB', 'AST'])
        fig = px.line(df, x='GAME_DATE', y=estatistica, title=f"{jogador} - {estatistica} por Jogo")
        st.plotly_chart(fig)

        st.markdown("### Últimos jogos")
        st.dataframe(df[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST']])

# Seção: Comparar Jogadores
elif escolha == "Comparar Jogadores":
    col1, col2 = st.columns(2)
    with col1:
        jogador1 = st.selectbox("Jogador 1", candidatos, key="j1")
    with col2:
        jogador2 = st.selectbox("Jogador 2", [j for j in candidatos if j != jogador1], key="j2")

    df1 = buscar_dados(jogador1)
    df2 = buscar_dados(jogador2)

    if df1.empty or df2.empty:
        st.warning("Dados insuficientes para comparação.")
    else:
        fig = px.line(df1, x='GAME_DATE', y='PTS', title="Comparação de Pontos")
        fig.add_scatter(x=df2['GAME_DATE'], y=df2['PTS'], mode='lines', name=jogador2)
        st.plotly_chart(fig)

# Seção: Ranking
elif escolha == "Ranking":
    st.markdown("### Ranking de Média de Pontos")
    medias = {}
    for nome in candidatos:
        df = buscar_dados(nome)
        if not df.empty:
            medias[nome] = round(df['PTS'].mean(), 1)

    ranking = pd.DataFrame.from_dict(medias, orient='index', columns=['Média de Pontos'])
    ranking = ranking.sort_values(by='Média de Pontos', ascending=False)
    st.dataframe(ranking)

    st.success("Atualizado com dados da temporada 2024–25!")