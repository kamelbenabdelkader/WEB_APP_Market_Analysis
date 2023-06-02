import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import pickle
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import json
# models
import pyfpgrowth
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules


# with open('basket_rules.pkl', 'rb') as f:
#     data_dict = pickle.load(f)


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

# Liste des pays
    country = ["France", "Netherlands", "Germany", "EIRE", "Spain"
                ,"Portugal", "Belgium", "Sweden", "Finland", "Bahrain", "Saudi Arabia"]

# Sélection du pays
    selected_country= st.selectbox('Choisissez un pays :', country)

    response = requests.get(f"https://apimarketanalysis.azurewebsites.net/{selected_country}")

    if response.status_code == 200:
                # Parsing the JSON response
                data = response.json()
                items = data["items"]
                df = pd.DataFrame(items)

                # Renommage des colonnes
                df.columns = ["InvoiceNo", "Description", "TotalQuantity"]
                # df1= df.head(10)
                # # Convertir le DataFrame en HTML sans l'index
                # df_html = df1.to_html(index=False)

                # # Affichage du tableau sans l'index
                # st.write(df_html, unsafe_allow_html=True)
                df_sorted = df.sort_values(by="TotalQuantity", ascending=False)
                df_sorted_html = df_sorted.head(10).to_html(index=False)
                st.write(df_sorted_html, unsafe_allow_html=True)
                # Convertir les données en tableau binaire (one-hot encoding)
                # df_encoded = pd.get_dummies(df_sorted["Description"])
                # st.write(df_encoded.head(1))
                # # # Appliquer l'algorithme Apriori pour trouver les itemsets fréquents
                # frequent_itemsets = apriori(df_encoded, min_support=0.01, use_colnames=True)
                # st.write(frequent_itemsets.head(1))
                # # # Générer les règles d'association
                # # Collecting the inferred rules in a dataframe
                # rules = association_rules(frequent_itemsets, metric ="lift", min_threshold = 1)
                # rules = rules.sort_values(['confidence', 'lift'], ascending =[False, False])
                # st.write(rules.head())

                # rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

                # # Afficher les règles d'association
                # st.write(rules)
                # # Displaying the results
                # st.table(items)
                # st.table(data_dict.get({selected_country}).sort_values(by="zhangs_metric", ascending = False).head(10))

    else:
                st.error("Error: Unable to retrieve items.")


def france_page():
    st.title("FRANCE")

    response = requests.get(f"https://apimarketanalysis.azurewebsites.net/france")

    if response.status_code == 200:
                # Parsing the JSON response
                data = response.json()
                items = data["items"]

                df = pd.DataFrame(items)

                # Renommage des colonnes
                df.columns = ["ID", "InvoiceNo", "StockCode", "Description", "Quantity",
                            "InvoiceDate", "UnitPrice", "CustomerID", "Country"]
                df1= df.head(2)
                # Convertir le DataFrame en HTML sans l'index
                df_html = df1.to_html(index=False)

                # Affichage du tableau sans l'index
                st.write(df_html, unsafe_allow_html=True)

                descriptions = [result[3] for result in data['items']]

                # Générer et afficher le nuage de mots
                fig: Figure
                ax: Axes
                fig, ax = plt.subplots()
                wordcloud = WordCloud(background_color='white', width=1200, height=1200).generate(str(descriptions))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)

                                #create basket dataframe
                basket = df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().reset_index().fillna(0).set_index('InvoiceNo')

                 #one hot encode the basket
                def encode_units(x):
                    if x <= 0:
                        return 0
                    if x >= 1:
                        return 1

                basket_sets = basket.applymap(encode_units)
                # st.write(basket_sets.head(10))
                #create minTransactions variable to represent the minimum number of baskets for support parameter
                minTransaction = 60
                totalTransactions = len(basket_sets.index)
                min_support_calc = minTransaction/totalTransactions
                st.metric(label='Number of Baskets', value=totalTransactions, delta=None)

                formatted_support_value = "{:.2%}".format(min_support_calc)
                formatted_support_value = f"{formatted_support_value}"

                st.metric(label='Minimum Support', value=formatted_support_value, delta=None,
                        delta_color='normal')
                 # Create frequent itemsets with the calculated minimum support
                frequent_itemsets = fpgrowth(basket_sets, min_support=min_support_calc, use_colnames=True)

                frequent_itemsets['itemsets'] = frequent_itemsets['itemsets'].apply(lambda x: ', '.join(list(x)))

                frequent_itemsets = frequent_itemsets.loc[~frequent_itemsets.apply(lambda row: 'POSTAGE' in row.values, axis=1)]
                st.write(frequent_itemsets.head())

                # Create association rules with the frequent itemsets
                rules = association_rules(frequent_itemsets, metric="support", min_threshold=min_support_calc, support_only=True)

                # Convert frozenset objects to strings
                rules['antecedents'] = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
                rules['consequents'] = rules['consequents'].apply(lambda x: ', '.join(list(x)))

                st.write(rules.head(10))



    else:
        st.error("Error: Unable to retrieve items.")

