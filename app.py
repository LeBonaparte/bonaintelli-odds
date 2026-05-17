import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="BonaIntelli | Odds Brasileirão",
    page_icon="⚽",
    layout="wide"
)

# ── Paleta de cores ─────────────────────────────────────────────────────────
AZUL_ESCURO  = "#0D1B2A"
AZUL_CARD    = "#152236"
AZUL_BORDA   = "#1E3148"
LARANJA      = "#C4621D"
LARANJA_SOFT = "#D4743A"
BRANCO       = "#FFFFFF"
CINZA        = "#8A9BB0"

# ── CSS personalizado ────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;600;700&family=Barlow+Condensed:wght@700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Barlow', sans-serif;
        background-color: {AZUL_ESCURO};
        color: {BRANCO};
    }}

    .stApp {{
        background-color: {AZUL_ESCURO};
    }}

    /* Header */
    .header {{
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 24px 0 8px 0;
        border-bottom: 2px solid {LARANJA};
        margin-bottom: 32px;
    }}
    .header-title {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: {BRANCO};
        letter-spacing: 1px;
    }}
    .header-subtitle {{
        font-size: 0.85rem;
        color: {CINZA};
        margin-top: 2px;
    }}
    .header-dot {{
        width: 12px;
        height: 12px;
        background: {LARANJA};
        border-radius: 50%;
        animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
        0%   {{ box-shadow: 0 0 0 0 rgba(196,98,29,0.6); }}
        70%  {{ box-shadow: 0 0 0 8px rgba(196,98,29,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(196,98,29,0); }}
    }}

    /* Cards de métricas */
    .metric-card {{
        background: {AZUL_CARD};
        border: 1px solid {AZUL_BORDA};
        border-left: 3px solid {LARANJA};
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }}
    .metric-label {{
        font-size: 0.75rem;
        color: {CINZA};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .metric-value {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: {BRANCO};
    }}
    .metric-sub {{
        font-size: 0.8rem;
        color: {LARANJA};
    }}

    /* Seções */
    .section-title {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: {BRANCO};
        letter-spacing: 1px;
        text-transform: uppercase;
        border-left: 3px solid {LARANJA};
        padding-left: 12px;
        margin: 32px 0 16px 0;
    }}

    /* Badge de atualização */
    .update-badge {{
        display: inline-block;
        background: rgba(196,98,29,0.15);
        border: 1px solid {LARANJA};
        color: {LARANJA};
        font-size: 0.75rem;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 24px;
    }}

    /* Tabelas */
    .dataframe {{
        background-color: {AZUL_CARD} !important;
        color: {BRANCO} !important;
    }}

    /* Selectbox e filtros */
    .stSelectbox label {{ color: {CINZA} !important; font-size: 0.85rem; }}
    div[data-baseweb="select"] {{
        background-color: {AZUL_CARD} !important;
        border-color: {AZUL_BORDA} !important;
    }}

    /* Divider */
    hr {{ border-color: {AZUL_BORDA}; margin: 32px 0; }}

    /* Esconder elementos padrão do Streamlit */
    #MainMenu, footer, header {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)


# ── Casas disponíveis para brasileiros ──────────────────────────────────────
# Atualizado com base em testes reais de acesso (Mai/2026)
CASAS_BR = [
    # ✅ Confirmadas — funcionam para brasileiros (Mai/2026)
    "Betsson",       # Licença SIGAP brasileira, BRL e Pix
    "888sport",      # Aceita brasileiros
    "Pinnacle",      # Via parceria com Betsson no Brasil
    "Marathon Bet",  # Aceita 200+ países incluindo Brasil
    "BetMGM",        # Licença brasileira via parceria com Grupo Globo
    "Unibet (NL)",   # URL confirmada
    "Unibet (UK)",   # URL confirmada
    "Unibet (SE)",   # URL confirmada
    "Coolbet",       # URL confirmada
    "Betfair",       # Exchange — aceita brasileiros
    "Matchbook",     # Exchange — aceita brasileiros
    "1xBet",         # Aceita brasileiros
    "Everygame",     # Aceita brasileiros
    "BetOnline.ag",  # Aceita brasileiros
    "Winamax (FR)",  # URL confirmada
    "Winamax (DE)",  # URL confirmada
    "FanDuel",       # Aceita internacionais
    "DraftKings",    # Aceita internacionais
]

# ── URLs diretas para Série A em cada casa ──────────────────────────────────
# ✅ = URL confirmada | ⚠️ = URL genérica (página específica não confirmada)
URLS_CASAS = {
    # ✅ Confirmadas
    "888sport":       "https://www.888sport.com/football/brazil/brazilian-serie-a-t-566860/",
    "Pinnacle":       "https://www.pinnacle.com/en/soccer/brazil-serie-a/matchups/",
    "Betfair":        "https://www.betfair.com/sport/football/south-american-soccer/brazil-serie-a",
    "Matchbook":      "https://www.matchbook.com/sport/football/brazil/serie-a",
    "Coolbet":        "https://www.coolbet.com/en/sports/football/brazil/serie-a",
    "Unibet (NL)":    "https://www.unibet.nl/betting/sports/filter/football/brazil/brasileirao_serie_a/all/matches",
    "Winamax (FR)":   "https://www.winamax.fr/paris-sportifs/sports/1/13/83",
    "Winamax (DE)":   "https://www.winamax.de/sportwetten/sports/1/13/83",
    "FanDuel":        "https://sportsbook.fanduel.com/soccer/brazilian-serie-a",
    "DraftKings":     "https://sportsbook.draftkings.com/leagues/soccer/brazil-serie-a",
    "BetMGM":         "https://www.betmgm.bet.br/aposta-esportiva#/league/1173/events",
    "Marathon Bet":   "https://www.marathonbet.com/en/betting/Football/Brazil/Serie+A",
    "1xBet":          "https://www.1xbet.com/en/line/football/116-brazil-serie-a",
    "BetOnline.ag":   "https://www.betonline.ag/sportsbook/soccer/brazil",
    "Everygame":      "https://www.everygame.com/sports-betting/soccer/south-america/brazil-serie-a",
    "Betsson":        "https://www.betsson.com/en/sportsbook/football/brazil",
    # ⚠️ Genéricas — levam para futebol/Brasil mas sem página específica da Série A confirmada
    "Nordic Bet":     "https://www.nordicbet.com/en/sports/football",
    "Unibet":         "https://www.unibet.com/betting/sports/filter/football",
    "Unibet (UK)":    "https://www.unibet.co.uk/betting/odds/football",
    "Unibet (SE)":    "https://www.unibet.se/betting/sports/filter/football",
    "Unibet (FR)":    "https://www.unibet.fr/paris-sportifs/sports/filter/football",
    "Betway":         "https://betway.com/g/en/sports/cat/soccer",
    "Bovada":         "https://www.bovada.lv/sports/soccer/brazil-serie-a",
    "Casumo":         "https://www.casumo.com/en/sports/football/",
    "Bet Victor":     "https://www.betvictor.com/en-gb/sport/football",
    "Betclic (FR)":   "https://www.betclic.fr/football-s1/",
    "LeoVegas (SE)":  "https://www.leovegas.com/en-se/sports/football/",
    "PMU (FR)":       "https://www.pmu.fr/paris-sportifs/football/",
    "Tipico":         "https://www.tipico.com/en/sports/soccer/",
    "BetAnything":    "https://www.betanything.com/sports/soccer/",
    "Codere (IT)":    "https://www.codere.it/sport/calcio/",
    "PointsBet (AU)": "https://pointsbet.com.au/sports/soccer/",
    "Coral":          "https://www.coral.co.uk/sport/football/",
    "Paddy Power":    "https://www.paddypower.com/football/",
    "BoyleSports":    "https://www.boylesports.com/sports/football/",
    "Grosvenor":      "https://www.grosvenorsport.com/football/",
    "LiveScore Bet":  "https://www.livescorebet.com/sports/football/",
    "Sky Bet":        "https://www.skybet.com/football/",
    "Smarkets":       "https://smarkets.com/sport/football/",
    "William Hill":   "https://www.williamhill.com/football/",
    "LowVig.ag":      "https://www.lowvig.ag/sports/soccer/",
    "BetRivers":      "https://www.betrivers.com/sports/soccer/",
    "Virgin Bet":     "https://www.virginbet.com/sport/football/",
    "Neds":           "https://www.neds.com.au/sports/soccer/",
    "PlayUp":         "https://www.playup.com/au/sport/soccer/",
}

# ── Funções de dados ─────────────────────────────────────────────────────────

def definir_intervalo_atualizacao(df_futuro):
    agora = datetime.now(timezone.utc)
    if df_futuro.empty:
        return 43200
    proximos_jogos = df_futuro['data'].unique()
    for data_jogo in proximos_jogos:
        diferenca_horas = (data_jogo - agora).total_seconds() / 3600
        if -2 <= diferenca_horas <= 2:
            return 300
        elif diferenca_horas <= 24:
            return 7200
        elif diferenca_horas <= 48:
            return 21600
    return 43200


@st.cache_data(ttl=7200)
def buscar_odds():
    API_KEY  = st.secrets["ODDS_API_KEY"]
    BASE_URL = "https://api.the-odds-api.com/v4"
    url = f"{BASE_URL}/sports/soccer_brazil_campeonato/odds"
    params = {
        "apiKey":      API_KEY,
        "regions":     "eu,us,uk,au",
        "markets":     "h2h",
        "oddsFormat":  "decimal"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None, None
    requisicoes_restantes = response.headers.get("x-requests-remaining", "?")
    return response.json(), requisicoes_restantes


def status_jogo(data):
    agora = datetime.now(timezone.utc)
    diff = (agora - data).total_seconds() / 60
    if diff < 0:
        return "🕐 Em breve"
    elif diff <= 120:
        return "🔴 Ao vivo"
    else:
        return "✅ Encerrado"


def processar_dados(jogos):
    from datetime import timedelta
    registros = []
    for jogo in jogos:
        for casa in jogo["bookmakers"]:
            for outcome in casa["markets"][0]["outcomes"]:
                registros.append({
                    "jogo":      f"{jogo['home_team']} x {jogo['away_team']}",
                    "data":      jogo["commence_time"],
                    "casa":      casa["title"],
                    "resultado": "Empate" if outcome["name"] == "Draw" else outcome["name"],
                    "odd":       outcome["price"]
                })
    df = pd.DataFrame(registros)
    df["data"] = pd.to_datetime(df["data"], utc=True)

    # Jogos futuros + ao vivo (até 2h após o início)
    agora = datetime.now(timezone.utc)
    df = df[df["data"] > agora - timedelta(hours=2)].copy()

    # Adicionar status do jogo
    df["status"] = df["data"].apply(status_jogo)

    # Probabilidade implícita e normalizada
    df["prob_implicita"] = 1 / df["odd"]
    soma = df.groupby(["jogo","casa"])["prob_implicita"].sum().reset_index()
    soma.columns = ["jogo","casa","soma_prob"]
    df = df.merge(soma, on=["jogo","casa"])
    df["prob_normalizada"] = (df["prob_implicita"] / df["soma_prob"] * 100).round(2)

    return df


def calcular_margem(group):
    return (1 / group["odd"]).sum() - 1


# ── Layout ───────────────────────────────────────────────────────────────────

# Header
st.markdown(f"""
<div class="header">
    <div class="header-dot"></div>
    <div>
        <div class="header-title">⚽ BONAINTELLI — ODDS BRASILEIRÃO</div>
        <div class="header-subtitle">Comparador de odds em tempo real · Série A 2026</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Buscar e processar dados
jogos_raw, requisicoes = buscar_odds()

if jogos_raw is None:
    st.error("Erro ao buscar dados da API. Verifique sua chave ou tente novamente.")
    st.stop()

df = processar_dados(jogos_raw)

# Badge de atualização
agora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
st.markdown(f'<div class="update-badge">🔄 Atualizado em {agora_str} &nbsp;|&nbsp; Requisições restantes: {requisicoes}</div>', unsafe_allow_html=True)

if df.empty:
    st.warning("Nenhum jogo futuro encontrado no momento.")
    st.stop()

# ── Seleção do jogo ─────────────────────────────────────────────────────────
jogos_status = df[["jogo","status","data"]].drop_duplicates().sort_values("data")
jogos_status["opcao"] = jogos_status["status"] + "  " + jogos_status["jogo"]
opcoes = jogos_status["opcao"].tolist()
jogos_map = dict(zip(jogos_status["opcao"], jogos_status["jogo"]))

opcao_selecionada = st.selectbox(
    "Selecione o jogo",
    options=opcoes,
    key="jogo_select"
)
jogo_selecionado = jogos_map[opcao_selecionada]

# ── Métricas gerais ──────────────────────────────────────────────────────────
margem_df = df.groupby(["jogo","casa"]).apply(calcular_margem).reset_index()
margem_df.columns = ["jogo","casa","margem"]
margem_df["margem"] = (margem_df["margem"] * 100).round(2)

# Filtrar combinações jogo+casa com margem absurda (acima de 20%)
# Filtra por jogo individualmente — preserva casas boas em outros jogos
pares_validos = margem_df[margem_df["margem"] <= 20][["jogo","casa"]].drop_duplicates()
margem_df = margem_df.merge(pares_validos, on=["jogo","casa"])
df = df.merge(pares_validos, on=["jogo","casa"])

ranking_casas = margem_df.groupby("casa")["margem"].mean().sort_values().reset_index()
ranking_casas.columns = ["casa","margem_media"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Jogos disponíveis</div>
        <div class="metric-value">{df['jogo'].nunique()}</div>
        <div class="metric-sub">próximos jogos</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Casas monitoradas</div>
        <div class="metric-value">{df['casa'].nunique()}</div>
        <div class="metric-sub">em tempo real</div>
    </div>""", unsafe_allow_html=True)

# Melhor odd por time do jogo selecionado
time_casa = jogo_selecionado.split(" x ")[0]
time_fora = jogo_selecionado.split(" x ")[1]
df_jogo_odds = df[df["jogo"] == jogo_selecionado]

odd_casa = df_jogo_odds[df_jogo_odds["resultado"] == time_casa]["odd"].max()
odd_fora = df_jogo_odds[df_jogo_odds["resultado"] == time_fora]["odd"].max()
casa_odd_casa = df_jogo_odds[df_jogo_odds["resultado"] == time_casa].loc[df_jogo_odds[df_jogo_odds["resultado"] == time_casa]["odd"].idxmax(), "casa"] if not df_jogo_odds[df_jogo_odds["resultado"] == time_casa].empty else "-"
casa_odd_fora = df_jogo_odds[df_jogo_odds["resultado"] == time_fora].loc[df_jogo_odds[df_jogo_odds["resultado"] == time_fora]["odd"].idxmax(), "casa"] if not df_jogo_odds[df_jogo_odds["resultado"] == time_fora].empty else "-"

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Melhor odd · {time_casa}</div>
        <div class="metric-value">{odd_casa:.2f}</div>
        <div class="metric-sub">{casa_odd_casa}</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Melhor odd · {time_fora}</div>
        <div class="metric-value">{odd_fora:.2f}</div>
        <div class="metric-sub">{casa_odd_fora}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Seção 1: Melhores odds por jogo ─────────────────────────────────────────
st.markdown('<div class="section-title">Melhores Odds por Jogo</div>', unsafe_allow_html=True)

# Toggle de filtro para brasileiros
apenas_br = st.toggle(
    "🇧🇷 Mostrar apenas casas disponíveis para brasileiros",
    value=False
)

df_jogo = df[df["jogo"] == jogo_selecionado]
if apenas_br:
    df_jogo = df_jogo[df_jogo["casa"].isin(CASAS_BR)]
    if df_jogo.empty:
        st.warning("Nenhuma casa disponível para brasileiros neste jogo.")
        st.stop()

# Tabela de odds por casa
pivot = df_jogo.pivot_table(index="casa", columns="resultado", values="odd").reset_index()
numeric_cols = [c for c in pivot.columns if c != "casa"]
pivot[numeric_cols] = pivot[numeric_cols].round(2)

# Adicionar coluna de link
pivot["🔗"] = pivot["casa"].map(lambda x: URLS_CASAS.get(x, ""))

# Destacar melhor odd por coluna
def highlight_max(s):
    is_max = s == s.max()
    return [f"background-color: rgba(196,98,29,0.25); color: #D4743A; font-weight: bold" if v else "" for v in is_max]

resultado_cols = [c for c in pivot.columns if c not in ["casa", "🔗"]]
styled = pivot.style.apply(highlight_max, subset=resultado_cols).format({col: "{:.2f}" for col in resultado_cols})

st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True,
    column_config={
        "casa": st.column_config.TextColumn("Casa", width="medium"),
        "🔗": st.column_config.LinkColumn("🔗", display_text="Acessar", width="small"),
        **{col: st.column_config.NumberColumn(col, width="small", format="%.2f") for col in resultado_cols}
    }
)

# Gráfico de odds por resultado
col_a, col_b = st.columns(2)

for i, resultado in enumerate(df_jogo["resultado"].unique()):
    df_res = df_jogo[df_jogo["resultado"] == resultado].sort_values("odd", ascending=False).head(15).sort_values("odd", ascending=True)
    fig = px.bar(
        df_res,
        x="odd", y="casa",
        orientation="h",
        title=f"Odds — {resultado}",
        color="odd",
        color_continuous_scale=[[0, AZUL_CARD], [1, LARANJA]],
        text=df_res["odd"].round(2)
    )
    fig.update_layout(
        plot_bgcolor=AZUL_CARD,
        paper_bgcolor=AZUL_ESCURO,
        font_color=BRANCO,
        font_family="Barlow",
        title_font_size=14,
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(showgrid=False, color=CINZA),
        yaxis=dict(showgrid=False, color=CINZA),
    )
    fig.update_traces(textposition="outside", textfont_color=BRANCO)

    if i % 2 == 0:
        col_a.plotly_chart(fig, use_container_width=True)
    else:
        col_b.plotly_chart(fig, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Seção 2: Probabilidade normalizada ──────────────────────────────────────
st.markdown('<div class="section-title">Consenso do Mercado — Probabilidade Normalizada</div>', unsafe_allow_html=True)

df_prob = df[df["jogo"] == jogo_selecionado].copy()
prob_media = df_prob.groupby("resultado")["prob_normalizada"].mean().reset_index()
prob_media.columns = ["resultado","probabilidade"]
prob_media = prob_media.sort_values("probabilidade", ascending=False)

fig_prob = go.Figure(go.Bar(
    x=prob_media["resultado"],
    y=prob_media["probabilidade"],
    marker_color=[LARANJA, CINZA, AZUL_BORDA],
    text=prob_media["probabilidade"].apply(lambda x: f"{x:.1f}%"),
    textposition="outside",
    textfont=dict(color=BRANCO, size=14)
))
fig_prob.update_layout(
    plot_bgcolor=AZUL_CARD,
    paper_bgcolor=AZUL_ESCURO,
    font_color=BRANCO,
    font_family="Barlow",
    yaxis=dict(showgrid=False, color=CINZA, title="Probabilidade (%)"),
    xaxis=dict(showgrid=False, color=CINZA),
    margin=dict(l=0, r=0, t=20, b=0),
    showlegend=False
)
st.plotly_chart(fig_prob, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Seção 3: Ranking de casas por margem ────────────────────────────────────
st.markdown('<div class="section-title">Ranking de Casas — Menor Margem</div>', unsafe_allow_html=True)
st.caption("Casas com menor margem são mais justas para o apostador")

fig_ranking = px.bar(
    ranking_casas,
    x="margem_media",
    y="casa",
    orientation="h",
    text="margem_media",
    color="margem_media",
    color_continuous_scale=[[0, LARANJA], [1, AZUL_BORDA]],
)
fig_ranking.update_layout(
    plot_bgcolor=AZUL_CARD,
    paper_bgcolor=AZUL_ESCURO,
    font_color=BRANCO,
    font_family="Barlow",
    coloraxis_showscale=False,
    margin=dict(l=0, r=0, t=20, b=0),
    xaxis=dict(showgrid=False, color=CINZA, title="Margem Média (%)"),
    yaxis=dict(showgrid=False, color=CINZA, categoryorder="total ascending"),
    height=500
)
fig_ranking.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
    textfont_color=BRANCO
)
st.plotly_chart(fig_ranking, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Seção 4: Jogos mais incertos ─────────────────────────────────────────────
st.markdown('<div class="section-title">Jogos Mais Incertos</div>', unsafe_allow_html=True)
st.caption("Jogos onde as casas mais discordam entre si — maior variação de probabilidade")

variacao = df.groupby(["jogo","resultado"])["prob_normalizada"].agg(["min","max"]).reset_index()
variacao["variacao"] = (variacao["max"] - variacao["min"]).round(2)
variacao_jogo = variacao.groupby("jogo")["variacao"].mean().sort_values(ascending=False).reset_index()
variacao_jogo.columns = ["jogo","variacao_media"]

fig_incerteza = px.bar(
    variacao_jogo,
    x="variacao_media",
    y="jogo",
    orientation="h",
    text="variacao_media",
    color="variacao_media",
    color_continuous_scale=[[0, AZUL_BORDA], [1, LARANJA]],
)
fig_incerteza.update_layout(
    plot_bgcolor=AZUL_CARD,
    paper_bgcolor=AZUL_ESCURO,
    font_color=BRANCO,
    font_family="Barlow",
    coloraxis_showscale=False,
    margin=dict(l=0, r=0, t=20, b=0),
    xaxis=dict(showgrid=False, color=CINZA, title="Variação Média de Probabilidade (pp)"),
    yaxis=dict(showgrid=False, color=CINZA, categoryorder="total ascending"),
    height=450
)
fig_incerteza.update_traces(
    texttemplate="%{text:.2f}pp",
    textposition="outside",
    textfont_color=BRANCO
)
st.plotly_chart(fig_incerteza, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; padding: 32px 0 16px 0; color: {CINZA}; font-size: 0.8rem; border-top: 1px solid {AZUL_BORDA}; margin-top: 32px;">
    BonaIntelli · Dados via The Odds API · Apenas para fins analíticos e educacionais
</div>
""", unsafe_allow_html=True)
