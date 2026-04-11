import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página (Deve ser sempre o primeiro comando Streamlit)
st.set_page_config(page_title="Dashboard de Estatísticas", layout="wide")

# 2. Função para carregar dados com cache para performance
@st.cache_data
def load_data():
    return pd.read_parquet('viz/data_base.parquet')

df_original = load_data()

st.title("CAT - Comunicado de Acidentes do Trabalho 2025")

# --- 3. FILTROS NA SIDEBAR ---
todas_ufs = sorted(df_original['UF Munic. Empregador'].dropna().unique())
uf_filtro = st.multiselect("Selecione a UF", options=todas_ufs)
st.divider()


# Aplicando os filtros ao DataFrame que será usado nos gráficos
df = df_original.copy()
if uf_filtro:
    df = df[df['UF Munic. Empregador'].isin(uf_filtro)]


# INDICADORES
st.subheader("Indicadores Gerais")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de Acidentes", f"{len(df):,}".replace(",", "."))
with col2:
    st.metric("Idade Média", f"{df['Idade'].mean():.0f} anos")
with col3:
    st.metric("Casos Críticos (Óbitos)", f"{int(df['target'].sum()):,}".replace(",", "."))

st.divider()




# TABELA DE GRAVIDADE
with st.expander("Top 10 Combinações Históricas de Maior Risco", expanded=False):
    st.write("Estas combinações abaixo representam o maior volume de casos fatais/críticos no banco de dados.")
    casos_criticos = df[df['target'] == 1]
    
    combinacoes_perigosas = (
        casos_criticos.groupby(['Tipo do Acidente', 'AGENTES_AGRUPADOS', 'NATUREZA_LEZAO_AJUSTADA'])
        .size()
        .reset_index(name='Total Acidentes Graves')
        .sort_values('Total Acidentes Graves', ascending=False)
        .head(10)
    )
    st.table(combinacoes_perigosas)



#GRAFICO DE LINHAS
st.divider()
st.subheader("Sazionalidade de acidentes - 2025")

meses_ordem = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
}

df_mes = df['Mes_Acidente'].value_counts().sort_index().reset_index()
df_mes['Mes_Nome'] = df_mes['Mes_Acidente'].map(meses_ordem)

fig_mes = px.line(
    df_mes, 
    x='Mes_Nome', 
    y='count', 
    markers=True,
    labels={'Mes_Nome': 'Mês', 'count': 'Total de Acidentes'},
    template="plotly_white"
)
fig_mes.update_traces(line_color='#1f77b4')
st.plotly_chart(fig_mes, use_container_width=True)



# --- 5. GRÁFICOS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("Distribuição por tipo de acidente")
    df_tipo = df['Tipo do Acidente'].value_counts().reset_index()
    
    cor_padrao = "#1f77b4" 
    
    fig_1 = px.bar(
        df_tipo, 
        x='Tipo do Acidente', 
        y='count',
        color_discrete_sequence=[cor_padrao], 
        labels={'Tipo do Acidente': 'Tipo', 'count': 'Quantidade'},
        template="plotly_white"
    )    
    st.plotly_chart(fig_1, use_container_width=True)   

with c2:
    st.subheader("Distribuição por Gênero")
    fig_sexo = px.pie(
    df, 
    names='Sexo', 
    hole=0.4,
    color='Sexo',
    color_discrete_map={
        'Masculino': '#1f77b4',
        'Feminino': "#BB0083"
    }
    )
    st.plotly_chart(fig_sexo, use_container_width=True)


with st.container():
    st.subheader("Partes do Corpo Mais Atingidas (TOP 10)")
    df['Parte Corpo Atingida'] = df['Parte Corpo Atingida'].str.strip()
    df_parte = df['Parte Corpo Atingida'].value_counts().reset_index().head(10)
    
    cor_padrao = "#1f77b4" 
    
    fig_parte = px.bar(
        df_parte, 
        x='count', 
        y='Parte Corpo Atingida',
        orientation='h',
        color_discrete_sequence=[cor_padrao],
        labels={'Parte Corpo Atingida': 'Parte do Corpo', 'count': 'Quantidade'},
        template="plotly_white"
    )
    fig_parte.update_layout(yaxis={'categoryorder':'total ascending'})
    
    fig_parte.update_xaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor='LightPink',           
        griddash='dash'
        )

    st.plotly_chart(fig_parte, use_container_width=True)

with st.container():
    st.subheader("Estados com mais acidentes (TOP 10)")
    df_estado = df['UF Munic. Empregador'].str.strip().value_counts().reset_index().head(10)
       
    cor_padrao = "#1f77b4" 
    
    fig_estado = px.bar(
        df_estado, 
        x='count', 
        y='UF Munic. Empregador',
        orientation='h',
        color_discrete_sequence=[cor_padrao],
        labels={'UF Munic. Empregador': 'Estado (UF)', 'count': 'Total de Acidentes'},
        template="plotly_white"
    )
    fig_estado.update_layout(
        yaxis={'categoryorder':'total ascending'},
        xaxis_title="Quantidade de Acidentes",
        yaxis_title=None
    )
    fig_estado.update_xaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor='LightPink',           
        griddash='dash'
        )
    
    st.plotly_chart(fig_estado, use_container_width=True)


with st.container():
    st.subheader("Principais Agentes Causadores (TOP 10)")
    # Limpeza e contagem para a coluna AGENTES_AGRUPADOS
    df_agente = df['AGENTES_AGRUPADOS'].str.strip().value_counts().reset_index().head(10)
       
    cor_padrao = "#1f77b4" 
    
    fig_agente = px.bar(
        df_agente, 
        x='count', 
        y='AGENTES_AGRUPADOS',
        orientation='h',
        color_discrete_sequence=[cor_padrao],
        labels={'AGENTES_AGRUPADOS': 'Agente Agrupado', 'count': 'Total de Acidentes'},
        template="plotly_white"
    )
    fig_agente.update_layout(
        yaxis={'categoryorder':'total ascending'},
        xaxis_title="Quantidade de Acidentes",
        yaxis_title=None
    )
    fig_agente.update_xaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor='LightGray',           
        griddash='dash'
    )
    
    st.plotly_chart(fig_agente, use_container_width=True)

with st.container():
    st.subheader("Funções com mais acidentes (TOP 10)")
    # Limpeza e contagem para a coluna TITULO
    df_titulo = df['TITULO'].str.strip().value_counts().reset_index().head(10)
       
    cor_padrao = "#1f77b4" 
    
    fig_titulo = px.bar(
        df_titulo, 
        x='count', 
        y='TITULO',
        orientation='h',
        color_discrete_sequence=[cor_padrao],
        labels={'TITULO': 'Função (CBO)', 'count': 'Total de Acidentes'},
        template="plotly_white"
    )
    fig_titulo.update_layout(
        yaxis={'categoryorder':'total ascending'},
        xaxis_title="Quantidade de Acidentes",
        yaxis_title=None
    )
    fig_titulo.update_xaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor='LightGray', # Mudei para cinza para ficar mais sóbrio, mas pode manter LightPink           
        griddash='dash'
    )
    
    st.plotly_chart(fig_titulo, use_container_width=True)
