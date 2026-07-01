import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Configuração da Interface (Layout Profissional)
st.set_page_config(page_title="Auditoria de Ativos - CDD Itabuna", layout="wide")

st.markdown("""
<style>
    .stApp {background-color: #f8f9fa;}
    .reportview-container .main .block-container {padding-top: 1rem;}
    .audit-card {border-left: 5px solid #2e86de; padding: 10px; background: white; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# Lógica de Auditoria (O "O que tem a ver com auditoria logística?")
# Auditoria Logística = Comparação de base (origem) vs. dado coletado (destino).
# Aqui: Preço de Compra (Base) vs. Preço de Mercado (Status Atual).

def obter_preco_scraping(ticker):
    # Simula a conferência de "status de entrega" do ativo no mercado
    try:
        url = f"https://statusinvest.com.br/opcoes/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=3)
        soup = BeautifulSoup(response.content, 'html.parser')
        val = soup.find('strong', class_='value d-block lh-4 fs-4 fw-700')
        return float(val.text.replace(',', '.')) if val else None
    except: return None

# Interface principal
st.title("🛡️ Auditoria e Monitoramento de Ativos")
st.caption("Unidade: CDD Itabuna | Foco: Gestão de Risco e Conformidade de Posições")

# Área de Auditoria (Interface)
with st.container():
    st.subheader("📋 Painel de Conferência de Posições")
    
    # Simulação da base de dados de auditoria
    conn = sqlite3.connect("terminal_b3.db")
    df = pd.read_sql_query("SELECT * FROM operacoes", conn)
    conn.close()

    if not df.empty:
        df['Auditoria_Status'] = df.apply(lambda row: 'Conforme' if row['preco_compra'] > 0 else 'Discrepância', axis=1)
        
        # Display dos ativos como "Itens sob Auditoria"
        for _, item in df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Ativo", item['ticker'].replace(".SA", ""))
                col2.metric("Base (Compra)", f"R$ {item['preco_compra']:.2f}")
                
                # O sistema audita se houve desvio
                preco_mercado = obter_preco_scraping(item['ticker'].replace(".SA", "")) or item['preco_compra']
                col3.metric("Mercado (Atual)", f"R$ {preco_mercado:.2f}")
                
                delta = ((preco_mercado - item['preco_compra']) / item['preco_compra']) * 100
                col4.metric("Desvio (Auditoria)", f"{delta:.2f}%")
    else:
        st.warning("Nenhuma ocorrência de ativo registrada para auditoria.")

# Área de Registro de Ocorrências (O seu "input" de auditor)
with st.sidebar:
    st.header("⚙️ Ferramentas de Auditor")
    ticker_input = st.text_input("Registrar Ativo para Auditoria:")
    valor_base = st.number_input("Preço de Base (Entrada):", format="%.2f")
    if st.button("Validar Posição"):
        # Adiciona ao seu "livro de registros"
        conn = sqlite3.connect("terminal_b3.db")
        c = conn.cursor()
        c.execute("INSERT INTO operacoes (id, ticker, preco_compra, tipo_ativo, qtd) VALUES (?,?,?,?,?)", 
                  (str(hash(datetime.now())), f"{ticker_input}.SA", valor_base, 'Ação', 1))
        conn.commit()
        conn.close()
        st.success("Ocorrência registrada no log.")
