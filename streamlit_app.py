import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import pickle
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud


# model = pickle.load(open('model.pkl', 'rb'))

# # Fonction qui charge le modèle entraîné
# def load_model():
#     with open('model.plk', 'rb') as f:
#         model = pickle.load(f)
#     return model

# # Charger le modèle entraîné
# model = load_model()

# Fonction qui charge le fichier css
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")


# Appel à l'API pour récupérer les informations de vol
url = "https://apimarketanalysis.azurewebsites.net/france"
response = requests.get(url)
dataFrance = response.json()
url2 = "https://apimarketanalysis.azurewebsites.net/portugal"
response = requests.get(url2)
dataPortugal = response.json()

def home_page():
    st.title("HOME")
    st.markdown("---")

    # User input for country
    country = st.text_input("Entrée un Pays:")

    # Button to trigger the API request
    if st.button("Envoyer"):
        if country:
            # API request to FastAPI endpoint
            response = requests.get(f"https://apimarketanalysis.azurewebsites.net/{country}")

            if response.status_code == 200:
                # Parsing the JSON response
                data = response.json()
                items = data["items"]

                # Displaying the results
                st.table(items)
            else:
                st.error("Error: Unable to retrieve items.")
        else:
            st.warning("Veuillez entrée un Pays avec la 1er lettre en Majuscule.")

def france_page():
    st.title("FRANCE")

    response = requests.get(f"https://apimarketanalysis.azurewebsites.net/france")

    if response.status_code == 200:
                # Parsing the JSON response
                data = response.json()
                items = data["items"]

                # Displaying the results as a table
                st.table(items)

        # # Grouping description based on countries
        #         z = data['Description'].groupby(data['Country'])
        #         p = []
        #         q = []
        #         for name, group in z:
        #             p.append(name)
        #             q.append(group)

        # # Items description of France country through Wordcloud
        #         wordcloud = WordCloud(background_color='white', width=1200, height=1200).generate(str(q[15]))
        #         plt.imshow(wordcloud)
        #         plt.axis("off")
        #         st.pyplot()

    else:
        st.error("Error: Unable to retrieve items.")

def portugal_page():

    st.title("Portugal")


    response = requests.get(f"https://apimarketanalysis.azurewebsites.net/france")

    if response.status_code == 200:
                # Parsing the JSON response
                data = response.json()
                items = data["items"]

                # Displaying the results
                st.table(items)
    else:
                st.error("Error: Unable to retrieve items.")


#---------------------  Sidebar  ----------------------#
# Menu déroulant pour sélectionner la page à afficher
menu = ["HOME", "FRANCE", "PORTUGAL"]
choice = st.sidebar.selectbox(" ", menu)



# Affichage de la page correspondant à la sélection du menu
if choice == "HOME":
    home_page()
elif choice == "FRANCE":
    france_page()
else:
    portugal_page()
