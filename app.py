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
    st.title("🔐 Connexion au Terminal")

    user_id = st.text_input(
        "Identifiant (4 chiffres)", max_chars=4, key="login_id"
    )

    if user_id:
        if not re.match(r"^\d{4}$", user_id):
            st.error(
                "Format invalide : l'identifiant doit contenir exactement 4 chiffres."
            )
        else:
            if user_id not in st.session_state.users_db:
                st.info(
                    "Première connexion détectée pour cet identifiant. Définissez votre mot de passe."
                )
                new_password = st.text_input(
                    "Créer le mot de passe",
                    type="password",
                    key="create_pass",
                )
                confirm_password = st.text_input(
                    "Confirmer le mot de passe",
                    type="password",
                    key="confirm_pass",
                )

                if st.button("Enregistrer et se connecter"):
                    if not new_password:
                        st.error("Le mot de passe ne peut pas être vide.")
                    elif new_password != confirm_password:
                        st.error("Les mots de passe ne correspondent pas.")
                    else:
                        st.session_state.users_db[user_id] = new_password
                        st.session_state.authenticated = True
                        st.session_state.current_user = user_id
                        st.success("Compte créé avec succès.")
                        st.rerun()
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

# --- APPLICATION PRINCIPALE (Accessible après connexion) ---

# Bouton de déconnexion dans la barre latérale
with st.sidebar:
    st.write(f"Utilisateur connecté : **{st.session_state.current_user}**")
    if st.button("Déconnexion"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.rerun()

st.title("🇨🇭 SwissNeoFrontier - Terminal Financier")


# --- MODULE FOREX EUR/CHF ---
@st.cache_data(ttl=3600)
def fetch_forex_data():
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    url = f"https://api.frankfurter.app/{start_date}..{end_date}?from=EUR&to=CHF"
    try:
        res = requests.get(url, timeout=5).json()
        rates = res.get("rates", {})
        df = pd.DataFrame(
            [{"Date": k, "EUR/CHF": v["CHF"]} for k, v in rates.items()]
        )
        return df
    except Exception:
        return pd.DataFrame()


df_forex = fetch_forex_data()
latest_rate = None

st.subheader("📈 Cours EUR / CHF (30 derniers jours)")
if not df_forex.empty:
    latest_rate = df_forex["EUR/CHF"].iloc[-1]
    st.metric("Cours Actuel EUR/CHF", f"1 EUR = {latest_rate:.4f} CHF")
    fig_forex = px.line(
        df_forex, x="Date", y="EUR/CHF", title="Évolution EUR/CHF"
    )
    fig_forex.update_traces(line_color="#D29922")
    st.plotly_chart(fig_forex, use_container_width=True)
else:
    st.warning("Impossible de charger les données Forex.")

st.divider()

# --- MODULE PATRIMOINE & PROJECTION ---
if "comptes" not in st.session_state:
    st.session_state.comptes = [
        {"nom": "Livret A", "solde": 10000.0, "taux": 3.0, "versement": 200.0},
        {
            "nom": "Portefeuille CHF/EUR",
            "solde": 25000.0,
            "taux": 5.0,
            "versement": 500.0,
        },
    ]

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("➕ Ajouter un Compte")
    with st.form("account_form", clear_on_submit=True):
        nom = st.text_input("Nom du Compte")
        solde = st.number_input("Solde Initial (€)", min_value=0.0, step=1000.0)
        taux = st.number_input(
            "Taux Annuel Théorique (%)", min_value=0.0, step=0.5
        )
        versement = st.number_input(
            "Versement Mensuel (€)", min_value=0.0, step=50.0
        )
        submitted = st.form_submit_button("+ Ajouter à la simulation")

        if submitted and nom:
            st.session_state.comptes.append(
                {
                    "nom": nom,
                    "solde": solde,
                    "taux": taux,
                    "versement": versement,
                }
            )
            st.rerun()

    st.subheader("💼 Comptes Actifs")
    total_patrimoine = sum(c["solde"] for c in st.session_state.comptes)
    st.metric("Patrimoine Net Total", f"{total_patrimoine:,.2f} €")

    for idx, acc in enumerate(st.session_state.comptes):
        c1, c2 = st.columns([4, 1])
        c1.write(
            f"**{acc['nom']}** | {acc['solde']:,.0f}€ | {acc['taux']}% | +{acc['versement']}€/m"
        )
        if c2.button("✕", key=f"del_{idx}"):
            st.session_state.comptes.pop(idx)
            st.rerun()

with col_right:
    st.subheader("📊 Projection à 20 Ans (Intérêts Composés)")

    years = list(range(21))
    projections = []
    for year in years:
        total_year = 0
        for c in st.session_state.comptes:
            P = c["solde"]
            r = c["taux"] / 100.0
            M = c["versement"] * 12
            vf = (
                P * ((1 + r) ** year) + M * (((1 + r) ** year - 1) / r)
                if r > 0
                else P + M * year
            )
            total_year += vf
        projections.append(round(total_year, 2))

    df_proj = pd.DataFrame({"Année": years, "Patrimoine (€)": projections})
    fig_proj = px.line(
        df_proj, x="Année", y="Patrimoine (€)", title="Projection financière"
    )
    fig_proj.update_traces(line_color="#238636")
    st.plotly_chart(fig_proj, use_container_width=True)

st.divider()

# --- MODULE GROK (xAI) ---
st.subheader("🚀 Assistant Grok (xAI)")
api_key = st.text_input(
    "Clé API xAI (Grok)", type="password", placeholder="xai-..."
)


def call_grok(prompt):
    if not api_key:
        return "Veuillez saisir votre clé API xAI ci-dessus."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    sys_prompt = f"Tu es Grok, un expert financier. Contexte portefeuille: {st.session_state.comptes}. Taux EUR/CHF actuel: {latest_rate}."
    payload = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": sys_prompt},
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
        data = res.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return f"Erreur API : {data.get('error', {}).get('message', 'Inconnue')}"
    except Exception as e:
        return f"Erreur réseau : {str(e)}"


if st.button("🤖 Analyser mon portefeuille"):
    with st.spinner("Grok analyse vos données..."):
        st.info(
            call_grok(
                "Analyse mon portefeuille et donne-moi un avis synthétique."
            )
        )

user_query = st.text_input("Poser une question à Grok :")
if user_query:
    with st.spinner("Grok réfléchit..."):
        st.write(f"**Grok :** {call_grok(user_query)}")
