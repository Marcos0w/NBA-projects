import streamlit as st
import pandas as pd
import plotly.express as px
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from streamlit_option_menu import option_menu

#  Dados principais
CANDIDATOS_MVP = [
    "Nikola Jokic", "Luka Doncic", "Giannis Antetokounmpo",
    "Jayson Tatum", "Shai Gilgeous-Alexander"
]

FOTOS_JOGADORES = {
    "Nikola Jokic": "https://a.espncdn.com/i/headshots/nba/players/full/3112335.png",
    "Luka Doncic": "https://a.espncdn.com/i/headshots/nba/players/full/3945274.png",
    "Giannis Antetokounmpo": "https://a.espncdn.com/i/headshots/nba/players/full/3032977.png",
    "Jayson Tatum": "https://a.espncdn.com/i/headshots/nba/players/full/4065648.png",
    "Shai Gilgeous-Alexander": "https://a.espncdn.com/i/headshots/nba/players/full/4278073.png"
}

LOGOS_TIMES = {
    "Nikola Jokic": "https://a.espncdn.com/i/teamlogos/nba/500/den.png",
    "Luka Doncic": "https://a.espncdn.com/i/teamlogos/nba/500/dal.png",
    "Giannis Antetokounmpo": "https://a.espncdn.com/i/teamlogos/nba/500/mil.png",
    "Jayson Tatum": "https://a.espncdn.com/i/teamlogos/nba/500/bos.png",
    "Shai Gilgeous-Alexander": "https://a.espncdn.com/i/teamlogos/nba/500/okc.png"
}

#  Função para buscar dados do jogador
@st.cache_data
def buscar_dados(nome):
    try:
        jogador_info = players.find_players_by_full_name(nome)[0]
        log = playergamelog.PlayerGameLog(player_id=jogador_info['id'], season='2023-24')
        df = log.get_data_frames()[0]
        df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
        return df.sort_values('GAME_DATE')
    except:
        return pd.DataFrame()

#  Exibir perfil
def mostrar_perfil(jogador):
    st.markdown("""
        <style>
            .perfil-container {
                display: flex;
                align-items: center;
                gap: 30px;
                background-color: #1f1f1f;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            .foto-jogador { border-radius: 10px; width: 200px; }
            .logo-time { width: 80px; }
            .nome-jogador {
                font-size: 28px; color: #FAFAFA;
                font-weight: bold; margin-top: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="perfil-container">
            <img src="{LOGOS_TIMES[jogador]}" class="logo-time">
            <div>
                <img src="{FOTOS_JOGADORES[jogador]}" class="foto-jogador">
                <div class="nome-jogador">{jogador}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

#  Estatísticas individuais
def mostrar_estatisticas(jogador):
    df = buscar_dados(jogador)
    if df.empty:
        st.warning("Sem dados disponíveis para este jogador.")
        return
    estatistica = st.selectbox("Escolha a estatística:", ['PTS', 'REB', 'AST'])
    fig = px.line(df, x='GAME_DATE', y=estatistica, title=f"{jogador} - {estatistica} por Jogo")
    st.plotly_chart(fig)
    st.dataframe(df[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST']])

#  Comparar jogadores
def comparar_jogadores(j1, j2):
    df1, df2 = buscar_dados(j1), buscar_dados(j2)
    if df1.empty or df2.empty:
        st.warning("Dados insuficientes para comparação.")
        return
    fig = px.line(df1, x='GAME_DATE', y='PTS', title="Comparação de Pontos")
    fig.add_scatter(x=df2['GAME_DATE'], y=df2['PTS'], mode='lines', name=j2)
    st.plotly_chart(fig)

#  Ranking por média de pontos
def mostrar_ranking():
    st.markdown("### Ranking de Média de Pontos - Temporada 2023–24")
    medias = {
        nome: round(buscar_dados(nome)['PTS'].mean(), 1)
        for nome in CANDIDATOS_MVP if not buscar_dados(nome).empty
    }
    ranking = pd.DataFrame.from_dict(medias, orient='index', columns=['Média de Pontos'])
    ranking = ranking.sort_values(by='Média de Pontos', ascending=False)
    st.dataframe(ranking)

    for nome in ranking.index:
        st.image(LOGOS_TIMES[nome], width=50)
        st.write(f"{nome}: {ranking.loc[nome, 'Média de Pontos']}")

#  Menu lateral
with st.sidebar:
    escolha = option_menu("Menu", ["Perfil", "Estatísticas", "Comparar", "Ranking"],
                          icons=["person", "bar-chart", "people", "trophy"],
                          menu_icon="cast", default_index=0)

#  Execução das seções
if escolha == "Perfil":
    jogador = st.selectbox("Selecione um jogador:", CANDIDATOS_MVP)
    mostrar_perfil(jogador)

elif escolha == "Estatísticas":
    jogador = st.selectbox("Selecione um jogador:", CANDIDATOS_MVP)
    mostrar_estatisticas(jogador)

elif escolha == "Comparar":
    col1, col2 = st.columns(2)
    with col1:
        jogador1 = st.selectbox("Jogador 1", CANDIDATOS_MVP, key="j1")
    with col2:
        jogador2 = st.selectbox("Jogador 2", [j for j in CANDIDATOS_MVP if j != jogador1], key="j2")
    comparar_jogadores(jogador1, jogador2)

elif escolha == "Ranking":
    mostrar_ranking()
