import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import uuid

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Quant Aggregator B3 - Master Terminal v4",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BANCO DE DADOS COMPLETO E EXPANDIDO B3 (MÍNIMO 48 ATIVOS SELECIONADOS) ---
@st.cache_data
def carregar_dados_consenso_b3():
    dados = {
        # --- BLUE CHIPS & MAIS INDICADAS ---
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

def calcular_terceira_sexta(ano, mes):
    primeiro_dia = datetime(ano, mes, 1)
    dia_semana_1 = primeiro_dia.weekday()
    dias_ate_sexta = (4 - dia_semana_1) % 7
    return primeiro_dia + timedelta(days=dias_ate_sexta) + timedelta(weeks=2)

def calcular_opcao_b3_dinamica(ticker, preco_acao, tipo_opcao="Call"):
    hoje = datetime.now()
    ano_alvo, mes_alvo = hoje.year, hoje.month
    vencimento_atual = calcular_terceira_sexta(ano_alvo, mes_alvo)
    
    if hoje.date() >= (vencimento_atual.date() - timedelta(days=4)):
        if mes_alvo == 12:
            mes_alvo, ano_alvo = 1, ano_alvo + 1
        else:
            mes_alvo += 1
        vencimento_final = calcular_terceira_sexta(ano_alvo, mes_alvo)
    else:
        vencimento_final = vencimento_atual
        
    vencimento_str = vencimento_final.strftime("%d/%m/%Y")
    
    if tipo_opcao == "Call":
        letras_call = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
        letra_mes = letras_call[mes_alvo - 1]
        strike_alvo = round(preco_acao * 1.10, 2)
    else:
        letras_put = ["M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X"]
        letra_mes = letras_put[mes_alvo - 1]
        strike_alvo = round(preco_acao * 0.90, 2)
    
    codigo_base = ticker.replace(".SA", "")
    letras_ticker = ''.join([char for char in codigo_base if not char.isdigit()])
    ticker_opcao = f"{letras_ticker}{letra_mes}{int(strike_alvo)}"
    
    premio_estimado = round(preco_acao * 0.012, 2)
    if premio_estimado < 0.01: 
        premio_estimado = 0.05
    
    return {
        "Opcao_Ticker": ticker_opcao, 
        "Vencimento_B3": vencimento_str, 
        "Strike_Alvo": strike_alvo, 
        "Premio_Est": premio_estimado,
        "Mes_Referencia": vencimento_final.strftime('%B / %Y').capitalize(),
        "Tipo_Opcao": tipo_opcao
    }

def processar_mercado_b3(tickers):
    dados_finais = {}
    fim = datetime.now()
    inicio = fim - timedelta(days=90)
    
    for ticker in tickers:
        try:
            asset = yf.Ticker(ticker)
            hist = asset.history(start=inicio, end=fim)
            if len(hist) < 2: continue
            preco_anterior = float(hist['Close'].iloc[-1])
            fundo = float(hist['Low'].min())
            topo = float(hist['High'].max())
            
            hist['SMA20'] = hist['Close'].rolling(window=20).mean()
            entrada = float(hist['SMA20'].iloc[-1]) if not np.isnan(hist['SMA20'].iloc[-1]) else preco_anterior * 0.98
            
            retornos = hist['Close'].pct_change()
            vol = retornos.std() if not np.isnan(retornos.std()) else 0.02
            stop = preco_anterior * (1 - (2 * vol))
            alvo_saida = preco_anterior * (1 + (3 * vol))
            
            dados_opcoes_call = calcular_opcao_b3_dinamica(ticker, preco_anterior, tipo_opcao="Call")
            dados_opcoes_put = calcular_opcao_b3_dinamica(ticker, preco_anterior, tipo_opcao="Put")
            
            dados_finais[ticker] = {
                "Preco_Anterior": round(preco_anterior, 2), 
                "Fundo": round(fundo, 2), 
                "Topo": round(topo, 2),
                "Entrada": round(entrada, 2), 
                "Alvo_Saida": round(alvo_saida, 2), 
                "Stop": round(stop, 2), 
                "Call": dados_opcoes_call,
                "Put": dados_opcoes_put
            }
        except Exception as e:
            continue
    return dados_finais

if "carteira_operacoes" not in st.session_state:
    st.session_state.carteira_operacoes = {}

banco_b3 = carregar_dados_consenso_b3()
lista_tickers = list(banco_b3.keys())

with st.spinner("Atualizando base quantitativa completa da B3..."):
    dados_mercado = processar_mercado_b3(lista_tickers)

st.title("📊 Terminal Quant Completo B3 - Master Edition v4")
st.markdown("**Agora com suporte para CALLs, PUTs e múltiplas operações por ativo!**")
st.markdown("---")

st.sidebar.header("Filtros Universais")
modo_exibicao = st.sidebar.radio("Modo de Visualização:", ["Todas as Ações Indicadas", "Apenas Minha Carteira"])

setores = sorted(list(set([info["Setor"] for info in banco_b3.values()])))
setores_sel = st.sidebar.multiselect("Filtrar por Setor:", setores, default=setores)

vieses = ["Alta", "Neutro", "Baixa"]
vies_sel = st.sidebar.multiselect("Filtrar por Viés:", vieses, default=vieses)

if st.sidebar.button("🔄 Forçar Recálculo Geral"):
    st.cache_data.clear()

st.write("### 💱 Painel de Lançamento de Operações (Ações e Derivativos)")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    tickers_boleta = sorted([t.replace(".SA", "") for t in lista_tickers])
    acao_operar = st.selectbox("Selecione a Ação Base:", tickers_boleta, key="acao_base")

with col2:
    tipo_ativo = st.selectbox(
        "Tipo de Ativo:", 
        ["Ação Pura", "Call (Comprador)", "Put (Comprador)"],
        key="tipo_ativo"
    )

with col3:
    qtd_op = st.number_input("Quantidade:", min_value=0, value=100, step=100, key="qtd_op")

ticker_mercado = f"{acao_operar}.SA"
preco_ref = dados_mercado[ticker_mercado]["Preco_Anterior"] if ticker_mercado in dados_mercado else 10.0

with col4:
    if tipo_ativo == "Ação Pura":
        label = "Preço da Ação (R$):"
        default = preco_ref
    elif tipo_ativo == "Call (Comprador)":
        label = "Prêmio da Call (R$):"
        default = dados_mercado[ticker_mercado]["Call"]["Premio_Est"] if ticker_mercado in dados_mercado else 0.5
    else:
        label = "Prêmio da Put (R$):"
        default = dados_mercado[ticker_mercado]["Put"]["Premio_Est"] if ticker_mercado in dados_mercado else 0.5
    
    preco_compra_op = st.number_input(label, min_value=0.0, value=float(default), step=0.01, key="preco_compra")

with col5:
    preco_venda_op = st.number_input("Preço Venda (R$, 0 = aberto):", min_value=0.0, value=0.0, step=0.01, key="preco_venda")

st.markdown("---")
st.write("#### 🔧 Customização de Código de Opção")

if tipo_ativo == "Ação Pura":
    st.info("✅ Operação em ação pura - sem código de opção")
    codigo_opcao_customizado = ""
else:
    if tipo_ativo == "Call (Comprador)":
        opcao_recomendada = dados_mercado[ticker_mercado]["Call"]["Opcao_Ticker"] if ticker_mercado in dados_mercado else "?????"
        vencimento_rec = dados_mercado[ticker_mercado]["Call"]["Vencimento_B3"] if ticker_mercado in dados_mercado else "N/A"
        strike_rec = dados_mercado[ticker_mercado]["Call"]["Strike_Alvo"] if ticker_mercado in dados_mercado else 0
    else:
        opcao_recomendada = dados_mercado[ticker_mercado]["Put"]["Opcao_Ticker"] if ticker_mercado in dados_mercado else "?????"
        vencimento_rec = dados_mercado[ticker_mercado]["Put"]["Vencimento_B3"] if ticker_mercado in dados_mercado else "N/A"
        strike_rec = dados_mercado[ticker_mercado]["Put"]["Strike_Alvo"] if ticker_mercado in dados_mercado else 0
    
    col_code1, col_code2, col_code3 = st.columns(3)
    with col_code1:
        st.write(f"**Opção Recomendada:** {opcao_recomendada}")
    with col_code2:
        st.write(f"**Strike:** R$ {strike_rec}")
    with col_code3:
        st.write(f"**Vencimento:** {vencimento_rec}")
    
    st.markdown("---")
    codigo_opcao_customizado = st.text_input(
        "Inserir código diferente (deixe em branco para usar o recomendado):",
        value="",
        placeholder=f"Ex: VALEJ120, PETRM40, etc",
        key="codigo_custom"
    )

col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 2])

