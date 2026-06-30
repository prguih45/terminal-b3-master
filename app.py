import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import hashlib
import uuid
import json
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO

# ============ CONFIG ============
st.set_page_config(
    page_title="Terminal B3 Master",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Personalizado
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .success-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
    }
    .danger-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 15px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============ DATABASE ============
DB_PATH = "terminal_b3.db"

def init_db():
    """Inicializa banco SQLite com persistência"""
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
            preco_venda REAL,
            codigo_opcao TEXT,
            status TEXT DEFAULT 'Em Andamento',
            data_operacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES usuarios(id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# ============ FUNÇÕES ============
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
    except Exception as e:
        st.error(f"Erro: {str(e)}")
        return False

def login_usuario(email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        hashed_pwd = hash_password(password)
        
        c.execute('''
            SELECT id, email, name, created_at FROM usuarios
            WHERE email = ? AND password_hash = ?
        ''', (email, hashed_pwd))
        
        user = c.fetchone()
        conn.close()
        
        if user:
            return {"id": user[0], "email": user[1], "name": user[2], "created_at": user[3]}
        return None
    except Exception as e:
        st.error(f"Erro: {str(e)}")
        return None

def salvar_operacao(user_id, ticker, tipo_ativo, qtd, preco_compra, preco_venda, codigo_opcao):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        op_id = str(uuid.uuid4())
        
        c.execute('''
            INSERT INTO operacoes (id, user_id, ticker, tipo_ativo, qtd, preco_compra, preco_venda, codigo_opcao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (op_id, user_id, ticker, tipo_ativo, qtd, preco_compra, 
              preco_venda if preco_venda > 0 else None, codigo_opcao if codigo_opcao else None))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro: {str(e)}")
        return False

def carregar_operacoes(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, user_id, ticker, tipo_ativo, qtd, preco_compra, preco_venda, codigo_opcao, status, data_operacao
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
                "user_id": row[1],
                "ticker": row[2],
                "tipo_ativo": row[3],
                "qtd": row[4],
                "preco_compra": row[5],
                "preco_venda": row[6],
                "codigo_opcao": row[7],
                "status": row[8],
                "data_operacao": row[9]
            })
        
        return operacoes
    except Exception as e:
        st.error(f"Erro: {str(e)}")
        return []

def deletar_operacao(op_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM operacoes WHERE id = ?', (op_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro: {str(e)}")
        return False

def atualizar_operacao(op_id, tipo_ativo, qtd, preco_compra, preco_venda, codigo_opcao, status):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            UPDATE operacoes 
            SET tipo_ativo=?, qtd=?, preco_compra=?, preco_venda=?, codigo_opcao=?, status=?
            WHERE id = ?
        ''', (tipo_ativo, qtd, preco_compra, preco_venda if preco_venda > 0 else None, codigo_opcao, status, op_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro: {str(e)}")
        return False

# ============ DADOS B3 ============
@st.cache_data
def carregar_dados_b3():
    return {
        "VALE3.SA": {"Empresa": "Vale", "Setor": "Mineração"},
        "PETR4.SA": {"Empresa": "Petrobras", "Setor": "Petróleo e Gás"},
        "ITUB4.SA": {"Empresa": "Itaú Unibanco", "Setor": "Financeiro"},
        "BBDC4.SA": {"Empresa": "Bradesco", "Setor": "Financeiro"},
        "BBAS3.SA": {"Empresa": "Banco do Brasil", "Setor": "Financeiro"},
        "WEGE3.SA": {"Empresa": "WEG", "Setor": "Industrial"},
        "ELET3.SA": {"Empresa": "Eletrobras", "Setor": "Utilidade Pública"},
        "EQTL3.SA": {"Empresa": "Equatorial", "Setor": "Utilidade Pública"},
        "RENT3.SA": {"Empresa": "Localiza", "Setor": "Consumo Cíclico"},
        "SUZB3.SA": {"Empresa": "Suzano", "Setor": "Materiais Básicos"},
        "PRIO3.SA": {"Empresa": "PRIO", "Setor": "Petróleo e Gás"},
        "BRFS3.SA": {"Empresa": "BRF", "Setor": "Alimentos"},
        "JBSS3.SA": {"Empresa": "JBS", "Setor": "Alimentos"},
        "RAIL3.SA": {"Empresa": "Rumo", "Setor": "Logística"},
        "TOTV3.SA": {"Empresa": "Totvs", "Setor": "Tecnologia"},
        "TRPL4.SA": {"Empresa": "ISA CTEEP", "Setor": "Utilidade Pública"},
        "CCRO3.SA": {"Empresa": "CCR", "Setor": "Infraestrutura"},
    }

# ============ MAIN APP ============
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    # TELA DE LOGIN
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 📊 Terminal B3 Master")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Cadastro"])
        
        with tab1:
            st.subheader("Faça Login")
            email = st.text_input("📧 Email:", key="login_email")
            password = st.text_input("🔒 Senha:", type="password", key="login_password")
            
            if st.button("✅ Entrar", use_container_width=True, type="primary"):
                if email and password:
                    user = login_usuario(email, password)
                    if user:
                        st.session_state.user = user
                        st.success("✅ Login realizado!")
                        st.rerun()
                    else:
                        st.error("❌ Email ou senha incorretos")
                else:
                    st.error("❌ Preencha todos os campos")
        
        with tab2:
            st.subheader("Criar Conta")
            nome = st.text_input("👤 Seu Nome:", key="signup_name")
            email = st.text_input("📧 Email:", key="signup_email")
            password = st.text_input("🔒 Senha:", type="password", key="signup_password")
            password_confirm = st.text_input("🔒 Confirmar:", type="password", key="signup_password_confirm")
            
            if st.button("✅ Cadastrar", use_container_width=True, type="primary"):
                if not nome or not email or not password:
                    st.error("❌ Preencha todos os campos")
                elif password != password_confirm:
                    st.error("❌ Senhas não coincidem")
                elif len(password) < 6:
                    st.error("❌ Senha deve ter 6+ caracteres")
                elif registrar_usuario(email, password, nome):
                    st.success("✅ Cadastro realizado! Faça login")
                else:
                    st.error("❌ Email já existe")

else:
    # APP PRINCIPAL
    st.markdown(f"# 📊 Terminal B3 Master")
    st.markdown(f"**Bem-vindo, {st.session_state.user['name']}!**")
    
    col1, col2 = st.columns([10, 2])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    
    banco_b3 = carregar_dados_b3()
    lista_tickers = list(banco_b3.keys())
    operacoes = carregar_operacoes(st.session_state.user["id"])
    
    # ===== TABS PRINCIPAIS =====
    tab1, tab2, tab3 = st.tabs(["📝 Operações", "📊 Relatórios", "📈 Análise"])
    
    # ===== TAB 1: OPERAÇÕES =====
    with tab1:
        st.markdown("## 💱 Lançar Nova Operação")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            acao = st.selectbox("Ação:", sorted([t.replace(".SA", "") for t in lista_tickers]), key="acao")
        with col2:
            tipo = st.selectbox("Tipo:", ["Ação Pura", "Call", "Put"], key="tipo")
        with col3:
            qtd = st.number_input("Qtd:", min_value=1, value=100, step=100, key="qtd")
        with col4:
            pc = st.number_input("Preço Compra:", min_value=0.01, value=10.0, step=0.01, key="pc")
        with col5:
            pv = st.number_input("Preço Venda:", min_value=0.0, value=0.0, step=0.01, key="pv")
        
        col6, col7 = st.columns([3, 2])
        with col6:
            cod = st.text_input("Código Opção (opcional):", key="cod")
        with col7:
            st.write("")
            if st.button("💾 Gravar", use_container_width=True, type="primary"):
                if salvar_operacao(st.session_state.user["id"], f"{acao}.SA", tipo, int(qtd), pc, pv, cod):
                    st.success("✅ Operação gravada!")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("## 📋 Suas Operações")
        
        if operacoes:
            # Criar DataFrame
            df = pd.DataFrame(operacoes)
            df["Resultado"] = df.apply(
                lambda row: f"R$ {(row['preco_venda'] - row['preco_compra']) * row['qtd']:.2f}" 
                if row['preco_venda'] else "Aberto",
                axis=1
            )
            
            # Exibir tabela estilizada
            st.dataframe(
                df[["ticker", "tipo_ativo", "qtd", "preco_compra", "preco_venda", "Resultado", "status", "data_operacao"]],
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("---")
            st.markdown("## ✏️ Editar / Deletar Operações")
            
            col_op1, col_op2 = st.columns([1, 1])
            
            with col_op1:
                op_selecionada = st.selectbox(
                    "Selecione operação:",
                    [f"{op['ticker']} - {op['qtd']} @ R${op['preco_compra']:.2f}" for op in operacoes],
                    key="op_select"
                )
                idx_selecionado = [f"{op['ticker']} - {op['qtd']} @ R${op['preco_compra']:.2f}" for op in operacoes].index(op_selecionada)
                op_edit = operacoes[idx_selecionado]
                
                st.markdown("### Editar Operação")
                
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    tipo_e = st.selectbox("Tipo:", ["Ação Pura", "Call", "Put"], 
                                          index=["Ação Pura", "Call", "Put"].index(op_edit['tipo_ativo']),
                                          key="tipo_e")
                    qtd_e = st.number_input("Qtd:", value=op_edit['qtd'], key="qtd_e")
                    pc_e = st.number_input("Preço Compra:", value=op_edit['preco_compra'], step=0.01, key="pc_e")
                
                with col_e2:
                    pv_e = st.number_input("Preço Venda:", value=op_edit['preco_venda'] or 0.0, step=0.01, key="pv_e")
                    cod_e = st.text_input("Código Opção:", value=op_edit['codigo_opcao'] or "", key="cod_e")
                    status_e = st.selectbox("Status:", ["Em Andamento", "Fechada", "Cancelada"],
                                            index=["Em Andamento", "Fechada", "Cancelada"].index(op_edit['status']),
                                            key="status_e")
                
                if st.button("✅ Atualizar", use_container_width=True, type="primary", key="btn_update"):
                    if atualizar_operacao(op_edit['id'], tipo_e, int(qtd_e), pc_e, pv_e, cod_e, status_e):
                        st.success("✅ Operação atualizada!")
                        st.rerun()
            
            with col_op2:
                st.markdown("### Deletar Operação")
                op_deletar = st.selectbox(
                    "Selecione para deletar:",
                    [f"{op['ticker']} - {op['qtd']} @ R${op['preco_compra']:.2f}" for op in operacoes],
                    key="op_delete"
                )
                idx_delete = [f"{op['ticker']} - {op['qtd']} @ R${op['preco_compra']:.2f}" for op in operacoes].index(op_deletar)
                op_del = operacoes[idx_delete]
                
                st.warning(f"⚠️ Você vai deletar: {op_del['ticker']} - {op_del['qtd']} unidades")
                
                if st.button("🗑️ DELETAR OPERAÇÃO", use_container_width=True, type="secondary", key="btn_delete"):
                    if deletar_operacao(op_del['id']):
                        st.success("✅ Operação deletada!")
                        st.rerun()
        else:
            st.info("Nenhuma operação registrada ainda.")
    
    # ===== TAB 2: RELATÓRIOS =====
    with tab2:
        st.markdown("## 📊 Relatórios e Análises")
        
        if operacoes:
            df = pd.DataFrame(operacoes)
            
            # Métricas principais
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            total_ops = len(df)
            ops_abertas = len(df[df['status'] == 'Em Andamento'])
            ops_fechadas = len(df[df['status'] == 'Fechada'])
            
            with col_m1:
                st.metric("📌 Total de Operações", total_ops)
            with col_m2:
                st.metric("🔄 Abertas", ops_abertas)
            with col_m3:
                st.metric("✅ Fechadas", ops_fechadas)
            
            # Lucro/Prejuízo
            df['lucro'] = df.apply(
                lambda row: (row['preco_venda'] - row['preco_compra']) * row['qtd'] 
                if row['preco_venda'] else 0,
                axis=1
            )
            
            lucro_total = df['lucro'].sum()
            with col_m4:
                if lucro_total >= 0:
                    st.metric("💰 Lucro/Prejuízo Total", f"R$ {lucro_total:.2f}", delta=f"+{lucro_total:.2f}")
                else:
                    st.metric("💰 Lucro/Prejuízo Total", f"R$ {lucro_total:.2f}", delta=f"{lucro_total:.2f}")
            
            st.markdown("---")
            
            # Gráficos
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.markdown("### Operações por Tipo")
                tipo_counts = df['tipo_ativo'].value_counts()
                fig_tipo = px.pie(
                    values=tipo_counts.values,
                    names=tipo_counts.index,
                    color_discrete_sequence=["#667eea", "#764ba2", "#f093fb"]
                )
                st.plotly_chart(fig_tipo, use_container_width=True)
            
            with col_g2:
                st.markdown("### Status das Operações")
                status_counts = df['status'].value_counts()
                fig_status = px.bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    color_discrete_sequence=["#667eea"]
                )
                st.plotly_chart(fig_status, use_container_width=True)
            
            # Lucro por ticker
            st.markdown("### Lucro/Prejuízo por Ação")
            lucro_ticker = df.groupby('ticker')['lucro'].sum().sort_values(ascending=False)
            
            fig_lucro = go.Figure()
            colors = ['#f093fb' if x >= 0 else '#fa709a' for x in lucro_ticker.values]
            fig_lucro.add_trace(go.Bar(
                x=lucro_ticker.index,
                y=lucro_ticker.values,
                marker=dict(color=colors)
            ))
            fig_lucro.update_layout(
                title="Resultado por Ticker",
                xaxis_title="Ticker",
                yaxis_title="Lucro/Prejuízo (R$)",
                height=400
            )
            st.plotly_chart(fig_lucro, use_container_width=True)
            
            # Tabela resumida
            st.markdown("### Resumo por Ticker")
            resumo = df.groupby('ticker').agg({
                'qtd': 'sum',
                'lucro': 'sum'
            }).round(2)
            resumo.columns = ['Total de Ações', 'Lucro/Prejuízo']
            st.dataframe(resumo, use_container_width=True)
        
        else:
            st.info("Sem dados para gerar relatórios. Crie operações primeiro!")
    
    # ===== TAB 3: ANÁLISE =====
    with tab3:
        st.markdown("## 📈 Análise Detalhada")
        
        if operacoes:
            df = pd.DataFrame(operacoes)
            
            # Seletor de ticker
            ticker_selecionado = st.selectbox("Selecione um ticker:", sorted(df['ticker'].unique()))
            df_ticker = df[df['ticker'] == ticker_selecionado]
            
            col_a1, col_a2, col_a3 = st.columns(3)
            
            with col_a1:
                st.metric("Total de Operações", len(df_ticker))
            with col_a2:
                qtd_total = df_ticker['qtd'].sum()
                st.metric("Total de Ações", qtd_total)
            with col_a3:
                preco_medio = (df_ticker['preco_compra'] * df_ticker['qtd']).sum() / qtd_total if qtd_total > 0 else 0
                st.metric("Preço Médio", f"R$ {preco_medio:.2f}")
            
            st.markdown("---")
            st.markdown("### Histórico de Operações")
            st.dataframe(df_ticker[['tipo_ativo', 'qtd', 'preco_compra', 'preco_venda', 'status', 'data_operacao']], 
                        use_container_width=True, hide_index=True)
        
        else:
            st.info("Sem dados para análise. Crie operações primeiro!")
