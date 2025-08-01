import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd

# === Config
st.set_page_config(page_title="Suivi IA des Actions", layout="wide")

ACTIONS = {
    "Sanofi": "SAN.PA",
    "Siemens Energy": "ENR.DE",
    "Airbus": "AIR.PA",
    "Stellantis": "STLA.PA",
    "Eiffage": "FGR.PA",
    "Teleperformance": "TEP.PA"
}

SEUILS = [-3, -5, -7]

def variation_percent(ticker):
    data = yf.Ticker(ticker)
    hist = data.history(period="2d")

    if len(hist) < 2:
        return None

    close_today = hist['Close'].iloc[-1]
    close_yesterday = hist['Close'].iloc[-2]
    variation = ((close_today - close_yesterday) / close_yesterday) * 100
    return round(variation, 2)

def get_boursorama_news(company_name):
    search_url = f"https://www.boursorama.com/recherche/?q={company_name.replace(' ', '+')}"
    try:
        r = requests.get(search_url, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        articles = soup.select("div.c-list-news__content > a.c-list-news__link")

        news = []
        for a in articles[:5]:
            title = a.text.strip()
            link = "https://www.boursorama.com" + a['href']
            news.append((title, link))
        return news
    except Exception as e:
        return [("Erreur de récupération", "")]

# === Interface Streamlit
st.title("📉 Agent IA – Suivi Boursier avec Actualités")

if st.button("📊 Lancer l’analyse"):
    results = []

    for nom, symbole in ACTIONS.items():
        variation = variation_percent(symbole)
        alert = None
        for seuil in SEUILS:
            if variation is not None and variation <= seuil:
                alert = f"🔻 Alerte : baisse de {variation}% (seuil : {seuil}%)"
                break

        news = get_boursorama_news(nom)

        results.append({
            "Nom": nom,
            "Symbole": symbole,
            "Variation": variation,
            "Alerte": alert if alert else "✅ Aucun signal",
            "Actualités": news
        })

    for res in results:
        st.subheader(f"{res['Nom']} ({res['Symbole']})")
        st.write(f"📉 Variation : {res['Variation']}%")
        st.write(res['Alerte'])

        st.markdown("📰 **Actualités Boursorama :**")
        for titre, lien in res["Actualités"]:
            st.markdown(f"- [{titre}]({lien})")
        st.markdown("---")