with col_btn1:
    if st.button("💾 Gravar Operação", use_container_width=True, key="btn_gravar"):
        if qtd_op > 0:
            ticker_chave = f"{acao_operar}.SA"
            
            if tipo_ativo == "Ação Pura":
                codigo_final = ""
            else:
                codigo_final = codigo_opcao_customizado if codigo_opcao_customizado.strip() else opcao_recomendada
            
            operacao = {
                "id": str(uuid.uuid4()),
                "ticker": ticker_chave,
                "tipo": tipo_ativo,
                "qtd": qtd_op,
                "preco_compra": preco_compra_op,
                "preco_venda": preco_venda_op,
                "codigo_opcao": codigo_final,
                "data_operacao": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
            if ticker_chave not in st.session_state.carteira_operacoes:
                st.session_state.carteira_operacoes[ticker_chave] = []
            
            st.session_state.carteira_operacoes[ticker_chave].append(operacao)
            st.success(f"✅ Operação gravada! {tipo_ativo} de {acao_operar} x {qtd_op}")
        else:
            st.error("❌ Quantidade deve ser > 0")

with col_btn2:
    if st.button("🗑️ Limpar Carteira", use_container_width=True, key="btn_limpar"):
        st.session_state.carteira_operacoes = {}
        st.info("Carteira limpa!")

st.markdown("---")
st.write("### 📈 Grade Dinâmica Unificada (Mercado + Minha Carteira)")

linhas_tabela = []
for ticker, info in banco_b3.items():
    if ticker not in dados_mercado:
        continue
    
    if info["Setor"] not in setores_sel:
        continue
    if info["Consenso_CP"] not in vies_sel:
        continue
    
    m = dados_mercado[ticker]
    tem_operacoes = ticker in st.session_state.carteira_operacoes
    
    if modo_exibicao == "Apenas Minha Carteira" and not tem_operacoes:
        continue
    
    if not tem_operacoes:
        linhas_tabela.append({
            "Ação": ticker.replace(".SA", ""),
            "Fechamento Anterior (R$)": m["Preco_Anterior"],
            "Entrada Técnica": m["Entrada"],
            "Call Recomendada": m["Call"]["Opcao_Ticker"],
            "Put Recomendada": m["Put"]["Opcao_Ticker"],
            "Setor": info["Setor"],
            "Tipo em Carteira": "-",
            "Quantidade": "-",
            "Preço Entrada": "-",
            "Lucro/Prejuízo (R$)": 0.0,
            "Data Operação": "-"
        })
    else:
        for op in st.session_state.carteira_operacoes[ticker]:
            if op["tipo"] == "Ação Pura":
                preco_ref_calculo = op["preco_venda"] if op["preco_venda"] > 0 else m["Preco_Anterior"]
                lucro = (preco_ref_calculo - op["preco_compra"]) * op["qtd"]
            else:
                preco_ref_calculo = op["preco_venda"] if op["preco_venda"] > 0 else 0
                if preco_ref_calculo > 0:
                    lucro = (preco_ref_calculo - op["preco_compra"]) * op["qtd"]
                else:
                    lucro = 0
            
            linhas_tabela.append({
                "Ação": ticker.replace(".SA", ""),
                "Fechamento Anterior (R$)": m["Preco_Anterior"],
                "Entrada Técnica": m["Entrada"],
                "Call Recomendada": m["Call"]["Opcao_Ticker"],
                "Put Recomendada": m["Put"]["Opcao_Ticker"],
                "Setor": info["Setor"],
                "Tipo em Carteira": op["tipo"],
                "Código Opção": op["codigo_opcao"] if op["codigo_opcao"] else "-",
                "Quantidade": op["qtd"],
                "Preço Entrada (R$)": op["preco_compra"],
                "Preço Venda (R$)": op["preco_venda"] if op["preco_venda"] > 0 else "Aberto",
                "Lucro/Prejuízo (R$)": round(lucro, 2),
                "Data Operação": op["data_operacao"]
            })

if linhas_tabela:
    df_final = pd.DataFrame(linhas_tabela)
    df_final = df_final.sort_values(by="Ação")
    
    lucro_total = df_final["Lucro/Prejuízo (R$)"].sum()
    qtd_operacoes = len(df_final)
    
    c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
    c_kpi1.metric("Operações em Carteira", qtd_operacoes)
    c_kpi2.metric("Lucro/Prejuízo Total (R$)", f"R$ {round(lucro_total, 2)}")
    c_kpi3.metric("Status", "✅ Operando" if lucro_total >= 0 else "⚠️ No vermelho")
    
    st.dataframe(df_final, use_container_width=True, hide_index=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Carteira_Operacoes')
    excel_data = output.getvalue()
    
    st.download_button(
        label="📥 Baixar Carteira em Excel",
        data=excel_data,
        file_name=f"carteira_b3_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("Nenhuma operação registrada. Use o painel acima para adicionar operações.")

st.markdown("---")
st.write("### 🔍 Análise Detalhada de Ativo")

tickers_unicos = sorted([t.replace(".SA", "") for t in st.session_state.carteira_operacoes.keys()]) if st.session_state.carteira_operacoes else []

if tickers_unicos:
    ativo_analise = st.selectbox("Selecione ativo para análise:", tickers_unicos, key="ativo_analise")
    
    if ativo_analise:
        ticker_completo = f"{ativo_analise}.SA"
        dados_ativos = dados_mercado[ticker_completo]
        consenso_ativo = banco_b3[ticker_completo]
        
        col_análise1, col_análise2, col_análise3 = st.columns(3)
        
        with col_análise1:
            st.info(f"**📊 Fundamentos LP:**\n\n{consenso_ativo['Fundamentos_LP']}")
        
        with col_análise2:
            st.success(f"""**🎯 Técnica - {ativo_analise}:**
- **Entrada:** R$ {dados_ativos['Entrada']}
- **Alvo:** R$ {dados_ativos['Alvo_Saida']}
- **Stop:** R$ {dados_ativos['Stop']}
- **Volatilidade:** {round((dados_ativos['Alvo_Saida'] - dados_ativos['Stop']) / dados_ativos['Preco_Anterior'] * 100, 1)}%
""")
        
        with col_análise3:
            st.warning(f"""**🚀 Opções Disponíveis:**

**CALL (Alta):**
- Código: {dados_ativos['Call']['Opcao_Ticker']}
- Strike: R$ {dados_ativos['Call']['Strike_Alvo']}
- Prêmio ~: R$ {dados_ativos['Call']['Premio_Est']}
- Vence: {dados_ativos['Call']['Vencimento_B3']}

**PUT (Proteção):**
- Código: {dados_ativos['Put']['Opcao_Ticker']}
- Strike: R$ {dados_ativos['Put']['Strike_Alvo']}
- Prêmio ~: R$ {dados_ativos['Put']['Premio_Est']}
- Vence: {dados_ativos['Put']['Vencimento_B3']}
""")
else:
    st.info("Adicione operações acima para ver análise detalhada.")
