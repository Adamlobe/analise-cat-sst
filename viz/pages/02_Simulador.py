import streamlit as st
import pandas as pd
import joblib

# 1. Configuração da Página (DEVE SER A PRIMEIRA)
st.set_page_config(page_title="Simulador de Risco CAT", page_icon="🚀", layout="wide")

# 2. Carregar o modelo
@st.cache_resource
def load_model():
    return joblib.load('../model/modelo.pkl')

model = load_model()

## VARIÁVEIS E BASES
df = pd.read_parquet('data_base.parquet')

# --- Mapeamentos e Variáveis (Seu código original aqui...) ---
df_cbo_ref = df[['CBO', 'TITULO']].drop_duplicates().sort_values('TITULO')
mapeamento_cbo = dict(zip(df_cbo_ref['TITULO'], df_cbo_ref['CBO']))
var_funcoes = df_cbo_ref['TITULO'].unique()

var_sexo = df['Sexo'].dropna().sort_values().unique()
var_TipoAcidente = df['Tipo do Acidente'].dropna().sort_values().unique()
var_agente = df['AGENTES_AGRUPADOS'].dropna().sort_values().unique()
var_uf = df['UF Munic. Empregador'].dropna().sort_values().unique()
var_parte = df['Parte Corpo Atingida'].dropna().sort_values().unique()
var_natureza = df['NATUREZA_LEZAO_AJUSTADA'].dropna().sort_values().unique()
var_cid = df['CID_Descricao_Grupo'].dropna().sort_values().unique()

map_meses = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12}
map_dias = {"Segunda-feira": 0, "Terça-feira": 1, "Quarta-feira": 2, "Quinta-feira": 3, "Sexta-feira": 4, "Sábado": 5, "Domingo": 6}
var_mes_nomes = list(map_meses.keys())
var_dia_nomes = list(map_dias.keys())

# --- Interface ---
st.title("🚀 Simulador de Risco de Acidente")
st.markdown("Preencha os dados abaixo para calcular a probabilidade de um caso crítico.")

# --- Formulário de Entrada (Seu código original aqui...) ---
with st.form("predicao_form"):
    st.subheader("Cenário do Acidente")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cbo_nome = st.selectbox("CBO-Função", var_funcoes)
        sexo = st.selectbox("Sexo", var_sexo)
        idade = st.number_input("Idade", min_value=14, max_value=100, value=30)
    with col2:
        tipo = st.selectbox("Tipo do Acidente", var_TipoAcidente)
        agente = st.selectbox("Agente Agrupado", var_agente)
        uf = st.selectbox("UF", var_uf)
        mes_nome = st.selectbox("Mês", var_mes_nomes)
    with col3:
        parte = st.selectbox("Parte Corpo Atingida", var_parte)
        natureza = st.selectbox("Natureza da Lesão", var_natureza)
        cid = st.selectbox("Grupo CID", var_cid)
        dia_nome = st.selectbox("Dia da Semana", var_dia_nomes)

    submit = st.form_submit_button("Analisar Risco")

if submit:
    # (Lógica de predição idêntica à sua...)
    cbo_input = mapeamento_cbo[cbo_nome]
    mes_input = map_meses[mes_nome]
    dia_input = map_dias[dia_nome]
    
    dados_usuario = pd.DataFrame([{
        'CBO': cbo_input, 'Natureza da Lesão': natureza, 'Parte Corpo Atingida': parte,
        'Sexo': sexo, 'Tipo do Acidente': tipo, 'UF Munic. Empregador': uf,
        'Idade': float(idade), 'CID_Descricao_Grupo': cid, 'AGENTES_AGRUPADOS': agente,
        'NATUREZA_LEZAO_AJUSTADA': natureza, 'Mes_Acidente': mes_input, 'Dia_Semana': dia_input
    }])

    prob = model.predict_proba(dados_usuario)[0, 1]
    
    st.divider()
    st.write(f"### Probabilidade de Óbito/Caso Crítico: **{prob:.0%}**")
    
    if prob >= 0.1:
        st.error(f"⚠️ **ALTO RISCO DETECTADO**\nA probabilidade de {prob:.0%} está acima do limite de segurança (10%).")
    else:
        st.success(f"✅ **RISCO CONTROLADO**\nA probabilidade de {prob:.0%} é considerada baixa.")