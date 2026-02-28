import streamlit as st
import pandas as pd

# 1. Configuration visuelle de la page web
st.set_page_config(page_title="Événements ÉTS", page_icon="🎓", layout="wide")

st.title("📅 Explorateur des événements de l'ÉTS")
st.markdown("Trouvez facilement les événements qui vous intéressent, et repérez les buffets !")

# 2. Chargement des données
# Le décorateur @st.cache_data est magique : il garde le CSV en mémoire 
# pour éviter de le recharger à chaque fois que tu cliques sur un filtre !
@st.cache_data
def charger_donnees():
    df = pd.read_csv('evenements_ets.csv')
    # On s'assure que les colonnes booléennes sont bien reconnues comme True/False
    df['Nourriture_Presente'] = df['Nourriture_Presente'].astype(bool)
    df['Boisson_Presente'] = df['Boisson_Presente'].astype(bool)
    return df

df_evenements = charger_donnees()

# 3. Création de la barre latérale pour les filtres
st.sidebar.header("🎯 Filtres")

# Cases à cocher
filtre_nourriture = st.sidebar.checkbox("🍕 Nourriture offerte")
filtre_boisson = st.sidebar.checkbox("☕ Boisson offerte")

# 4. Application des filtres
# On travaille sur une copie pour ne pas altérer les données d'origine
df_filtre = df_evenements.copy()

if filtre_nourriture:
    df_filtre = df_filtre[df_filtre['Nourriture_Presente'] == True]

if filtre_boisson:
    df_filtre = df_filtre[df_filtre['Boisson_Presente'] == True]

# 5. Affichage des résultats
st.subheader(f"{len(df_filtre)} événements correspondent à vos critères")

# On sélectionne seulement quelques colonnes pertinentes pour un affichage propre
colonnes_visuelles = ['Titre', 'Date_Label', 'Lieu', 'Prix_Inscription', 'Detail_Consommation', 'Lien_Inscription']

# st.dataframe génère un tableau interactif (on peut trier les colonnes en cliquant dessus !)
st.dataframe(df_filtre[colonnes_visuelles], use_container_width=True)