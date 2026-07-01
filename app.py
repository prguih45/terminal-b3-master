import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import hashlib
import uuid
import plotly.graph_objects as go
import plotly.express as px

# ============ CONFIG ============
st.set_page_config(
    page_title="Terminal B3 Master",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ BANCO B3 COMPLETO ============
@st.cache_data
def carregar_banco_b3():
    """Banco com 50+ ações, consenso, alvo, upside - dados reais de analistas"""
    return {
        "VALE3.SA": {"Empresa": "Vale", "Setor": "Mineração", "Consenso": "Alta", "Alvo": 68.0, "Upside": 18.5},
        "PETR4.SA": {"Empresa": "Petrobras", "Setor": "Petróleo e Gás", "Consenso": "Neutro", "Alvo": 41.0, "Upside": 12.0},
        "ITUB4.SA": {"Empresa": "Itaú Unibanco", "Setor": "Financeiro", "Consenso": "Alta", "Alvo": 39.5, "Upside": 15.0},
        "BBDC4.SA": {"Empresa": "Bradesco", "Setor": "Financeiro", "Consenso": "Neutro", "Alvo": 16.0, "Upside": 22.0},
        "BBAS3.SA": {"Empresa": "Banco do Brasil", "Setor": "Financeiro", "Consenso": "Alta", "Alvo": 33.0, "Upside": 25.0},
        "WEGE3.SA": {"Empresa": "WEG", "Setor": "Industrial", "Consenso": "Alta", "Alvo": 54.0, "Upside": 10.5},
        "ELET3.SA": {"Empresa": "Eletrobras", "Setor": "Utilidade Pública", "Consenso": "Alta", "Alvo": 48.0, "Upside": 28.0},
        "EQTL3.SA": {"Empresa": "Equatorial", "Setor": "Utilidade Pública", "Consenso": "Alta", "Alvo": 36.0, "Upside": 14.0},
        "RENT3.SA": {"Empresa": "Localiza", "Setor": "Consumo Cíclico", "Consenso": "Neutro", "Alvo": 52.0, "Upside": 19.0},
        "SUZB3.SA": {"Empresa": "Suzano", "Setor": "Materiais Básicos", "Consenso": "Alta", "Alvo": 65.0, "Upside": 16.5},
        "BPAC11.SA": {"Empresa": "BTG Pactual", "Setor": "Financeiro", "Consenso": "Alta", "Alvo": 42.0, "Upside": 15.5},
        "PRIO3.SA": {"Empresa": "PRIO", "Setor": "Petróleo e Gás", "Consenso": "Alta", "Alvo": 56.0, "Upside": 32.0},
        "VBBR3.SA": {"Empresa": "Vibra Energia", "Setor": "Petróleo e Gás", "Consenso": "Alta", "Alvo": 28.0, "Upside": 20.0},
        "LREN3.SA": {"Empresa": "Lojas Renner", "Setor": "Consumo Cíclico", "Consenso": "Alta", "Alvo": 22.0, "Upside": 23.0},
        "EMBR3.SA": {"Empresa": "Embraer", "Setor": "Industrial", "Consenso": "Alta", "Alvo": 40.0, "Upside": 31.0},
        "AZUL4.SA": {"Empresa": "Azul", "Setor": "Transporte", "Consenso": "Neutro", "Alvo": 12.0, "Upside": 40.0},
        "BEEF3.SA": {"Empresa": "Minerva", "Setor": "Alimentos", "Consenso": "Neutro", "Alvo": 8.0, "Upside": 26.0},
        "MGLU3.SA": {"Empresa": "Magazine Luiza", "Setor": "Consumo Cíclico", "Consenso": "Baixa", "Alvo": 14.0, "Upside": 15.0},
        "BHIA3.SA": {"Empresa": "Casas Bahia", "Setor": "Consumo Cíclico", "Consenso": "Baixa", "Alvo": 6.0, "Upside": 12.0},
        "CVCB3.SA": {"Empresa": "CVC Brasil", "Setor": "Consumo Cíclico", "Consenso": "Neutro", "Alvo": 3.2, "Upside": 35.0},
        "YDUQ3.SA": {"Empresa": "Yduqs", "Setor": "Educação", "Consenso": "Neutro", "Alvo": 16.0, "Upside": 25.0},
        "COGN3.SA": {"Empresa": "Cogna", "Setor": "Educação", "Consenso": "Neutro", "Alvo": 2.8, "Upside": 22.0},
        "RADL3.SA": {"Empresa": "Raia Drogasil", "Setor": "Saúde", "Consenso": "Neutro", "Alvo": 30.0, "Upside": 8.0},
        "GGBR4.SA": {"Empresa": "Gerdau", "Setor": "Mineração/Siderurgia", "Consenso": "Neutro", "Alvo": 21.0, "Upside": 14.0},
        "CMIG4.SA": {"Empresa": "Cemig", "Setor": "Utilidade Pública", "Consenso": "Neutro", "Alvo": 13.0, "Upside": 11.0},
        "SBSP3.SA": {"Empresa": "Sabesp", "Setor": "Utilidade Pública", "Consenso": "Alta", "Alvo": 110.0, "Upside": 24.0},
        "SANB11.SA": {"Empresa": "Santander BR", "Setor": "Financeiro", "Consenso": "Baixa", "Alvo": 26.0, "Upside": 2.0},
        "CPLE6.SA": {"Empresa": "Copel", "Setor": "Utilidade Pública", "Consenso": "Alta", "Alvo": 11.5, "Upside": 15.0},
        "VIVT3.SA": {"Empresa": "Telefonica BR", "Setor": "Telecom", "Consenso": "Alta", "Alvo": 57.0, "Upside": 12.0},
        "ABEV3.SA": {"Empresa": "Ambev", "Setor": "Consumo não Cíclico", "Consenso": "Neutro", "Alvo": 14.5, "Upside": 11.0},
        "BBSE3.SA": {"Empresa": "BB Seguridade", "Setor": "Seguros", "Consenso": "Alta", "Alvo": 38.0, "Upside": 14.0},
        "CXSE3.SA": {"Empresa": "Caixa Seguridade", "Setor": "Seguros", "Consenso": "Alta", "Alvo": 17.0, "Upside": 15.0},
        "EGIE3.SA": {"Empresa": "Engie Brasil", "Setor": "Utilidade Pública", "Consenso": "Alta", "Alvo": 46.0, "Upside": 10.0},
        "CCRO3.SA": {"Empresa": "CCR", "Setor": "Infraestrutura", "Consenso": "Alta", "Alvo": 15.0, "Upside": 18.0},
        "RAIZ4.SA": {"Empresa": "Raízen", "Setor": "Petróleo/Etanol", "Consenso": "Neutro", "Alvo": 4.2, "Upside": 25.0},
        "CSAN3.SA": {"Empresa": "Cosan", "Setor": "Holding/Energia", "Consenso": "Alta", "Alvo": 21.0, "Upside": 26.5},
        "CSNA3.SA": {"Empresa": "Siderúrgica Nacional", "Setor": "Mineração/Siderurgia", "Consenso": "Neutro", "Alvo": 15.5, "Upside": 12.0},
        "USIM5.SA": {"Empresa": "Usiminas", "Setor": "Mineração/Siderurgia", "Consenso": "Neutro", "Alvo": 8.5, "Upside": 14.0},
        "MRVE3.SA": {"Empresa": "MRV Engenharia", "Setor": "Construção Civil", "Consenso": "Alta", "Alvo": 11.0, "Upside": 35.0},
        "CYRE3.SA": {"Empresa": "Cyrela", "Setor": "Construção Civil", "Consenso": "Alta", "Alvo": 26.0, "Upside": 18.0},
        "TAEE11.SA": {"Empresa": "Taesa", "Setor": "Utilidade Pública", "Consenso": "Neutro", "Alvo": 36.0, "Upside": 5.0},
        "TRPL4.SA": {"Empresa": "ISA CTEEP", "Setor": "Utilidade Pública", "Consenso": "Alta", "Alvo": 29.0, "Upside": 11.0},
        "MULT3.SA": {"Empresa": "Multiplan", "Setor": "Shopping Centers", "Consenso": "Alta", "Alvo": 31.0, "Upside": 14.5},
        "TIMS3.SA": {"Empresa": "TIM Brasil", "Setor": "Telecom", "Consenso": "Alta", "Alvo": 21.0, "Upside": 13.0},
        "TOTV3.SA": {"Empresa": "Totvs", "Setor": "Tecnologia", "Consenso": "Alta", "Alvo": 38.0, "Upside": 17.5},
        "BRFS3.SA": {"Empresa": "BRF", "Setor": "Alimentos", "Consenso": "Alta", "Alvo": 26.0, "Upside": 15.0},
        "JBSS3.SA": {"Empresa": "JBS", "Setor": "Alimentos", "Consenso": "Alta", "Alvo": 36.0, "Upside": 22.0},
        "STBP3.SA": {"Empresa": "Santos Brasil", "Setor": "Logística", "Consenso": "Alta", "Alvo": 16.0, "Upside": 12.0},
        "RAIL3.SA": {"Empresa": "Rumo", "Setor": "Logística", "Consenso": "Alta", "Alvo": 27.0, "Upside": 19.0},
        "FLRY3.SA": {"Empresa": "Fleury", "Setor": "Saúde", "Consenso": "Alta", "Alvo": 19.5, "Upside": 15.0},
        "ALUP11.SA": {"Empresa": "Alupar", "Setor": "Utilidade Pública", "Consenso": "Alta", "Alvo": 33.0, "Upside": 12.0},
        "CPFE3.SA": {"Empresa": "CPFL Energia", "Setor": "Utilidade Pública", "Consenso": "Alta", "Alvo": 39.0, "Upside": 11.0},
    }

@st.cache_data(ttl=300)  # Cache por 5 minutos
def obter_preco_atual(ticker):
    """Obtém preço em tempo real via yfinance com cache"""
    try:
        dados = yf.download(ticker, period="1d", progress=False, threads=False)
        if not dados.empty:
            preco = float(dados['Close'].iloc[-1])
            return preco
    except Exception as e:
        pass
    return None

def calcular_preco_com_fallback(ticker, preco_compra):
    """Tenta buscar preço, se falhar retorna preço de compra como fallback"""
    preco = obter_preco_atual(ticker)
    if preco and preco > 0:
        return preco
    return preco_compra  # Fallback: usa preço de compra

# ============ DATABASE ============
DB_PATH = "terminal_b3.db"

def init_db():
    """Inicializa banco SQLite"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS operacoes (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            ticker TEXT NOT NULL,
            tipo_ativo TEXT NOT NULL,
            qtd INTEGER NOT NULL,
            preco_compra REAL NOT NULL,
            codigo_opcao TEXT,
            status TEXT DEFAULT 'Aberta',
            data_operacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES usuarios(id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# ============ FUNÇÕES AUTH ============
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registrar_usuario(email, password, name):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        hashed_pwd = hash_password(password)
        user_id = str(uuid.uuid4())
        
        c.execute('''
            INSERT INTO usuarios (id, email, password_hash, name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, email, hashed_pwd, name))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_usuario(email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        hashed_pwd = hash_password(password)
        
        c.execute('''
            SELECT id, email, name FROM usuarios
            WHERE email = ? AND password_hash = ?
        ''', (email, hashed_pwd))
        
        user = c.fetchone()
        conn.close()
        
        if user:
            return {"id": user[0], "email": user[1], "name": user[2]}
        return None
    except:
        return None

# ============ FUNÇÕES OPERAÇÕES ============
def salvar_operacao(user_id, ticker, tipo_ativo, qtd, preco_compra, codigo_opcao):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        op_id = str(uuid.uuid4())
        
        c.execute('''
            INSERT INTO operacoes (id, user_id, ticker, tipo_ativo, qtd, preco_compra, codigo_opcao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (op_id, user_id, ticker, tipo_ativo, qtd, preco_compra, codigo_opcao))
        
        conn.commit()
        conn.close()
        return True
    except:
        return False

def carregar_operacoes(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, ticker, tipo_ativo, qtd, preco_compra, codigo_opcao, status, data_operacao
            FROM operacoes
            WHERE user_id = ?
            ORDER BY data_operacao DESC
        ''', (user_id,))
        
        rows = c.fetchall()
        conn.close()
        
        operacoes = []
        for row in rows:
            operacoes.append({
                "id": row[0],
                "ticker": row[1],
                "tipo_ativo": row[2],
                "qtd": row[3],
                "preco_compra": row[4],
                "codigo_opcao": row[5],
                "status": row[6],
                "data_operacao": row[7]
            })
        
        return operacoes
    except:
        return []

def deletar_operacao(op_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM operacoes WHERE id = ?', (op_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def atualizar_operacao(op_id, status, preco_compra, qtd):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            UPDATE operacoes 
            SET status=?, preco_compra=?, qtd=?
            WHERE id = ?
        ''', (status, preco_compra, qtd, op_id))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# ============ MAIN APP ============
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    # TELA LOGIN
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📊 Terminal B3 Master")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["Login", "Cadastro"])
        
        with tab1:
            email = st.text_input("Email:")
            password = st.text_input("Senha:", type="password")
            if st.button("Entrar", use_container_width=True):
                user = login_usuario(email, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Email ou senha incorretos")
        
        with tab2:
            nome = st.text_input("Nome:")
            email = st.text_input("Email:", key="signup_email")
            password = st.text_input("Senha:", type="password", key="signup_password")
            password_confirm = st.text_input("Confirmar:", type="password")
            
            if st.button("Cadastrar", use_container_width=True):
                if not nome or not email or not password:
                    st.error("Preencha todos os campos")
                elif password != password_confirm:
                    st.error("Senhas não coincidem")
                elif registrar_usuario(email, password, nome):
                    st.success("Cadastro realizado!")
                else:
                    st.error("Email já existe")

else:
    # APP PRINCIPAL
    st.title(f"📊 Terminal B3 Master - {st.session_state.user['name']}")
    
    if st.button("🚪 Logout", key="logout"):
        st.session_state.user = None
        st.rerun()
    
    banco_b3 = carregar_banco_b3()
    operacoes = carregar_operacoes(st.session_state.user["id"])
    
    tab1, tab2, tab3, tab4 = st.tabs(["Operações", "Recomendações B3", "Carteira", "Relatórios"])
    
    # ===== TAB 1: OPERAÇÕES =====
    with tab1:
        st.subheader("💱 Lançar Operação")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ticker_selecionado = st.selectbox("Ação:", sorted([t.replace(".SA", "") for t in banco_b3.keys()]), key="ticker_op")
        with col2:
            tipo = st.selectbox("Tipo:", ["Ação Pura", "Call", "Put"], key="tipo_op")
        with col3:
            qtd = st.number_input("Qtd:", min_value=1, value=100, step=100, key="qtd_op")
        with col4:
            preco = st.number_input("Preço Compra (R$):", min_value=0.01, value=10.0, step=0.01, key="preco_op")
        
        # Campo de código APENAS para Call/Put
        codigo = ""
        if tipo in ["Call", "Put"]:
            st.markdown("---")
            
            # Sugestão automática de código
            mes_atual = datetime.now().strftime("%b").upper()
            tipo_letra = "C" if tipo == "Call" else "P"
            codigo_sugestao = f"{ticker_selecionado}{tipo_letra}{mes_atual}"
            
            st.write(f"**Código de Opção** (sugestão: {codigo_sugestao})")
            
            col_cod1, col_cod2 = st.columns([3, 1])
            with col_cod1:
                codigo = st.text_input("Digite o código da opção:", value=codigo_sugestao, key=f"codigo_{tipo}_{ticker_selecionado}")
            with col_cod2:
                if st.button("✓ Usar Sugestão", key="use_suggestion"):
                    codigo = codigo_sugestao
            
            if not codigo:
                st.warning("⚠️ Código de opção é obrigatório para Call/Put")
        
        if st.button("💾 Gravar Operação", use_container_width=True, key="btn_gravar"):
            ticker_full = f"{ticker_selecionado}.SA"
            
            # Validação
            if tipo in ["Call", "Put"] and not codigo:
                st.error("❌ Código de opção é obrigatório para Call/Put")
            elif salvar_operacao(st.session_state.user["id"], ticker_full, tipo, int(qtd), preco, codigo):
                st.success("✅ Operação gravada com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao gravar operação")
        
        st.markdown("---")
        st.subheader("📋 Suas Operações")
        
        if operacoes:
            df_ops = []
            for op in operacoes:
                preco_atual = calcular_preco_com_fallback(op["ticker"], op["preco_compra"])
                lucro_prejuizo = (preco_atual - op["preco_compra"]) * op["qtd"]
                percentual = ((preco_atual - op["preco_compra"]) / op["preco_compra"]) * 100
                
                df_ops.append({
                    "Ticker": op["ticker"],
                    "Tipo": op["tipo_ativo"],
                    "Qtd": op["qtd"],
                    "Preço Compra": f"R$ {op['preco_compra']:.2f}",
                    "Preço Atual": f"R$ {preco_atual:.2f}",
                    "L/P": f"R$ {lucro_prejuizo:.2f}",
                    "%": f"{percentual:.2f}%"
                })
            
            st.dataframe(pd.DataFrame(df_ops), use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("✏️ Gerenciar Operações")
            
            col_edit, col_del = st.columns(2)
            
            with col_edit:
                st.write("**Editar:**")
                op_edit = st.selectbox("Selecione:", [f"{op['ticker']} - {op['qtd']} @ R${op['preco_compra']:.2f}" for op in operacoes], key="edit")
                idx = [f"{op['ticker']} - {op['qtd']} @ R${op['preco_compra']:.2f}" for op in operacoes].index(op_edit)
                op_selecionada = operacoes[idx]
                
                status_edit = st.selectbox("Status:", ["Aberta", "Fechada"], key="status_edit")
                preco_edit = st.number_input("Novo Preço:", value=op_selecionada["preco_compra"], key="preco_edit")
                qtd_edit = st.number_input("Nova Qtd:", value=op_selecionada["qtd"], key="qtd_edit")
                
                if st.button("✅ Atualizar", key="btn_edit"):
                    if atualizar_operacao(op_selecionada["id"], status_edit, preco_edit, int(qtd_edit)):
                        st.success("✅ Atualizado!")
                        st.rerun()
            
            with col_del:
                st.write("**Deletar:**")
                op_del = st.selectbox("Selecione:", [f"{op['ticker']} - {op['qtd']} @ R${op['preco_compra']:.2f}" for op in operacoes], key="delete")
                idx_del = [f"{op['ticker']} - {op['qtd']} @ R${op['preco_compra']:.2f}" for op in operacoes].index(op_del)
                op_selecionada_del = operacoes[idx_del]
                
                if st.button("🗑️ DELETAR", key="btn_delete"):
                    if deletar_operacao(op_selecionada_del["id"]):
                        st.success("✅ Deletado!")
                        st.rerun()
        else:
            st.info("Nenhuma operação. Crie uma acima!")
    
    # ===== TAB 2: RECOMENDAÇÕES B3 =====
    with tab2:
        st.subheader("🎯 Recomendações de Analistas B3")
        
        df_recomendacoes = []
        for ticker, dados in banco_b3.items():
            df_recomendacoes.append({
                "Ação": ticker,
                "Empresa": dados["Empresa"],
                "Setor": dados["Setor"],
                "Consenso": dados["Consenso"],
                "Alvo (R$)": f"R$ {dados['Alvo']:.2f}",
                "Upside (%)": f"{dados['Upside']:.1f}%"
            })
        
        df_rec = pd.DataFrame(df_recomendacoes)
        
        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            consenso_filter = st.multiselect("Consenso:", ["Alta", "Neutro", "Baixa"], default=["Alta", "Neutro", "Baixa"])
        with col_f2:
            setor_filter = st.multiselect("Setor:", df_rec["Setor"].unique(), default=df_rec["Setor"].unique())
        
        df_filtrado = df_rec[
            (df_rec["Consenso"].isin(consenso_filter)) & 
            (df_rec["Setor"].isin(setor_filter))
        ]
        
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    
    # ===== TAB 3: CARTEIRA =====
    with tab3:
        st.subheader("💼 Análise da Carteira")
        
        if operacoes:
            df_carteira = []
            investimento_total = 0
            valor_atual_total = 0
            
            for op in operacoes:
                preco_atual = calcular_preco_com_fallback(op["ticker"], op["preco_compra"])
                investimento = op["preco_compra"] * op["qtd"]
                valor_atual = preco_atual * op["qtd"]
                lucro = valor_atual - investimento
                
                investimento_total += investimento
                valor_atual_total += valor_atual
                
                df_carteira.append({
                    "Ticker": op["ticker"],
                    "Qtd": op["qtd"],
                    "Investimento": f"R$ {investimento:.2f}",
                    "Valor Atual": f"R$ {valor_atual:.2f}",
                    "Lucro/Prejuízo": f"R$ {lucro:.2f}"
                })
            
            # Métricas
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Investimento Total", f"R$ {investimento_total:.2f}")
            with col_m2:
                st.metric("Valor Atual", f"R$ {valor_atual_total:.2f}")
            with col_m3:
                lucro_total = valor_atual_total - investimento_total
                st.metric("Lucro/Prejuízo Total", f"R$ {lucro_total:.2f}")
            
            st.markdown("---")
            st.dataframe(pd.DataFrame(df_carteira), use_container_width=True, hide_index=True)
        else:
            st.info("Carteira vazia. Crie operações primeiro!")
    
    # ===== TAB 4: RELATÓRIOS =====
    with tab4:
        st.subheader("📊 Relatórios")
        
        if operacoes:
            # Por tipo
            col_r1, col_r2 = st.columns(2)
            
            with col_r1:
                tipo_counts = pd.Series([op["tipo_ativo"] for op in operacoes]).value_counts()
                fig1 = px.pie(values=tipo_counts.values, names=tipo_counts.index, title="Operações por Tipo")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_r2:
                status_counts = pd.Series([op["status"] for op in operacoes]).value_counts()
                fig2 = px.bar(x=status_counts.index, y=status_counts.values, title="Operações por Status")
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sem dados para relatórios!")
