import datetime
import re
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(
    page_title="SwissNeoFrontier - Terminal Financier",
    layout="wide",
    page_icon="🇨🇭",
)

# --- MODULE D'AUTHENTIFICATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "users_db" not in st.session_state:
    st.session_state.users_db = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if not st.session_state.authenticated:
    st.title("🔐 Connexion au Terminal SwissNeoFrontier")

    col_auth, _ = st.columns([1, 1])
    with col_auth:
        user_id = st.text_input(
            "Identifiant (4 chiffres)", max_chars=4, key="login_id"
        )

        if user_id:
            if not re.match(r"^\d{4}$", user_id):
                st.error("L'identifiant doit contenir exactement 4 chiffres.")
            elif user_id not in st.session_state.users_db:
                st.info(
                    "Première connexion : choisissez votre mot de passe."
                )
                new_pass = st.text_input(
                    "Créer le mot de passe", type="password", key="create_pass"
                )
                conf_pass = st.text_input(
                    "Confirmer le mot de passe",
                    type="password",
                    key="confirm_pass",
                )
                if st.button("Enregistrer et se connecter"):
                    if new_pass and new_pass == conf_pass:
                        st.session_state.users_db[user_id] = new_pass
                        st.session_state.authenticated = True
                        st.session_state.current_user = user_id
                        st.rerun()
                    else:
                        st.error(
                            "Mots de passe invalides ou non identiquement saisis."
                        )
            else:
                password = st.text_input(
                    "Mot de passe", type="password", key="login_pass"
                )
                if st.button("Se connecter"):
                    if st.session_state.users_db[user_id] == password:
                        st.session_state.authenticated = True
                        st.session_state.current_user = user_id
                        st.rerun()
                    else:
                        st.error("Mot de passe incorrect.")
    st.stop()

