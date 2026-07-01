import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
import hashlib
import uuid
import plotly.express as px
import requests
from bs4 import BeautifulSoup

# ============ CONFIG ============
st.set_page_config(page_title="Terminal B3 Master", layout="wide")

# ============ FUNÇÃO DE SCRAPING (AUTOMAÇÃO DE PREÇO) ============
def obter_preco_opcao_b3(ticker_opcao):
    """Busca o preço da opção no Status Invest automaticamente"""
    try:
        url = f"https://statusinvest.com.br/opcoes/{ticker_opcao.replace('.SA', '')}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # O preço atual das opções no site fica nesta classe específica
            preco_element = soup.find('strong', class_='value d-block lh-4 fs-4 fw-700')
            if preco_element:
                preco_str = preco_element.text.replace(',', '.')
                return float(preco_str)
    except:
        return None
    return None

def calcular_preco_com_status(ticker, preco_compra, tipo_ativo):
    """Motor inteligente: Tenta Scraping, depois Yahoo, por fim Fallback"""
    # 1. Se for opção, tenta o Scraping primeiro
    if tipo_ativo in ["Call", "Put"]:
        preco_scrap = obter_preco_opcao_b3(ticker)
        if preco_scrap:
            return preco_scrap, "Scraping"
            
    # 2. Tenta via Yahoo Finance
    try:
        hist = yf.Ticker(ticker).history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1]), "API"
    except:
        pass
        
    # 3. Fallback manual
    return preco_compra, "Manual"

# ... (Mantenha aqui TODAS as suas funções de BANCO DE DADOS, AUTH, e as TABS como estavam no código anterior) ...
# Apenas substitua a lógica de cálculo dentro da TAB 1 e TAB 3 por esta nova função acima.
