import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

url_api = "https://www.etsmtl.ca/api/evenements/get"

# Simulation d'un vrai navigateur pour ne pas être bloqué
en_tetes = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3 Safari/605.1.15",
    "Accept": "application/json"
}
# Requête POST à l'API
reponse = requests.post(url_api, headers=en_tetes)

print("Code de statut :", reponse.status_code)
if reponse.status_code == 200: # Vérification du statut
    donnees_json = reponse.json()
    
    print("\nClés du dictionnaire principal :")
    print(donnees_json.keys()) 
else:
    print("Erreur lors de la requête")

urls = [] # récupératon des urls
for donnee in donnees_json['eventsData']: # donnees_json['eventsData'] est une liste de dictionnaires, chaque dictionnaire représentant un événement
    urls.append([donnee['id'],donnee['url'],donnee['title'],donnee['dateLabel'],donnee['startTime'],donnee['endTime']]) # on stocke l'id de l'événement comme clé et une liste contenant l'url, le titre et la date comme valeur
# print(len(urls))

# print(donnees_json['eventsData'][1])
print('-----------------------------')
# print(urls[1])

# url_test = [["https://www.etsmtl.ca/evenement/mini-conference-ieee?date=2026-03-10"]]

for url in urls:
    page = requests.get(url[1], headers=en_tetes)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        sidebar = soup.find('div', class_='c-floated-sidebar')
        # print(sidebar)

        # Stockage infos pertinentes
        lieu = None
        prix_inscription = None
        lien_inscription = None
        mode = None
        date = None
        info = None


        # Récupération de tous les blocs d'infos
        blocs_items = sidebar.find_all('div', class_='o-boxed-info__item')
        

        for bloc in blocs_items:
            
            # Récupération du titre
            balise_titre = bloc.find('div', class_='o-boxed-info__title') 
            
            if balise_titre: # Vérif non vide
                # Extraction titre - sécuriation en minuscules
                titre = balise_titre.text.strip().lower()
                
                # Extraction caractéristiques du bloc
                if "lieu" in titre or "local" in titre:
                    balise_texte = bloc.find('div', class_='o-boxed-info__text')
                    if balise_texte: # Vérif non vide
                        lieu = balise_texte.text.strip()
                elif "date" in titre:
                    balise_texte = bloc.find('div', class_='o-boxed-info__text')
                    if balise_texte:
                        date = balise_texte.text.strip()
                elif "mode" in titre:
                    balise_texte = bloc.find('div', class_='o-boxed-info__text')
                    if balise_texte:
                        mode = balise_texte.text.strip()
                elif "inscription" in titre:
                    balise_lien = bloc.find('a')
                    if balise_lien :
                        prix_inscription = balise_lien.text.strip()
                        if 'href' in balise_lien.attrs:
                            lien_inscription = balise_lien['href']
                
        url.append(lieu)
        url.append(date)
        url.append(mode)
        url.append(prix_inscription)
        url.append(lien_inscription)
                
        balise_info = soup.find('div', class_='c-fold__subtitle o-text') or soup.find('div', class_='o-text')
        nourriture_presente = False
        boisson_presente = False
        detail_consommation = None

        if balise_info:
            info = balise_info.text.strip()
            url.append(info)



            mots_nourriture = ['pizza', 'buffet', 'repas', 'goûter', 'gouter', 'popcorn', 'collation', 'dîner',
                               'diner', 'nourriture', 'bouchées', 'déjeuner', 'dejeuner', 'snack', 'casse-croûte', 
                               'casse-croute', 'apéritif', 'aperitif', 'apéritifs', 'aperitifs', 'amuse-gueule', 'amuse-gueules', 'amuse-gueule',
                               'amuse-gueules', "hors-d'œuvre", 'hors-doeuvre', 'dessert', 'gateau', 'gâteau',
                               'sucrerie', 'sucreries', 'salé', 'sale', 'salées', 'salees', 'saléé', 'salee',
                               ]
            mots_boisson = ['boisson', 'breuvage', 'café', 'cafe', 'thé', 'the' 'bière', 'rafraîchissement', 'verre',
                            'cocktail', 'soda', 'jus', 'eau', 'alcool', 'alcoolisé', 'alcoolise', 'alcoolisée', 'alcoolisee',
                            'alcoolisés', 'alcoolises', 'alcoolisées', 'alcoolisees']

            paragraphes = balise_info.find_all('p')
    
            for p in paragraphes:
                texte_p = p.text.strip()
                
                # NOUVEAU : On découpe le paragraphe en une liste de phrases
                # (?<=[.!?]) : Regarde si le caractère précédent est un point, ! ou ?
                # \s+ : Coupe au niveau de l'espace (ou des espaces) qui suit
                phrases = re.split(r'(?<=[.!?])\s*(?=[A-ZÀ-Ÿ])', texte_p)
                
                # On analyse maintenant phrase par phrase (et non plus tout le paragraphe)
                for phrase in phrases:
                    phrase_minuscule = phrase.lower()
                    
                    # --- Détection Nourriture ---
                    if any(re.search(r'\b' + mot + r'\b', phrase_minuscule) for mot in mots_nourriture):
                        nourriture_presente = True
                        
                        if detail_consommation is None:
                            detail_consommation = phrase # On garde juste LA phrase
                        elif phrase not in detail_consommation: 
                            detail_consommation += " | " + phrase
                            
                    # --- Détection Boisson ---
                    if any(re.search(r'\b' + mot + r'\b', phrase_minuscule) for mot in mots_boisson):
                        boisson_presente = True
                        
                        if detail_consommation is None:
                            detail_consommation = phrase
                        elif phrase not in detail_consommation: 
                            detail_consommation += " | " + phrase


        else :
            url.append(info) # Si aucune info trouvée, on ajoute None pour garder la structure
        url.append(nourriture_presente)
        url.append(boisson_presente)
        url.append(detail_consommation)

        
# 1. On définit le nom des colonnes dans l'ordre exact de tes 'append'
colonnes = [
    'ID', 'URL', 'Titre', 'Date_Label', 'Heure_Debut', 'Heure_Fin', 
    'Lieu', 'Date', 'Mode', 'Prix_Inscription', 'Lien_Inscription', 
    'Description', 'Nourriture_Presente', 'Boisson_Presente', 'Detail_Consommation'
]

# 2. Création du DataFrame
df_evenements = pd.DataFrame(urls, columns=colonnes)

# 3. Sauvegarde en fichier CSV
# L'argument index=False évite de rajouter une colonne de numérotation inutile
df_evenements.to_csv('evenements_ets.csv', index=False, encoding='utf-8')

print("Fichier CSV généré avec succès !")