# --- INITIALISATION SESSION UTILISATEUR ---
user_key = f"comptes_{st.session_state.current_user}"
if user_key not in st.session_state:
    st.session_state[user_key] = [
        {"nom": "Livret A", "solde": 10000.0, "taux": 3.0, "versement": 200.0},
        {
            "nom": "Portefeuille CHF/EUR",
            "solde": 25000.0,
            "taux": 5.0,
            "versement": 500.0,
        },
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Sidebar Déconnexion
with st.sidebar:
    st.markdown(f"👤 Connecté : **{st.session_state.current_user}**")
    if st.button("🚪 Déconnexion"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.rerun()

st.title("🇨🇭 SwissNeoFrontier - Terminal Financier")


# --- FOREX EUR/CHF ---
@st.cache_data(ttl=3600)
def fetch_forex_data():
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    url = f"https://api.frankfurter.app/{start_date}..{end_date}?from=EUR&to=CHF"
    try:
        res = requests.get(url, timeout=5).json()
        rates = res.get("rates", {})
        return pd.DataFrame(
            [{"Date": k, "EUR/CHF": v["CHF"]} for k, v in rates.items()]
        )
    except Exception:
        return pd.DataFrame()


df_forex = fetch_forex_data()
latest_rate = df_forex["EUR/CHF"].iloc[-1] if not df_forex.empty else 0.95

# --- SECTIONS PRINCIPALES ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("💼 Comptes & Solde")
    comptes = st.session_state[user_key]
    total_patrimoine = sum(c["solde"] for c in comptes)
    st.metric("Patrimoine Net Total", f"{total_patrimoine:,.2f} €")

    with st.form("add_account", clear_on_submit=True):
        st.write("**Ajouter un compte**")
        nom = st.text_input("Nom du Compte")
        solde = st.number_input("Solde Initial (€)", min_value=0.0, step=500.0)
        taux = st.number_input(
            "Taux Annuel (%)", min_value=0.0, step=0.5, value=3.0
        )
        versement = st.number_input(
            "Versement Mensuel (€)", min_value=0.0, step=50.0, value=100.0
        )
        if st.form_submit_button("+ Ajouter"):
            if nom:
                comptes.append(
                    {
                        "nom": nom,
                        "solde": solde,
                        "taux": taux,
                        "versement": versement,
                    }
                )
                st.rerun()

    st.write("**Comptes actifs :**")
    for idx, acc in enumerate(comptes):
        c1, c2 = st.columns([4, 1])
        c1.write(
            f"• **{acc['nom']}** : {acc['solde']:,.0f} € ({acc['taux']}%, +{acc['versement']}€/m)"
        )
        if c2.button("✕", key=f"del_{idx}"):
            comptes.pop(idx)
            st.rerun()

with col_right:
    st.subheader("📊 Projection sur 20 Ans")
    years = list(range(21))
    projections = []
    for year in years:
        total_year = 0
        for c in comptes:
            P, r, M = c["solde"], c["taux"] / 100.0, c["versement"] * 12
            vf = (
                P * ((1 + r) ** year) + M * (((1 + r) ** year - 1) / r)
                if r > 0
                else P + M * year
            )
            total_year += vf
        projections.append(round(total_year, 2))

    df_proj = pd.DataFrame({"Année": years, "Patrimoine (€)": projections})
    fig_proj = px.line(
        df_proj,
        x="Année",
        y="Patrimoine (€)",
        title="Évolution estimée du capital",
    )
    fig_proj.update_traces(line_color="#238636", line_width=3)
    fig_proj.update_layout(
        height=320, margin=dict(l=20, r=20, t=40, b=20), template="plotly_dark"
    )
    st.plotly_chart(fig_proj, use_container_width=True)

st.divider()

# --- ASSISTANT GROK IA SÉCURISÉ ---
st.subheader("🚀 Assistant Grok (xAI)")

key_input = st.text_input(
    "Clé API xAI (Grok)",
    type="password",
    value=st.session_state.api_key,
    placeholder="xai-...",
)
if key_input != st.session_state.api_key:
    st.session_state.api_key = key_input


def query_grok(prompt):
    api_key_clean = st.session_state.api_key.strip()
    if not api_key_clean:
        return "⚠️ Veuillez d'abord renseigner votre clé API xAI ci-dessus."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key_clean}",
    }
    sys_msg = (
        f"Tu es Grok, expert financier sur le terminal SwissNeoFrontier. "
        f"Patrimoine utilisateur : {st.session_state[user_key]}. "
        f"Taux EUR/CHF actuel : {latest_rate:.4f}."
    )
    payload = {
        "model": "grok-2-latest",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    try:
        res = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15,
        )

        try:
            data = res.json()
        except Exception:
            return f"❌ Erreur HTTP {res.status_code} : Réponse brute non-JSON ({res.text})"

        if isinstance(data, dict):
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            elif "error" in data:
                err_detail = (
                    data["error"].get("message", str(data["error"]))
                    if isinstance(data["error"], dict)
                    else str(data["error"])
                )
                return f"❌ Erreur API ({res.status_code}) : {err_detail}"

        return f"❌ Erreur HTTP {res.status_code} : {res.text}"

    except Exception as e:
        return f"❌ Erreur réseau : {str(e)}"


# Bouton Analyse Rapide
if st.button("🤖 Analyser mon portefeuille"):
    analysis_prompt = "Fais une analyse synthétique de mon portefeuille, de mes projections à 20 ans et de l'exposition EUR/CHF."
    st.session_state.chat_history.append(
        {"role": "user", "content": analysis_prompt}
    )
    with st.spinner("Grok analyse vos données..."):
        reply = query_grok(analysis_prompt)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )
    st.rerun()

# Flux de discussion conversationnel
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_prompt = st.chat_input("Posez une question à Grok...")
if user_prompt:
    st.session_state.chat_history.append(
        {"role": "user", "content": user_prompt}
    )
    with st.spinner("Grok réfléchit..."):
        reply = query_grok(user_prompt)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )
    st.rerun()
