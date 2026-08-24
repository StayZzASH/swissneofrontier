import pandas as pd
import streamlit as st
from openai import OpenAI

# Configuration de la page
st.set_page_config(
    page_title="SwissNeoFrontier | Terminal Financier Avancé",
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
    st.title("🇨🇭 SwissNeoFrontier OS - Édition Complète")
    st.markdown(
        "Votre terminal financier et assistant intelligent pour frontaliers suisses :"
        " Impôts, Santé (LAMAL/CMU) et Investissement Immobilier en France."
    )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
                <div class="cyber-card">
                    <h3>📊 Modules Financiers</h3>
                    <p>• Calculateur Net / Brut par Canton.<br>
                    • Comparateur Santé LAMAL vs CMU chiffré.<br>
                    • Analyse de la capacité d'emprunt transfrontalier.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
                <div class="cyber-card">
                    <h3>🏡 Immobilier & IA</h3>
                    <p>• Simulation Résidence Principale + 2 Locatifs.<br>
                    • Calcul d'autofinancement et reste à vivre en Euros.<br>
                    • Assistant IA contextuel 24/7.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("🚀 LANCER LE TERMINAL", type="primary"):
        st.session_state.page = "app"
        st.rerun()

# --- PAGE 2 : APPLICATION ---
else:
    with st.sidebar:
        if st.button("🏠 Retour à l'accueil"):
            st.session_state.page = "accueil"
            st.rerun()

        st.header("⚙️ Paramètres Salariaux & Fiscaux")
        salaire_1 = st.number_input(
            "Salaire Brut 1 (CHF/mois)", 1000.0, 50000.0, 8500.0, 100.0
        )
        situation = st.selectbox(
            "Situation familiale", ["Celibataire", "En couple (Non mariés)", "Mariés"]
        )

        salaire_2 = 0.0
        if situation != "Celibataire":
            salaire_2 = st.number_input(
                "Salaire Brut 2 (Conjoint) (CHF/mois)", 0.0, 50000.0, 5000.0, 100.0
            )

        canton = st.selectbox("Canton de travail", ["geneve", "vaud", "valais"])
        regime_sante = st.radio("Régime d'Assurance Maladie", ["LAMAL", "CMU"])
        
        st.header("🏡 Paramètres Immobiliers")
        loyer_actuel = st.number_input("Loyer / Crédit Actuel (€)", 0.0, 5000.0, 1200.0, 50.0)
        prix_maison = st.number_input("Cible : Maison Principale Frontière (€)", 0.0, 1000000.0, 450000.0, 10000.0)
        prix_locatif_1 = st.number_input("Cible : Appartement Locatif 1 (€)", 0.0, 500000.0, 150000.0, 5000.0)
        loyer_locatif_1 = st.number_input("Loyer estimé Locatif 1 (€/mois)", 0.0, 3000.0, 750.0, 25.0)
        prix_locatif_2 = st.number_input("Cible : Appartement Locatif 2 (€)", 0.0, 500000.0, 150000.0, 5000.0)
        loyer_locatif_2 = st.number_input("Loyer estimé Locatif 2 (€/mois)", 0.0, 3000.0, 750.0, 25.0)

    # --- CALCULS FINANCIERS AVANCÉS ---
    # Taux de change estimé CHF -> EUR (env. 1.05)
    taux_change = 1.05

    # Charges sociales suisses estimées (~12.5%)
    net_1_chf = salaire_1 * 0.875
    net_2_chf = salaire_2 * 0.875 if situation != "Celibataire" else 0
    total_net_chf = net_1_chf + net_2_chf

    # Impôt à la source estimé selon canton (~15% à 22%)
    taux_impot = 0.18 if canton == "geneve" else (0.16 if canton == "vaud" else 0.14)
    impot_estime_chf = total_net_chf * taux_impot
    
    # Santé (LAMAL ~350 CHF/pers/mois vs CMU ~8% du revenu fiscal converti)
    nb_personnes = 2 if situation != "Celibataire" else 1
    cout_sante_chf = (350 * nb_personnes) if regime_sante == "LAMAL" else ((total_net_chf * 12 * 0.08) / 12)

    # Net disponible en CHF puis converti en Euros
    disponible_chf = total_net_chf - impot_estime_chf - cout_sante_chf
    disponible_eur = disponible_chf * taux_change

    # Simulation Crédit Immobilier global (taux 3.5% sur 25 ans -> mensualité ~ 5 € pour 1000 € empruntés)
    facteur_mensualite = 0.005
    mensualite_maison = prix_maison * facteur_mensualite
    mensualite_loc1 = prix_locatif_1 * facteur_mensualite
    mensualite_loc2 = prix_locatif_2 * facteur_mensualite
    
    total_mensualites_credits = mensualite_maison + mensualite_loc1 + mensualite_loc2
    
    # Revenus locatifs pondérés à 70% par les banques françaises
    revenus_locatifs_pondérés = (loyer_locatif_1 + loyer_locatif_2) * 0.70
    revenu_global_eur_pour_banque = disponible_eur + revenus_locatifs_pondérés
    
    # Taux d'endettement global
    taux_endettement = (total_mensualites_credits / revenu_global_eur_pour_banque) if revenu_global_eur_pour_banque > 0 else 0
    reste_a_vivre_reel = revenu_global_eur_pour_banque - total_mensualites_credits

    # --- INTERFACE PRINCIPALE ---
    st.title("🇨🇭 Terminal Financier & Immobilier Frontalier")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard & Santé", "🏡 Investissement Immobilier (3 Biens)", "💬 Assistant IA"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        col1.metric("Revenu Net Suisse (Total)", f"{total_net_chf:,.2f} CHF")
        col2.metric(f"Impôts & Santé ({canton} / {regime_sante})", f"-{(impot_estime_chf + cout_sante_chf):,.2f} CHF")
        col3.metric("Reste à vivre net (€)", f"{disponible_eur:,.2f} €", delta=f"Change: {taux_change}")

        st.markdown("---")
        st.subheader("💡 Comparatif Santé & Charges")
        
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**Régime choisi : {regime_sante}**\n\n"
                    f"• Coût estimé : **{cout_sante_chf:,.2f} CHF / mois**\n"
                    f"• Impact Canton ({canton}) : Impôt source estimé à **{impot_estime_chf:,.2f} CHF / mois**.")
        with c2:
            df_budget = pd.DataFrame({
                "Poste": ["Revenu Net", "Impôts Source", "Assurance Maladie", "Disponible Net"],
                "Montant (EUR)": [total_net_chf * taux_change, -impot_estime_chf * taux_change, -cout_sante_chf * taux_change, disponible_eur]
            })
            st.bar_chart(df_budget.set_index("Poste"), color="#00f0ff")

    with tab2:
        st.subheader("🏡 Analyse de Projet Immobilier (Maison + 2 Locatifs)")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Mensualité Totale Crédits", f"{total_mensualites_credits:,.2f} € / mois")
        m2.metric("Taux d'endettement estimé", f"{taux_endettement * 100:.1f} %", 
                  delta="Validé (< 35%)" if taux_endettement <= 0.35 else "Attention (> 35%)", 
                  delta_color="normal" if taux_endettement <= 0.35 else "inverse")
        m3.metric("Reste à vivre après crédits", f"{reste_a_vivre_reel:,.2f} € / mois")

        st.markdown("---")
        st.markdown("""
        > **Note sur le montage bancaire transfrontalier :** 
        > * Les banques françaises prennent en compte **70% des revenus locatifs** de tes 2 appartements pour calculer ton ratio d'endettement.
        > * Le seuil maximal d'endettement toléré en France est généralement de **35%** de tes revenus nets globaux convertis en Euros.
        """)

        # Détail des biens
        data_immo = pd.DataFrame({
            "Bien": ["Maison Principale Frontière", "Appartement Locatif 1", "Appartement Locatif 2"],
            "Prix d'achat (€)": [prix_maison, prix_locatif_1, prix_locatif_2],
            "Loyer / Valeur locative (€)": [0, loyer_locatif_1, loyer_locatif_2],
            "Mensualité de crédit estimée (€)": [mensualite_maison, mensualite_loc1, mensualite_loc2]
        })
        st.table(data_immo)

    with tab3:
        st.subheader("💬 Discutez avec votre Conseiller IA")

        if "messages" not in st.session_state:
            st.session_state.messages = [{
                "role": "assistant",
                "content": (
                    "Bonjour ! Je suis votre conseiller financier expert pour frontaliers. "
                    "J'ai pris en compte votre salaire, votre choix de santé ({regime_sante}), "
                    "votre canton ({canton}) et vos projets immobiliers (1 maison + 2 locatifs). "
                    "Que souhaitez-vous analyser en premier ?"
                ),
            }]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Posez votre question sur vos impôts, la LAMAL ou vos crédits immo..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Réflexion de l'IA (Groq Cloud)..."):
                    try:
                        system_prompt = (
                            f"Tu es un conseiller financier expert pour frontaliers suisses. "
                            f"Situation actuelle : {situation}, Salaire 1: {salaire_1} CHF, Salaire 2: {salaire_2} CHF. "
                            f"Canton : {canton}, Régime santé : {regime_sante}. "
                            f"Projet immo : Maison à {prix_maison}€, 2 apparts locatifs de {prix_locatif_1}€ et {prix_locatif_2}€ "
                            f"générant {loyer_locatif_1 + loyer_locatif_2}€ de loyer. "
                            f"Taux d'endettement calculé : {taux_endettement*100:.1f}%. "
                            f"Réponds de façon précise, technique et directement utile."
                        )

                        formatted_msgs = [{"role": "system", "content": system_prompt}]
                        for m in st.session_state.messages:
                            formatted_msgs.append({"role": m["role"], "content": m["content"]})

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
