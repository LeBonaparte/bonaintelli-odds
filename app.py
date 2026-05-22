import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="BonaIntelli | Odds Brasileirão",
    page_icon="⚽",
    layout="wide"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Barlow', sans-serif; background-color: #0D1B2A; color: #fff; }
    .stApp { background-color: #0D1B2A; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Header */
    .bi-header { background: #0D1B2A; border-bottom: 2px solid #C4621D; padding: 14px 24px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 0; }
    .bi-header-left { display: flex; align-items: center; gap: 14px; }
    .bi-logo-text { font-size: 19px; color: #fff; letter-spacing: 2px; line-height: 1.2; }
    .bi-logo-bold { font-weight: 700; }
    .bi-logo-light { font-weight: 300; }
    .bi-badge { background: rgba(196,98,29,0.15); border: 1px solid #C4621D; color: #C4621D; font-size: 11px; padding: 4px 12px; border-radius: 20px; }

    /* Hero */
    .bi-hero { background: #111f30; padding: 22px 24px 18px; border-bottom: 1px solid #1E3148; margin-bottom: 20px; }
    .bi-hero-title { font-size: 20px; font-weight: 500; color: #fff; margin-bottom: 5px; }
    .bi-hero-sub { font-size: 13px; color: #8A9BB0; }
    .bi-hero-sub span { color: #C4621D; }

    /* Métricas */
    .bi-metric { background: #152236; border: 1px solid #1E3148; border-left: 3px solid #C4621D; border-radius: 8px; padding: 14px 16px; height: 100%; }
    .bi-metric-label { font-size: 10px; color: #8A9BB0; text-transform: uppercase; letter-spacing: 1px; }
    .bi-metric-value { font-size: 22px; font-weight: 600; color: #fff; margin-top: 4px; }
    .bi-metric-sub { font-size: 11px; color: #C4621D; margin-top: 2px; }

    /* Section title */
    .bi-stitle { font-size: 12px; font-weight: 500; color: #fff; text-transform: uppercase; letter-spacing: 1px; border-left: 3px solid #C4621D; padding-left: 10px; margin: 20px 0 14px 0; }

    /* Game cards */
    .bi-game-card { background: #152236; border: 1px solid #1E3148; border-radius: 10px; padding: 14px; margin-bottom: 12px; }
    .bi-game-card-sel { background: #152236; border: 1px solid #C4621D; border-radius: 10px; padding: 14px; margin-bottom: 12px; }
    .bi-game-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .bi-game-league { font-size: 11px; color: #8A9BB0; }
    .bi-live { background: rgba(196,38,29,0.15); border: 1px solid #c4261d; color: #ff5544; font-size: 10px; padding: 2px 8px; border-radius: 20px; }
    .bi-soon { background: rgba(196,98,29,0.1); border: 1px solid #C4621D55; color: #C4621D; font-size: 10px; padding: 2px 8px; border-radius: 20px; }
    .bi-teams { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .bi-team { text-align: center; flex: 1; }
    .bi-team-name { font-size: 13px; font-weight: 500; color: #fff; }
    .bi-team-odd { font-size: 19px; font-weight: 600; color: #C4621D; margin-top: 4px; }
    .bi-vs { color: #8A9BB0; font-size: 12px; padding: 0 8px; }
    .bi-draw { display: flex; justify-content: center; gap: 8px; align-items: center; }
    .bi-draw-label { font-size: 11px; color: #8A9BB0; }
    .bi-draw-odd { font-size: 14px; color: #fff; font-weight: 500; }
    .bi-game-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; border-top: 1px solid #1E3148; padding-top: 8px; }
    .bi-game-time { font-size: 11px; color: #8A9BB0; }
    .bi-best-label { font-size: 10px; color: #8A9BB0; text-align: right; }
    .bi-best-casa { font-size: 11px; color: #C4621D; text-align: right; }

    /* Panel */
    .bi-panel { background: #152236; border: 1px solid #1E3148; border-radius: 10px; padding: 14px; margin-bottom: 20px; }
    .bi-panel-sub { font-size: 11px; color: #8A9BB0; margin-bottom: 12px; }

    /* Prob bars */
    .bi-prow { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
    .bi-pname { font-size: 11px; color: #8A9BB0; width: 90px; }
    .bi-pbw { flex: 1; background: #1E3148; border-radius: 4px; height: 7px; overflow: hidden; }
    .bi-pb { height: 7px; border-radius: 4px; }
    .bi-pval { font-size: 12px; color: #fff; width: 36px; text-align: right; }

    /* Uncertain bars */
    .bi-urow { display: flex; align-items: center; gap: 8px; margin-bottom: 9px; }
    .bi-uname { font-size: 11px; color: #fff; flex: 1; }
    .bi-ubw { width: 110px; background: #1E3148; border-radius: 4px; height: 5px; overflow: hidden; }
    .bi-ub { height: 5px; border-radius: 4px; background: #C4621D; }
    .bi-upct { font-size: 11px; color: #C4621D; width: 36px; text-align: right; }

    /* Ranking bars */
    .bi-rrow { display: flex; align-items: center; gap: 8px; margin-bottom: 9px; }
    .bi-rnum { font-size: 11px; color: #8A9BB0; width: 18px; }
    .bi-rname { font-size: 12px; color: #fff; width: 90px; }
    .bi-rbw { flex: 1; background: #1E3148; border-radius: 4px; height: 6px; overflow: hidden; }
    .bi-rb { height: 6px; border-radius: 4px; background: #C4621D; }
    .bi-rval { font-size: 12px; color: #C4621D; width: 40px; text-align: right; }

    /* Odds table */
    .bi-odds-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .bi-odds-table th { color: #8A9BB0; font-weight: 400; padding: 6px 10px; text-align: left; border-bottom: 1px solid #1E3148; font-size: 10px; text-transform: uppercase; }
    .bi-odds-table td { padding: 7px 10px; border-bottom: 1px solid #1E3148; color: #fff; }
    .bi-odds-table tr:last-child td { border-bottom: none; }
    .bi-best-odd { color: #C4621D; font-weight: 600; background: rgba(196,98,29,0.1); border-radius: 4px; padding: 1px 5px; }
    .bi-lbtn { font-size: 10px; color: #C4621D; border: 1px solid #C4621D44; border-radius: 4px; padding: 2px 7px; text-decoration: none; }
    .bi-margem-ok { color: #4CAF50; }
    .bi-margem-bad { color: #8A9BB0; }

    /* Toggle */
    .stToggle label { color: #8A9BB0 !important; font-size: 12px !important; }
    .stSelectbox label { color: #8A9BB0 !important; font-size: 12px !important; }
    div[data-baseweb="select"] { background-color: #152236 !important; border-color: #1E3148 !important; }

    /* Buttons for card selection */
    div[data-testid="stButton"] button {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        width: 100% !important;
        text-align: left !important;
    }

    /* Update badge */
    .bi-update { display: inline-block; background: rgba(196,98,29,0.15); border: 1px solid #C4621D; color: #C4621D; font-size: 11px; padding: 4px 12px; border-radius: 20px; margin-bottom: 20px; }

    /* Footer */
    .bi-footer { text-align: center; padding: 24px 0 12px 0; color: #8A9BB0; font-size: 11px; border-top: 1px solid #1E3148; margin-top: 24px; }
</style>
""", unsafe_allow_html=True)

# ── Casas BR ─────────────────────────────────────────────────────────────────
CASAS_BR = [
    "Betsson", "888sport", "Pinnacle", "Marathon Bet", "BetMGM",
    "Unibet (NL)", "Unibet (UK)", "Unibet (SE)", "Coolbet",
    "Betfair", "Matchbook", "1xBet", "Everygame", "BetOnline.ag",
    "Winamax (FR)", "Winamax (DE)", "FanDuel", "DraftKings",
]

URLS_CASAS = {
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
    "William Hill":   "https://www.williamhill.com/football/",
    "Coral":          "https://www.coral.co.uk/sport/football/",
    "Paddy Power":    "https://www.paddypower.com/football/",
    "BoyleSports":    "https://www.boylesports.com/sports/football/",
    "Grosvenor":      "https://www.grosvenorsport.com/football/",
    "LiveScore Bet":  "https://www.livescorebet.com/sports/football/",
    "Sky Bet":        "https://www.skybet.com/football/",
    "Smarkets":       "https://smarkets.com/sport/football/",
    "LowVig.ag":      "https://www.lowvig.ag/sports/soccer/",
    "BetRivers":      "https://www.betrivers.com/sports/soccer/",
    "Virgin Bet":     "https://www.virginbet.com/sport/football/",
    "Neds":           "https://www.neds.com.au/sports/soccer/",
    "PlayUp":         "https://www.playup.com/au/sport/soccer/",
}

TIMES_SERIE_A = [
    "Atletico Mineiro", "Atletico Paranaense", "Bahia", "Botafogo",
    "Corinthians", "Coritiba", "Cruzeiro", "Flamengo", "Fluminense",
    "Fortaleza", "Gremio", "Grêmio", "Internacional", "Mirassol",
    "Palmeiras", "RB Bragantino", "Bragantino-SP", "Santos",
    "Sao Paulo", "São Paulo", "Vasco da Gama", "Vitoria", "Vitória",
    "Juventude", "Chapecoense", "Remo"
]

# ── Funções ──────────────────────────────────────────────────────────────────
def status_jogo(data):
    agora = datetime.now(timezone.utc)
    diff = (agora - data).total_seconds() / 60
    if diff < 0:
        minutos = int(abs((data - agora).total_seconds() / 60))
        if minutos < 60:
            return "em_breve", f"Em breve · {minutos}min"
        horas = int(minutos / 60)
        if horas < 24:
            return "em_breve", f"Hoje · {data.astimezone(timezone(timedelta(hours=-3))).strftime('%H:%M')}"
        return "amanha", f"Amanhã · {data.astimezone(timezone(timedelta(hours=-3))).strftime('%H:%M')}"
    elif diff <= 120:
        return "ao_vivo", f"Ao vivo · {int(diff)}'"
    return "encerrado", "Encerrado"


@st.cache_data(ttl=300)
def buscar_odds():
    API_KEY = st.secrets["ODDS_API_KEY"]
    url = "https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds"
    params = {"apiKey": API_KEY, "regions": "eu,us,uk,au", "markets": "h2h", "oddsFormat": "decimal"}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None, None
    return response.json(), response.headers.get("x-requests-remaining", "?")


def processar_dados(jogos):
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
    agora = datetime.now(timezone.utc)
    df = df[df["data"] > agora - timedelta(hours=2)].copy()
    df = df[df["jogo"].apply(lambda j: any(t in j for t in TIMES_SERIE_A))].copy()
    df["prob_implicita"] = 1 / df["odd"]
    soma = df.groupby(["jogo","casa"])["prob_implicita"].sum().reset_index()
    soma.columns = ["jogo","casa","soma_prob"]
    df = df.merge(soma, on=["jogo","casa"])
    df["prob_normalizada"] = (df["prob_implicita"] / df["soma_prob"] * 100).round(2)
    return df


def calcular_margem(group):
    return (1 / group["odd"]).sum() - 1





# ── Buscar dados ─────────────────────────────────────────────────────────────
jogos_raw, requisicoes = buscar_odds()

if jogos_raw is None:
    st.error("Erro ao buscar dados da API.")
    st.stop()

df = processar_dados(jogos_raw)

# Filtrar margem absurda
margem_df = df.groupby(["jogo","casa"]).apply(calcular_margem).reset_index()
margem_df.columns = ["jogo","casa","margem"]
margem_df["margem"] = (margem_df["margem"] * 100).round(2)
pares_validos = margem_df[margem_df["margem"] <= 20][["jogo","casa"]].drop_duplicates()
margem_df = margem_df.merge(pares_validos, on=["jogo","casa"])
df = df.merge(pares_validos, on=["jogo","casa"])

if df.empty:
    st.warning("Nenhum jogo disponível.")
    st.stop()

# Dados por jogo
jogos_info = df[["jogo","data"]].drop_duplicates().sort_values("data")
ranking_casas = margem_df.groupby("casa")["margem"].mean().sort_values().reset_index()
ranking_casas.columns = ["casa","margem_media"]

# ── TTL dinâmico ─────────────────────────────────────────────────────────────
agora_utc = datetime.now(timezone.utc)
ttl_label = "12h"
for dt in sorted(df["data"].unique()):
    diff_h = (dt - agora_utc).total_seconds() / 3600
    if -2 <= diff_h <= 2:
        ttl_label = "5 min"; break
    elif diff_h <= 24:
        ttl_label = "2h"; break
    elif diff_h <= 48:
        ttl_label = "6h"; break

# ── Header ───────────────────────────────────────────────────────────────────
agora_br = datetime.now(timezone.utc) - timedelta(hours=3)
agora_str = agora_br.strftime("%d/%m/%Y %H:%M")

st.markdown(f"""
<div class="bi-header">
    <div class="bi-header-left">
        <svg width="38" height="38" viewBox="0 0 40 40" fill="none">
            <circle cx="20" cy="20" r="5" fill="#C4621D"/>
            <circle cx="20" cy="4" r="3" fill="#C4621D"/>
            <circle cx="20" cy="36" r="3" fill="#C4621D"/>
            <circle cx="4" cy="20" r="3" fill="#C4621D"/>
            <circle cx="36" cy="20" r="3" fill="#C4621D"/>
            <circle cx="7" cy="7" r="2.5" fill="#C4621D"/>
            <circle cx="33" cy="7" r="2.5" fill="#C4621D"/>
            <circle cx="7" cy="33" r="2.5" fill="#C4621D"/>
            <circle cx="33" cy="33" r="2.5" fill="#C4621D"/>
            <line x1="20" y1="20" x2="20" y2="7" stroke="#C4621D" stroke-width="1.5"/>
            <line x1="20" y1="20" x2="20" y2="33" stroke="#C4621D" stroke-width="1.5"/>
            <line x1="20" y1="20" x2="7" y2="20" stroke="#C4621D" stroke-width="1.5"/>
            <line x1="20" y1="20" x2="33" y2="20" stroke="#C4621D" stroke-width="1.5"/>
            <line x1="20" y1="20" x2="9" y2="9" stroke="#C4621D" stroke-width="1.5"/>
            <line x1="20" y1="20" x2="31" y2="9" stroke="#C4621D" stroke-width="1.5"/>
            <line x1="20" y1="20" x2="9" y2="31" stroke="#C4621D" stroke-width="1.5"/>
            <line x1="20" y1="20" x2="31" y2="31" stroke="#C4621D" stroke-width="1.5"/>
        </svg>
        <div>
            <div class="bi-logo-text"><span class="bi-logo-bold">BONA</span><span class="bi-logo-light">INTELLI</span></div>
            <div style="font-size:10px; color:#8A9BB0;">by Leticia Guedea Bonaparte</div>
        </div>
    </div>
    <div class="bi-badge">Atualizado {agora_str} (Brasília) · próx. {ttl_label} · {requisicoes} req. restantes</div>
</div>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="bi-hero">
    <div class="bi-hero-title">O mercado de apostas do Brasileirão, em um só lugar.</div>
    <div class="bi-hero-sub">Odds em tempo real · Série A 2026 · <span>{df['casa'].nunique()} casas monitoradas</span></div>
</div>
""", unsafe_allow_html=True)

# ── Seleção do jogo ──────────────────────────────────────────────────────────
if "jogo_selecionado" not in st.session_state:
    st.session_state.jogo_selecionado = jogos_info["jogo"].iloc[0]

jogo_selecionado = st.session_state.jogo_selecionado

# ── Métricas ─────────────────────────────────────────────────────────────────
time_casa = jogo_selecionado.split(" x ")[0]
time_fora = jogo_selecionado.split(" x ")[1]
df_jogo_odds = df[df["jogo"] == jogo_selecionado]

odd_casa_max = df_jogo_odds[df_jogo_odds["resultado"] == time_casa]["odd"].max() if not df_jogo_odds[df_jogo_odds["resultado"] == time_casa].empty else 0
odd_fora_max = df_jogo_odds[df_jogo_odds["resultado"] == time_fora]["odd"].max() if not df_jogo_odds[df_jogo_odds["resultado"] == time_fora].empty else 0
casa_odd_casa = df_jogo_odds[df_jogo_odds["resultado"] == time_casa].sort_values("odd", ascending=False)["casa"].iloc[0] if not df_jogo_odds[df_jogo_odds["resultado"] == time_casa].empty else "-"
casa_odd_fora = df_jogo_odds[df_jogo_odds["resultado"] == time_fora].sort_values("odd", ascending=False)["casa"].iloc[0] if not df_jogo_odds[df_jogo_odds["resultado"] == time_fora].empty else "-"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="bi-metric"><div class="bi-metric-label">Jogos disponíveis</div><div class="bi-metric-value">{df["jogo"].nunique()}</div><div class="bi-metric-sub">próximos jogos</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="bi-metric"><div class="bi-metric-label">Casas monitoradas</div><div class="bi-metric-value">{df["casa"].nunique()}</div><div class="bi-metric-sub">em tempo real</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="bi-metric"><div class="bi-metric-label">Melhor odd · {time_casa}</div><div class="bi-metric-value">{odd_casa_max:.2f}</div><div class="bi-metric-sub">{casa_odd_casa}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="bi-metric"><div class="bi-metric-label">Melhor odd · {time_fora}</div><div class="bi-metric-value">{odd_fora_max:.2f}</div><div class="bi-metric-sub">{casa_odd_fora}</div></div>', unsafe_allow_html=True)

st.markdown('<div style="margin-bottom:8px;"></div>', unsafe_allow_html=True)

# ── Seleção via dropdown ─────────────────────────────────────────────────────
st.markdown('<div class="bi-stitle">Jogo selecionado</div>', unsafe_allow_html=True)

# Montar opções do dropdown com status
jogos_lista = jogos_info["jogo"].tolist()
opcoes_dropdown = []
for jogo in jogos_lista:
    data = jogos_info[jogos_info["jogo"] == jogo]["data"].iloc[0]
    status_tipo, status_label = status_jogo(data)
    prefixo = "🔴" if status_tipo == "ao_vivo" else "🕐"
    opcoes_dropdown.append(f"{prefixo} {jogo} · {status_label}")

jogos_map = dict(zip(opcoes_dropdown, jogos_lista))
opcao_atual = next((k for k, v in jogos_map.items() if v == jogo_selecionado), opcoes_dropdown[0])

opcao_escolhida = st.selectbox(
    "Selecione o jogo",
    options=opcoes_dropdown,
    index=opcoes_dropdown.index(opcao_atual),
    label_visibility="collapsed"
)

if jogos_map[opcao_escolhida] != jogo_selecionado:
    st.session_state.jogo_selecionado = jogos_map[opcao_escolhida]
    jogo_selecionado = jogos_map[opcao_escolhida]
else:
    jogo_selecionado = jogos_map[opcao_escolhida]

# Card do jogo selecionado
data_sel = jogos_info[jogos_info["jogo"] == jogo_selecionado]["data"].iloc[0]
status_tipo_sel, status_label_sel = status_jogo(data_sel)
t_casa_sel = jogo_selecionado.split(" x ")[0]
t_fora_sel = jogo_selecionado.split(" x ")[1]
df_j_sel = df[df["jogo"] == jogo_selecionado]
o_casa_sel = df_j_sel[df_j_sel["resultado"] == t_casa_sel]["odd"].max() if not df_j_sel[df_j_sel["resultado"] == t_casa_sel].empty else 0
o_fora_sel = df_j_sel[df_j_sel["resultado"] == t_fora_sel]["odd"].max() if not df_j_sel[df_j_sel["resultado"] == t_fora_sel].empty else 0
o_emp_sel  = df_j_sel[df_j_sel["resultado"] == "Empate"]["odd"].max() if not df_j_sel[df_j_sel["resultado"] == "Empate"].empty else 0
marg_sel = margem_df[margem_df["jogo"] == jogo_selecionado].sort_values("margem")
melhor_casa_sel = marg_sel.iloc[0]["casa"] if not marg_sel.empty else "-"
melhor_val_sel  = marg_sel.iloc[0]["margem"] if not marg_sel.empty else 0

# Montar card do jogo selecionado
badge_cor = "#ff5544" if status_tipo_sel == "ao_vivo" else "#C4621D"
badge_bg  = "rgba(196,38,29,0.15)" if status_tipo_sel == "ao_vivo" else "rgba(196,98,29,0.1)"
badge_bd  = "#c4261d" if status_tipo_sel == "ao_vivo" else "#C4621D55"

card_parts = []
card_parts.append(f'''<div style="background:#152236;border:1px solid #C4621D;border-radius:10px;padding:14px;margin-bottom:14px;">''')
card_parts.append(f'''<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;"><span style="font-size:11px;color:#8A9BB0;">Brasileirao Serie A</span><span style="background:{badge_bg};border:1px solid {badge_bd};color:{badge_cor};font-size:10px;padding:2px 8px;border-radius:20px;">{status_label_sel}</span></div>''')

if status_tipo_sel == "ao_vivo":
    minutos = int(abs((datetime.now(timezone.utc) - data_sel).total_seconds() / 60))
    card_parts.append(f'''<div style="background:#0D1B2A;border:1px solid #2a3d52;border-radius:8px;padding:12px;margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;"><div style="text-align:center;flex:1;"><div style="font-size:10px;color:#8A9BB0;margin-bottom:4px;">{t_casa_sel}</div><div style="font-size:28px;font-weight:700;color:#fff;">-</div></div><div style="text-align:center;"><div style="font-size:10px;color:#ff5544;">{minutos} min</div><div style="font-size:16px;color:#8A9BB0;margin:4px 12px;">x</div><div style="font-size:9px;color:#8A9BB0;">ao vivo</div></div><div style="text-align:center;flex:1;"><div style="font-size:10px;color:#8A9BB0;margin-bottom:4px;">{t_fora_sel}</div><div style="font-size:28px;font-weight:700;color:#fff;">-</div></div></div>''')
    card_parts.append('<div style="font-size:10px;color:#8A9BB0;text-align:center;margin-bottom:10px;">Placar requer integracao com API-Football</div>')

o_casa_fmt = f"{o_casa_sel:.2f}"
o_fora_fmt = f"{o_fora_sel:.2f}"
o_emp_fmt  = f"{o_emp_sel:.2f}"
marg_fmt   = f"{melhor_val_sel:.1f}"

card_parts.append(f'''<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;"><div style="text-align:center;flex:1;"><div style="font-size:13px;font-weight:500;color:#fff;">{t_casa_sel}</div><div style="font-size:20px;font-weight:600;color:#C4621D;margin-top:4px;">{o_casa_fmt}</div></div><div style="color:#8A9BB0;font-size:12px;padding:0 12px;">x</div><div style="text-align:center;flex:1;"><div style="font-size:13px;font-weight:500;color:#fff;">{t_fora_sel}</div><div style="font-size:20px;font-weight:600;color:#C4621D;margin-top:4px;">{o_fora_fmt}</div></div></div>''')
card_parts.append(f'''<div style="display:flex;justify-content:center;gap:8px;align-items:center;"><span style="font-size:11px;color:#8A9BB0;">Empate</span><span style="font-size:14px;color:#fff;font-weight:500;">{o_emp_fmt}</span></div>''')
card_parts.append(f'''<div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;border-top:1px solid #1E3148;padding-top:8px;"><span style="font-size:10px;color:#8A9BB0;">Serie A 2026</span><span style="font-size:10px;color:#C4621D;">menor margem: {melhor_casa_sel} · {marg_fmt}%</span></div>''')
card_parts.append('</div>')

st.markdown("".join(card_parts), unsafe_allow_html=True)

# ── Odds detalhadas ──────────────────────────────────────────────────────────
st.markdown(f'<div class="bi-stitle">Odds detalhadas · {jogo_selecionado}</div>', unsafe_allow_html=True)

apenas_br = st.toggle("🇧🇷 Mostrar apenas casas disponíveis para brasileiros", value=False)

df_jogo = df[df["jogo"] == jogo_selecionado].copy()
if apenas_br:
    df_jogo = df_jogo[df_jogo["casa"].isin(CASAS_BR)]

if df_jogo.empty:
    st.warning("Nenhuma casa disponível para brasileiros neste jogo.")
else:
    # Montar tabela HTML
    resultados = [r for r in df_jogo["resultado"].unique() if r != "Empate"]
    resultados_ordem = sorted(resultados) + ["Empate"]

    # Pivot
    pivot = df_jogo.pivot_table(index="casa", columns="resultado", values="odd").reset_index()
    pivot = pivot.merge(margem_df[margem_df["jogo"] == jogo_selecionado][["casa","margem"]], on="casa", how="left")
    pivot = pivot.sort_values("margem")

    # Encontrar max por coluna de resultado
    maximos = {}
    for r in resultados_ordem:
        if r in pivot.columns:
            maximos[r] = pivot[r].max()

    st.markdown('<div class="bi-panel">', unsafe_allow_html=True)

    # Header da tabela
    header_cols = ["Casa"] + resultados_ordem + ["Margem", ""]
    header_html = "".join(f"<th>{h}</th>" for h in header_cols)

    rows_html = ""
    for _, row in pivot.iterrows():
        casa = row["casa"]
        url = URLS_CASAS.get(casa, "#")
        margem = row.get("margem", 0)
        margem_class = "bi-margem-ok" if margem < 6 else "bi-margem-bad"

        cells = f"<td>{casa}</td>"
        for r in resultados_ordem:
            if r in pivot.columns and pd.notna(row.get(r)):
                val = row[r]
                is_best = val == maximos.get(r, -1)
                span = f'<span class="bi-best-odd">{val:.2f}</span>' if is_best else f"{val:.2f}"
                cells += f"<td>{span}</td>"
            else:
                cells += "<td>—</td>"

        cells += f'<td class="{margem_class}">{margem:.1f}%</td>'
        cells += f'<td><a class="bi-lbtn" href="{url}" target="_blank">Acessar</a></td>'
        rows_html += f"<tr>{cells}</tr>"

    st.markdown(f"""
    <table class="bi-odds-table">
        <thead><tr>{header_html}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Consenso + Incertos ──────────────────────────────────────────────────────
col_prob, col_incert = st.columns(2)

with col_prob:
    st.markdown('<div class="bi-stitle">Consenso do mercado</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bi-panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="bi-panel-sub">Probabilidade normalizada · {jogo_selecionado}</div>', unsafe_allow_html=True)

    df_prob = df[df["jogo"] == jogo_selecionado].groupby("resultado")["prob_normalizada"].mean().sort_values(ascending=False)
    max_prob = df_prob.max()

    cores = ["#C4621D", "#8A9BB0", "#1E3148"]
    bars_html = ""
    for idx, (resultado, prob) in enumerate(df_prob.items()):
        pct_width = int((prob / max_prob) * 100) if max_prob > 0 else 0
        cor = cores[idx % len(cores)]
        bars_html += f"""
        <div class="bi-prow">
            <span class="bi-pname">{resultado}</span>
            <div class="bi-pbw"><div class="bi-pb" style="width:{pct_width}%; background:{cor};"></div></div>
            <span class="bi-pval">{prob:.1f}%</span>
        </div>"""

    st.markdown(bars_html + '</div>', unsafe_allow_html=True)

with col_incert:
    st.markdown('<div class="bi-stitle">Jogos mais incertos</div>', unsafe_allow_html=True)
    st.markdown('<div class="bi-panel">', unsafe_allow_html=True)
    st.markdown('<div class="bi-panel-sub">Maior divergência entre casas</div>', unsafe_allow_html=True)

    variacao = df.groupby(["jogo","resultado"])["prob_normalizada"].agg(["min","max"]).reset_index()
    variacao["variacao"] = (variacao["max"] - variacao["min"]).round(2)
    variacao_jogo = variacao.groupby("jogo")["variacao"].mean().sort_values(ascending=False).reset_index()
    variacao_jogo.columns = ["jogo","variacao_media"]
    max_var = variacao_jogo["variacao_media"].max()

    incert_html = ""
    for _, row in variacao_jogo.head(8).iterrows():
        pct = int((row["variacao_media"] / max_var) * 100) if max_var > 0 else 0
        nome_curto = row["jogo"].replace("Atletico", "Atl.").replace("Paranaense", "PR").replace("Mineiro", "MG")
        incert_html += f"""
        <div class="bi-urow">
            <span class="bi-uname">{nome_curto}</span>
            <div class="bi-ubw"><div class="bi-ub" style="width:{pct}%;"></div></div>
            <span class="bi-upct">{row["variacao_media"]:.1f}%</span>
        </div>"""

    st.markdown(incert_html + '</div>', unsafe_allow_html=True)

# ── Ranking de casas ─────────────────────────────────────────────────────────
st.markdown('<div class="bi-stitle">Ranking de casas · menor margem</div>', unsafe_allow_html=True)
st.markdown('<div class="bi-panel">', unsafe_allow_html=True)
st.markdown('<div class="bi-panel-sub">Casas com menor margem são mais justas para o apostador</div>', unsafe_allow_html=True)

top_casas = ranking_casas.head(20)
max_marg = top_casas["margem_media"].max()

col_r1, col_r2 = st.columns(2)
metade = len(top_casas) // 2

rank_html_1 = ""
for i, (_, row) in enumerate(top_casas.head(metade).iterrows()):
    pct = int((row["margem_media"] / max_marg) * 100)
    rank_html_1 += f"""
    <div class="bi-rrow">
        <span class="bi-rnum">{i+1}</span>
        <span class="bi-rname">{row['casa']}</span>
        <div class="bi-rbw"><div class="bi-rb" style="width:{pct}%;"></div></div>
        <span class="bi-rval">{row['margem_media']:.1f}%</span>
    </div>"""

rank_html_2 = ""
for i, (_, row) in enumerate(top_casas.iloc[metade:].iterrows()):
    pct = int((row["margem_media"] / max_marg) * 100)
    rank_html_2 += f"""
    <div class="bi-rrow">
        <span class="bi-rnum">{i+metade+1}</span>
        <span class="bi-rname">{row['casa']}</span>
        <div class="bi-rbw"><div class="bi-rb" style="width:{pct}%;"></div></div>
        <span class="bi-rval">{row['margem_media']:.1f}%</span>
    </div>"""

with col_r1:
    st.markdown(rank_html_1, unsafe_allow_html=True)
with col_r2:
    st.markdown(rank_html_2, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bi-footer">
    BonaIntelli · Dados via The Odds API · Apenas para fins analíticos e educacionais
</div>
""", unsafe_allow_html=True)
