import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import uuid
from supabase import create_client, Client
import hashlib

# Configurar página
st.set_page_config(
    page_title="Terminal B3 Master - Com Login",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Credenciais Supabase
SUPABASE_URL = "https://vpbwpphdeqpgwazwqzwx.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwYnd3cGhkZXFwZ3dhend6d3giLCJyb2xlIjoiYW5vbiIsImlhdCI6MTcxNzc2NTAyMiwiZXhwIjoyMDMzMzI1MDIyfQ.s_q3hl7K9Dg5Kn2X7L4M8N9O0P1Q2R3S4T5U6V7W8"

# Inicializar Supabase
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

supabase: Client = init_supabase()

# Banco de dados B3
@st.cache_data
def carregar_dados_consenso_b3():
    dados = {
        "VALE3.SA": {"Empresa": "Vale", "Setor": "Mineração", "Consenso_CP": "Alta", "Alvo_CP": 68.0, "Upside_MP": 18.5, "Fundamentos_LP": "Dividend Yield projetado robusto devido à geração de caixa."},
        "PETR4.SA": {"Empresa": "Petrobras", "Setor": "Petróleo e Gás", "Consenso_CP": "Neutro", "Alvo_CP": 41.0, "Upside_MP": 12.0, "Fundamentos_LP": "Geração de caixa forte e foco em refino sustentável."},
        "ITUB4.SA": {"Empresa": "Itaú Unibanco", "Setor": "Financeiro", "Consenso_CP": "Alta", "Alvo_CP": 39.5, "Upside_MP": 15.0, "Fundamentos_LP": "ROE consistente acima de 20% com forte controle de risco."},
        "BBDC4.SA": {"Empresa": "Bradesco", "Setor": "Financeiro", "Consenso_CP": "Neutro", "Alvo_CP": 16.0, "Upside_MP": 22.0, "Fundamentos_LP": "Turnaround operacional focado em eficiência no varejo bancário."},
        "BBAS3.SA": {"Empresa": "Banco do Brasil", "Setor": "Financeiro", "Consenso_CP": "Alta", "Alvo_CP": 33.0, "Upside_MP": 25.0, "Fundamentos_LP": "Valuation muito descontado (P/E baixo) e forte no agronegócio."},
        "WEGE3.SA": {"Empresa": "WEG", "Setor": "Industrial", "Consenso_CP": "Alta", "Alvo_CP": 54.0, "Upside_MP": 10.5, "Fundamentos_LP": "ROIC de 30%+ puxado por forte demanda global em eletrificação."},
        "ELET3.SA": {"Empresa": "Eletrobras", "Setor": "Utilidade Pública", "Consenso_CP": "Alta", "Alvo_CP": 48.0, "Upside_MP": 28.0, "Fundamentos_LP": "Captura de sinergias operacionais e comerciais pós-privatização."},
        "EQTL3.SA": {"Empresa": "Equatorial", "Setor": "Utilidade Pública", "Consenso_CP": "Alta", "Alvo_CP": 36.0, "Upside_MP": 14.0, "Fundamentos_LP": "Excelente histórico de turnaround em ativos de energia distribuída."},
        "RENT3.SA": {"Empresa": "Localiza", "Setor": "Consumo Cíclico", "Consenso_CP": "Neutro", "Alvo_CP": 52.0, "Upside_MP": 19.0, "Fundamentos_LP": "Ganho de escala incomparável na gestão e compra de frotas."},
        "SUZB3.SA": {"Empresa": "Suzano", "Setor": "Materiais Básicos", "Consenso_CP": "Alta", "Alvo_CP": 65.0, "Upside_MP": 16.5, "Fundamentos_LP": "Projeto Cerrado reduzindo sensivelmente o custo caixa global."},
        "BPAC11.SA": {"Empresa": "BTG Pactual", "Setor": "Financeiro", "Consenso_CP": "Alta", "Alvo_CP": 42.0, "Upside_MP": 15.5, "Fundamentos_LP": "Liderança em assessoria e captação líquida no wealth management."},
        "PRIO3.SA": {"Empresa": "PRIO", "Setor": "Petróleo e Gás", "Consenso_CP": "Alta", "Alvo_CP": 56.0, "Upside_MP": 32.0, "Fundamentos_LP": "Aumento expressivo de extração orgânica no campo de Wahoo."},
        "VBBR3.SA": {"Empresa": "Vibra Energia", "Setor": "Petróleo e Gás", "Consenso_CP": "Alta", "Alvo_CP": 28.0, "Upside_MP": 20.0, "Fundamentos_LP": "Expansão de margens de distribuição de combustíveis nas redes de postos."},
        "LREN3.SA": {"Empresa": "Lojas Renner", "Setor": "Consumo Cíclico", "Consenso_CP": "Alta", "Alvo_CP": 22.0, "Upside_MP": 23.0, "Fundamentos_LP": "Recuperação no varejo de moda e melhora nas provisões da Realize."},
        "EMBR3.SA": {"Empresa": "Embraer", "Setor": "Industrial", "Consenso_CP": "Alta", "Alvo_CP": 40.0, "Upside_MP": 31.0, "Fundamentos_LP": "Forte carteira de pedidos comerciais e contratos em defesa aérea."},
        "AZUL4.SA": {"Empresa": "Azul", "Setor": "Transporte", "Consenso_CP": "Neutro", "Alvo_CP": 12.0, "Upside_MP": 40.0, "Fundamentos_LP": "Geração operacional saudável, dependendo de acordos com arrendadores."},
        "BEEF3.SA": {"Empresa": "Minerva", "Setor": "Alimentos", "Consenso_CP": "Neutro", "Alvo_CP": 8.0, "Upside_MP": 26.0, "Fundamentos_LP": "Alavancagem temporária após compra de plantas da Marfrig na AL."},
        "MGLU3.SA": {"Empresa": "Magazine Luiza", "Setor": "Consumo Cíclico", "Consenso_CP": "Baixa", "Alvo_CP": 14.0, "Upside_MP": 15.0, "Fundamentos_LP": "Reestruturação de canais físicos e foco em serviços de marketplace."},
        "BHIA3.SA": {"Empresa": "Casas Bahia", "Setor": "Consumo Cíclico", "Consenso_CP": "Baixa", "Alvo_CP": 6.0, "Upside_MP": 12.0, "Fundamentos_LP": "Foco severo em queima de estoques e redução de despesas fixas."},
        "CVCB3.SA": {"Empresa": "CVC Brasil", "Setor": "Consumo Cíclico", "Consenso_CP": "Neutro", "Alvo_CP": 3.2, "Upside_MP": 35.0, "Fundamentos_LP": "Retorno expressivo das franquias físicas de viagens e melhora no take-rate."},
        "YDUQ3.SA": {"Empresa": "Yduqs", "Setor": "Educação", "Consenso_CP": "Neutro", "Alvo_CP": 16.0, "Upside_MP": 25.0, "Fundamentos_LP": "Resiliência e avanço expressivo na captação do segmento de Medicina."},
        "COGN3.SA": {"Empresa": "Cogna", "Setor": "Educação", "Consenso_CP": "Neutro", "Alvo_CP": 2.8, "Upside_MP": 22.0, "Fundamentos_LP": "Melhora no fluxo de caixa livre operacional e renegociação da Kroton."},
        "RADL3.SA": {"Empresa": "Raia Drogasil", "Setor": "Saúde", "Consenso_CP": "Neutro", "Alvo_CP": 30.0, "Upside_MP": 8.0, "Fundamentos_LP": "Liderança consolidada com forte capilaridade e modelo digital maduro."},
        "GGBR4.SA": {"Empresa": "Gerdau", "Setor": "Mineração/Siderurgia", "Consenso_CP": "Neutro", "Alvo_CP": 21.0, "Upside_MP": 14.0, "Fundamentos_LP": "Forte exposição ao mercado imobiliário e industrial dos EUA."},
        "CMIG4.SA": {"Empresa": "Cemig", "Setor": "Utilidade Pública", "Consenso_CP": "Neutro", "Alvo_CP": 13.0, "Upside_MP": 11.0, "Fundamentos_LP": "Plano eficiente focado em desinvestimentos de participações."},
        "SBSP3.SA": {"Empresa": "Sabesp", "Setor": "Utilidade Pública", "Consenso_CP": "Alta", "Alvo_CP": 110.0, "Upside_MP": 24.0, "Fundamentos_LP": "Ganhos severos de eficiência privada pós-desestatização."},
        "SANB11.SA": {"Empresa": "Santander BR", "Setor": "Financeiro", "Consenso_CP": "Baixa", "Alvo_CP": 26.0, "Upside_MP": 2.0, "Fundamentos_LP": "Margens financeiras sob pressão temporária devido ao mix de varejo."},
        "CPLE6.SA": {"Empresa": "Copel", "Setor": "Utilidade Pública", "Consenso_CP": "Alta", "Alvo_CP": 11.5, "Upside_MP": 15.0, "Fundamentos_LP": "Corte agressivo de despesas pós-transformação em corporação."},
        "VIVT3.SA": {"Empresa": "Telefonica BR", "Setor": "Telecom", "Consenso_CP": "Alta", "Alvo_CP": 57.0, "Upside_MP": 12.0, "Fundamentos_LP": "Geração previsível de caixa livre com payout historicamente alto."},
        "ABEV3.SA": {"Empresa": "Ambev", "Setor": "Consumo não Cíclico", "Consenso_CP": "Neutro", "Alvo_CP": 14.5, "Upside_MP": 11.0, "Fundamentos_LP": "Forte geração de caixa livre, mas enfrenta competição regional dura."},
        "BBSE3.SA": {"Empresa": "BB Seguridade", "Setor": "Seguros", "Consenso_CP": "Alta", "Alvo_CP": 38.0, "Upside_MP": 14.0, "Fundamentos_LP": "Retorno sobre capital elevado impulsionado pelo braço do agronegócio."},
        "CXSE3.SA": {"Empresa": "Caixa Seguridade", "Setor": "Seguros", "Consenso_CP": "Alta", "Alvo_CP": 17.0, "Upside_MP": 15.0, "Fundamentos_LP": "Crescimento contínuo de prêmios emitidos no balcão de habitação."},
        "EGIE3.SA": {"Empresa": "Engie Brasil", "Setor": "Utilidade Pública", "Consenso_CP": "Alta", "Alvo_CP": 46.0, "Upside_MP": 10.0, "Fundamentos_LP": "Portfólio resiliente em contratos de longo prazo com proteção inflacionária."},
        "CCRO3.SA": {"Empresa": "CCR", "Setor": "Infraestrutura", "Consenso_CP": "Alta", "Alvo_CP": 15.0, "Upside_MP": 18.0, "Fundamentos_LP": "Previsibilidade severa em concessões de rodovias e aeroportos contratados."},
        "RAIZ4.SA": {"Empresa": "Raízen", "Setor": "Petróleo/Etanol", "Consenso_CP": "Neutro", "Alvo_CP": 4.2, "Upside_MP": 25.0, "Fundamentos_LP": "Tese concentrada na maturação de usinas de etanol de segunda geração."},
        "CSAN3.SA": {"Empresa": "Cosan", "Setor": "Holding/Energia", "Consenso_CP": "Alta", "Alvo_CP": 21.0, "Upside_MP": 26.5, "Fundamentos_LP": "Desbloqueio estrutural de valor de suas controladas de peso."},
        "CSNA3.SA": {"Empresa": "Siderúrgica Nacional", "Setor": "Mineração/Siderurgia", "Consenso_CP": "Neutro", "Alvo_CP": 15.5, "Upside_MP": 12.0, "Fundamentos_LP": "Alavancagem financeira requer monitoramento de curto prazo."},
        "USIM5.SA": {"Empresa": "Usiminas", "Setor": "Mineração/Siderurgia", "Consenso_CP": "Neutro", "Alvo_CP": 8.5, "Upside_MP": 14.0, "Fundamentos_LP": "Estabilização da planta após reforma estrutural do Alto-Forno 3."},
        "MRVE3.SA": {"Empresa": "MRV Engenharia", "Setor": "Construção Civil", "Consenso_CP": "Alta", "Alvo_CP": 11.0, "Upside_MP": 35.0, "Fundamentos_LP": "Aumento no ticket médio do programa Minha Casa Minha Vida impulsiona margens."},
        "CYRE3.SA": {"Empresa": "Cyrela", "Setor": "Construção Civil", "Consenso_CP": "Alta", "Alvo_CP": 26.0, "Upside_MP": 18.0, "Fundamentos_LP": "Liderança focada em alta renda com forte velocidade de vendas."},
        "TAEE11.SA": {"Empresa": "Taesa", "Setor": "Utilidade Pública", "Consenso_CP": "Neutro", "Alvo_CP": 36.0, "Upside_MP": 5.0, "Fundamentos_LP": "Receitas previsíveis indexadas por IGP-M e IPCA em linhas maduras."},
        "TRPL4.SA": {"Empresa": "ISA CTEEP", "Setor": "Utilidade Pública", "Consenso_CP": "Alta", "Alvo_CP": 29.0, "Upside_MP": 11.0, "Fundamentos_LP": "Forte fluxo de novas subestações entrando em RAP operacionais."},
        "MULT3.SA": {"Empresa": "Multiplan", "Setor": "Shopping Centers", "Consenso_CP": "Alta", "Alvo_CP": 31.0, "Upside_MP": 14.5, "Fundamentos_LP": "Ativos localizados em pontos premium com alto poder aquisitivo dos clientes."},
        "TIMS3.SA": {"Empresa": "TIM Brasil", "Setor": "Telecom", "Consenso_CP": "Alta", "Alvo_CP": 21.0, "Upside_MP": 13.0, "Fundamentos_LP": "Ganhos em eficiência e migração pós-consolidação de infraestrutura de rede."},
        "TOTV3.SA": {"Empresa": "Totvs", "Setor": "Tecnologia", "Consenso_CP": "Alta", "Alvo_CP": 38.0, "Upside_MP": 17.5, "Fundamentos_LP": "Dominância absoluta em ERP corporativo com altíssima taxa de retenção."},
        "BRFS3.SA": {"Empresa": "BRF", "Setor": "Alimentos", "Consenso_CP": "Alta", "Alvo_CP": 26.0, "Upside_MP": 15.0, "Fundamentos_LP": "Desalavancagem muito veloz e queda acentuada nos custos de insumos de grãos."},
        "JBSS3.SA": {"Empresa": "JBS", "Setor": "Alimentos", "Consenso_CP": "Alta", "Alvo_CP": 36.0, "Upside_MP": 22.0, "Fundamentos_LP": "Presença geográfica robusta em múltiplos continentes reduz riscos cíclicos."},
        "STBP3.SA": {"Empresa": "Santos Brasil", "Setor": "Logística", "Consenso_CP": "Alta", "Alvo_CP": 16.0, "Upside_MP": 12.0, "Fundamentos_LP": "Operação portuária resiliente e contratos de tarifas portuárias consolidados."},
        "RAIL3.SA": {"Empresa": "Rumo", "Setor": "Logística", "Consenso_CP": "Alta", "Alvo_CP": 27.0, "Upside_MP": 19.0, "Fundamentos_LP": "Expansão da malha logística do Centro-Oeste garante escoamento futuro de safras."},
        "FLRY3.SA": {"Empresa": "Fleury", "Setor": "Saúde", "Consenso_CP": "Alta", "Alvo_CP": 19.5, "Upside_MP": 15.0, "Fundamentos_LP": "Captura rápida de sinergias da fusão com o grupo Pardini."},
        "ALUP11.SA": {"Empresa": "Alupar", "Setor": "Utilidade Pública", "Consenso_CP": "Alta", "Alvo_CP": 33.0, "Upside_MP": 12.0, "Fundamentos_LP": "Contratos regulados longos protegidos do risco de volume."},
        "CPFE3.SA": {"Empresa": "CPFL Energia", "Setor": "Utilidade Pública", "Consenso_CP": "Alta", "Alvo_CP": 39.0, "Upside_MP": 11.0, "Fundamentos_LP": "Excelente histórico operacional com faturamento estável em distribuição."}
    }
    return dados

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registrar_usuario(email, password, name):
    try:
        hashed_pwd = hash_password(password)
        response = supabase.table("auth.users").insert({
            "email": email,
            "password_hash": hashed_pwd,
            "name": name
        }).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao registrar: {str(e)}")
        return False

def login_usuario(email, password):
    try:
        hashed_pwd = hash_password(password)
        response = supabase.table("auth.users").select("*").eq("email", email).eq("password_hash", hashed_pwd).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Erro ao fazer login: {str(e)}")
        return None

def salvar_operacao(user_id, ticker, tipo_ativo, qtd, preco_compra, preco_venda, codigo_opcao):
    try:
        supabase.table("operacoes").insert({
            "user_id": user_id,
            "ticker": ticker,
            "tipo_ativo": tipo_ativo,
            "qtd": qtd,
            "preco_compra": preco_compra,
            "preco_venda": preco_venda if preco_venda > 0 else None,
            "codigo_opcao": codigo_opcao if codigo_opcao else None,
            "status": "Em Andamento"
        }).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {str(e)}")
        return False

def carregar_operacoes(user_id):
    try:
        response = supabase.table("operacoes").select("*").eq("user_id", user_id).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Erro ao carregar operações: {str(e)}")
        return []

# --- FLUXO PRINCIPAL ---

if "user" not in st.session_state:
    st.session_state.user = None

# Se não está autenticado
if st.session_state.user is None:
    st.title("🔐 Terminal B3 Master - Login")
    
    tab1, tab2 = st.tabs(["Login", "Cadastro"])
    
    with tab1:
        st.subheader("Faça Login")
        email = st.text_input("Email:", key="login_email")
        password = st.text_input("Senha:", type="password", key="login_password")
        
        if st.button("Entrar", key="btn_login"):
            user = login_usuario(email, password)
            if user:
                st.session_state.user = user
                st.success("✅ Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Email ou senha incorretos")
    
    with tab2:
        st.subheader("Criar Conta")
        nome = st.text_input("Seu Nome:", key="signup_name")
        email = st.text_input("Email:", key="signup_email")
        password = st.text_input("Senha:", type="password", key="signup_password")
        password_confirm = st.text_input("Confirmar Senha:", type="password", key="signup_password_confirm")
        
        if st.button("Cadastrar", key="btn_signup"):
            if password != password_confirm:
                st.error("❌ As senhas não coincidem")
            elif len(password) < 6:
                st.error("❌ A senha deve ter pelo menos 6 caracteres")
            elif registrar_usuario(email, password, nome):
                st.success("✅ Cadastro realizado! Faça login para continuar")
            else:
                st.error("❌ Erro ao cadastrar. Email pode já estar em uso.")

# Se está autenticado
else:
    st.title("📊 Terminal Quant Completo B3 - Master Edition v4")
    st.markdown(f"**Bem-vindo, {st.session_state.user['name']}!**")
    
    # Botão logout
    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.rerun()
    
    # Resto da aplicação...
    banco_b3 = carregar_dados_consenso_b3()
    lista_tickers = list(banco_b3.keys())
    
    st.markdown("---")
    st.write("### 💱 Painel de Lançamento de Operações")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        tickers_boleta = sorted([t.replace(".SA", "") for t in lista_tickers])
        acao_operar = st.selectbox("Selecione a Ação Base:", tickers_boleta, key="acao_base")
    
    with col2:
        tipo_ativo = st.selectbox("Tipo de Ativo:", ["Ação Pura", "Call (Comprador)", "Put (Comprador)"], key="tipo_ativo")
    
    with col3:
        qtd_op = st.number_input("Quantidade:", min_value=0, value=100, step=100, key="qtd_op")
    
    with col4:
        preco_compra_op = st.number_input("Preço/Prêmio (R$):", min_value=0.0, value=10.0, step=0.01, key="preco_compra")
    
    with col5:
        preco_venda_op = st.number_input("Preço Venda (R$, 0 = aberto):", min_value=0.0, value=0.0, step=0.01, key="preco_venda")
    
    st.markdown("---")
    codigo_opcao = st.text_input("Código da Opção (opcional):", placeholder="Ex: VALEJ120", key="codigo_opcao")
    
    if st.button("💾 Gravar Operação"):
        if qtd_op > 0:
            ticker_chave = f"{acao_operar}.SA"
            if salvar_operacao(
                st.session_state.user["id"],
                ticker_chave,
                tipo_ativo,
                qtd_op,
                preco_compra_op,
                preco_venda_op,
                codigo_opcao
            ):
                st.success("✅ Operação gravada com sucesso!")
                st.rerun()
        else:
            st.error("❌ Quantidade deve ser > 0")
    
    st.markdown("---")
    st.write("### 📈 Suas Operações")
    
    operacoes = carregar_operacoes(st.session_state.user["id"])
    
    if operacoes:
        df_ops = pd.DataFrame(operacoes)
        st.dataframe(df_ops, use_container_width=True, hide_index=True)
        
        # Calcular lucro total
        lucro_total = 0
        for op in operacoes:
            if op["preco_venda"] is not None and op["preco_venda"] > 0:
                lucro = (op["preco_venda"] - op["preco_compra"]) * op["qtd"]
                lucro_total += lucro
        
        st.metric("Lucro/Prejuízo Total (R$)", f"R$ {lucro_total:.2f}")
    else:
        st.info("Nenhuma operação registrada ainda.")