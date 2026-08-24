import pandas as pd
import streamlit as st
from openai import OpenAI

# Configuration de la page
st.set_page_config(
    page_title="SwissNeoFrontier | Terminal Financier",
    page_icon="🇨🇭",
    layout="wide",
)

# Design épuré & futuriste
st.markdown(
    """
    <style>
    .main { background-color: #05050a; color: #e0e6ed; }
    .cyber-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-left: 4px solid #00f0ff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    h1, h2, h3 { color: #ffffff; }
    </style>
""",
    unsafe_allow_html=True,
)

# Connexion sécurisée à l'IA Cloud via Groq et les Secrets Streamlit
try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=st.secrets["GROQ_API_KEY"],
    )
except Exception as e:
    st.error(f"Erreur de configuration des Secrets Streamlit : {e}")

# Gestion des pages (Accueil vs App)
if "page" not in st.session_state:
    st.session_state.page = "accueil"

# --- PAGE 1 : ACCUEIL ---
if st.session_state.page == "accueil":
    st.title("🇨🇭 SwissNeoFrontier OS")
    st.markdown(
        "Votre simulateur financier et assistant privé pour travailleurs"
        " frontaliers (Propulsé par le Cloud)."
    )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
                <div class="cyber-card">
                    <h3>📊 Ce que fait l'outil</h3>
                    <p>• Calcule vos charges suisses et impôts précis.<br>
                    • Gère les couples non mariés (double salaire).<br>
                    • Affiche vos diagrammes de budget en direct.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
                <div class="cyber-card">
                    <h3>💬 L'Assistant IA Intervieweur</h3>
                    <p>• Discute avec vous pour comprendre vos projets.<br>
                    • Analyse votre reste à vivre et votre épargne.<br>
                    • Accessible 24/7 sur smartphone.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("🚀 LANCER LE SIMULATEUR", type="primary"):
        st.session_state.page = "app"
        st.rerun()

# --- PAGE 2 : APPLICATION ---
else:
    with st.sidebar:
        if st.button("🏠 Retour à l'accueil"):
            st.session_state.page = "accueil"
            st.rerun()

        st.header("⚙️ Paramètres")
        salaire_1 = st.number_input(
            "Salaire Brut 1 (CHF)", 1000.0, 50000.0, 8500.0, 100.0
        )
        situation = st.selectbox(
            "Situation", ["Celibataire", "En couple (Non mariés)", "Mariés"]
        )

        salaire_2 = 0.0
        if situation != "Celibataire":
            salaire_2 = st.number_input(
                "Salaire Brut 2 (Conjoint) (CHF)", 0.0, 50000.0, 5000.0, 100.0
            )

        canton = st.selectbox("Canton", ["geneve", "vaud", "valais"])
        regime = st.radio("Santé", ["LAMAL", "CMU"])
        loyer = st.number_input("Loyer / Crédit (€)", 0.0, 5000.0, 1200.0, 50.0)

    # Calculs basiques
    net_1 = salaire_1 * 0.875 * 1.05
    net_2 = salaire_2 * 0.875 * 1.05 if situation != "Celibataire" else 0
    total_net = net_1 + net_2
    epargne_estimee = total_net - loyer - 800

    st.title("🇨🇭 Terminal Financier & Assistant")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📊 Dashboard & Budget", "💬 Assistant IA"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        col1.metric("Salaire Net (Vous)", f"{net_1:,.2f} CHF")
        col2.metric("Salaire Net (Conjoint)", f"{net_2:,.2f} CHF")
        col3.metric("Reste à vivre estimé", f"{epargne_estimee:,.2f} €")

        st.markdown("---")
        st.subheader("📊 Diagramme de Répartition du Budget")

        df = pd.DataFrame({
            "Poste": ["Logement", "Charges & Loisirs", "Épargne / Investissement"],
            "Montant (€)": [loyer, 800.0, max(0.0, epargne_estimee)],
        })
        st.bar_chart(df.set_index("Poste"), color="#00f0ff")

    with tab2:
        st.subheader("💬 Discutez avec votre IA")

        if "messages" not in st.session_state:
            st.session_state.messages = [{
                "role": "assistant",
                "content": (
                    "Bonjour ! Je suis votre conseiller financier. Dites-moi, quel"
                    " est votre principal objectif en tant que frontalier (acheter"
                    " un bien, optimiser vos impôts, choisir LAMAL) ?"
                ),
            }]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Écrivez votre message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Réflexion de l'IA (Groq Cloud)..."):
                    try:
                        system_prompt = (
                            "Tu es un conseiller financier expert pour frontaliers"
                            " suisses. Réponds de façon unique, directe et utile à la"
                            f" dernière question. Situation actuelle : {situation},"
                            f" Salaire 1: {salaire_1} CHF, Salaire 2: {salaire_2} CHF."
                        )

                        formatted_msgs = [{"role": "system", "content": system_prompt}]
                        for m in st.session_state.messages:
                            formatted_msgs.append({"role": m["role"], "content": m["content"]})

                        # Appel direct et sécurisé avec un modèle de référence ultra-stable
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=formatted_msgs,
                            temperature=0.7,
                            max_tokens=1024,
                        )
                        reponse_ia = response.choices[0].message.content
                        st.markdown(reponse_ia)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": reponse_ia}
                        )
                    except Exception as e:
                        st.error(f"Erreur avec l'API Groq : {e}")
