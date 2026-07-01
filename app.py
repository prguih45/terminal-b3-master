import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import sqlite3
import hashlib
import uuid
import requests
from bs4 import BeautifulSoup

# ============ CONFIG ============
st.set_page_config(page_title="Terminal B3 Master", layout="wide")

# ============ SCRAPING B3 ============
def obter_preco_opcao_b3(ticker_opcao):
    try:
        url = f"https://statusinvest.com.br/opcoes/{ticker_opcao.replace('.SA', '')}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            preco_element = soup.find('strong', class_='value d-block lh-4 fs-4 fw-700')
            if preco_element:
                return float(preco_element.text.replace(',', '.'))
    except: return None
    return None

def calcular_preco(ticker, preco_compra, tipo_ativo):
    if tipo_ativo in ["Call", "Put"]:
        preco_scrap = obter_preco_opcao_b3(ticker)
        if preco_scrap: return preco_scrap, "Scraping"
    try:
        hist = yf.Ticker(ticker).history(period="1d")
        if not hist.empty: return float(hist['Close'].iloc[-1]), "API"
    except: pass
    return preco_compra, "Manual"

# ============ BANCO DE DADOS ============
DB_PATH = "terminal_b3.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS operacoes (id TEXT PRIMARY KEY, ticker TEXT, tipo_ativo TEXT, qtd INTEGER, preco_compra REAL, codigo_opcao TEXT, status TEXT DEFAULT 'Aberta', data_operacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit(); conn.close()

init_db()

# ============ INTERFACE ============
st.title("📊 Terminal B3 Master - Auditoria Logística")

# Botão de Atualização em Massa
if st.button("🔄 Forçar Atualização de Preços em Massa"):
    st.cache_data.clear()
    st.rerun()

st.info(f"🕒 Última verificação do sistema: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Exibição de Operações
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM operacoes", conn)
conn.close()

if not df.empty:
    lista_exibicao = []
    for _, op in df.iterrows():
        ticker_busca = f"{op['codigo_opcao']}.SA" if op['tipo_ativo'] in ["Call", "Put"] else op['ticker']
        preco_atual, origem = calcular_preco(ticker_busca, op['preco_compra'], op['tipo_ativo'])
        
        lucro = (preco_atual - op['preco_compra']) * op['qtd']
        icone = "🟢" if origem == "API" else "🔍" if origem == "Scraping" else "⚠️"
        
        lista_exibicao.append({
            "Ativo": op['codigo_opcao'] if op['codigo_opcao'] else op['ticker'].replace(".SA", ""),
            "Tipo": op['tipo_ativo'],
            "Qtd": op['qtd'],
            "Compra": f"R$ {op['preco_compra']:.2f}",
            "Atual": f"{icone} R$ {preco_atual:.2f}",
            "Resultado": f"R$ {lucro:.2f}"
        })
    
    st.dataframe(pd.DataFrame(lista_exibicao), use_container_width=True)
    st.caption("Legenda: 🟢 API Financeira | 🔍 Robô de Scraping | ⚠️ Preço Manual (Ajuste em 'Editar')")
else:
    st.warning("Nenhuma operação registrada.")

# Lançamento
st.subheader("➕ Lançar Nova Operação")
col1, col2, col3 = st.columns(3)
with col1: ticker = st.text_input("Ticker (Ex: BEEF3):").upper()
with col2: tipo = st.selectbox("Tipo:", ["Ação Pura", "Call", "Put"])
with col3: preco = st.number_input("Preço:", value=0.00)
cod_op = st.text_input("Código da Opção (se houver):").upper()

if st.button("Gravar"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO operacoes (id, ticker, tipo_ativo, qtd, preco_compra, codigo_opcao) VALUES (?,?,?,?,?,?)', 
              (str(uuid.uuid4()), f"{ticker}.SA", tipo, 100, preco, cod_op))
    conn.commit(); conn.close(); st.rerun()