def portugal_page():

    st.title("Portugal")


    response1 = requests.get(f"https://apimarketanalysis.azurewebsites.net/portugal")

    if response1.status_code == 200:
                # Parsing the JSON response
                data = response1.json()
                items = data["items"]

                df = pd.DataFrame(items)

                # Renommage des colonnes
                df.columns = ["ID", "InvoiceNo", "StockCode", "Description", "Quantity",
                            "InvoiceDate", "UnitPrice", "CustomerID", "Country"]

                # Affichage du DataFrame dans une table Streamlit
                # Convert the dataset into the required format
                transactions = []
                for i in range(len(df)):
                    transaction = []
                    try:
                        transaction.append(str(df['InvoiceNo'][i]))
                        transaction.append(str(df['StockCode'][i]))
                        transaction.append(str(df['Quantity'][i]))
                        transaction.append(str(df['UnitPrice'][i]))
                        transaction.append(str(df['Description'][i]))
                        transaction.append(str(df['CustomerID'][i]))
                        transaction.append(str(df['InvoiceDate'][i]))
                        transactions.append(transaction)
                    except:
                        continue


                st.write(len(transactions))
                st.write(transactions[:1])

                # Perform frequent itemset mining using FPGrowth
                patterns = pyfpgrowth.find_frequent_patterns(transactions, 30)  # Adjust the support threshold as needed

                # Generate association rules from the frequent itemsets
                rules = pyfpgrowth.generate_association_rules(patterns, 0.7)  # Adjust the confidence threshold as needed
                # Create a DataFrame for frequent itemsets
                frequent_itemsets_df = pd.DataFrame.from_records(list(patterns.items()), columns=['Itemset', 'Support'])
                frequent_itemsets_df_sorted = frequent_itemsets_df.sort_values(by ='Support', ascending=False)

                # Create a DataFrame for association rules
                association_rules_df = pd.DataFrame.from_records(list(rules.items()), columns=['Rule', 'Confidence'])

                # Combine the frequent itemsets and association rules into a single DataFrame
                result_df = pd.concat([frequent_itemsets_df, association_rules_df], axis=1)
                result_df_sorted = result_df.sort_values(by ='Support', ascending=False)
                # items = data["items"]

                frequent_itemsets_df["Support_ratio"] = frequent_itemsets_df["Support"] / len(transactions)
                frequent_itemsets_df_sorted["Support_ratio"] = frequent_itemsets_df_sorted["Support"] / len(transactions)

                st.write(frequent_itemsets_df.head())

                association_rules_df[['Confidence', 'Confidence_score']] = association_rules_df['Confidence'].apply(pd.Series)
                association_rules_df = association_rules_df.rename(columns={'Rule': 'Antecedent', 'Confidence': 'Consequent'})
                association_rules_df_sorted = association_rules_df.sort_values(by ='Confidence_score', ascending=True)
                st.write(association_rules_df_sorted.head())
                # # Displaying the results as a table
                # st.table(items)

                descriptions = [result[3] for result in data['items']]

                # Générer et afficher le nuage de mots
                fig: Figure
                ax: Axes
                fig, ax = plt.subplots()
                wordcloud = WordCloud(background_color='white', width=1200, height=1200).generate(str(descriptions))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
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
