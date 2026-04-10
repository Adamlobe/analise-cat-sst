import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="IA na Segurança do Trabalho",
    page_icon="🛡️",
    layout="wide"
)

# Estilização CSS para melhorar a estética do texto
st.markdown("""
    <style>
    .main-title {
        color: #1f77b4;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    .section-header {
        color: #1f77b4;
        font-weight: bold;
        margin-top: 30px;
    }
    .content-text {
        font-size: 1.1rem;
        line-height: 1.6;
        text-align: justify;
    }
    .highlight-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown('<h1 class="main-title">Inteligência Artificial: O Novo Horizonte da Prevenção de Acidentes</h1>', unsafe_allow_html=True)
st.divider()

# Coluna Principal de Texto
col_texto, col_espaco, col_nav = st.columns([2, 0.1, 1])

with col_texto:
    st.markdown('<h3 class="section-header">O Paradigma da Segurança</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="content-text">
    Historicamente, a Segurança do Trabalho operou sob um modelo <b>reativo</b>. A gestão de riscos baseava-se na análise de eventos que já ocorreram: 
    investigamos o acidente, emitimos a CAT e tentamos corrigir a falha para evitar a repetição. Embora essencial, esse método olha apenas para o retrovisor.
    <br><br>
    A chegada da IA e do Machine Learning nos permite <b>olhar para o para-brisa</b>. O verdadeiro valor da IA não está em substituir a experiência do 
    Engenheiro ou Técnico de Segurança, mas em potencializar sua percepção através da Análise Preditiva.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<h3 class="section-header">O Desafio das Variáveis: A "Impressão Digital" do Risco</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="content-text">
    O grande desafio para os gestores modernos não é apenas implementar a tecnologia, mas sim <b>identificar as variáveis corretas</b> que precedem um acidente grave. 
    Diferente de uma receita de bolo, os gatilhos de risco não são universais:
    </div>
    """, unsafe_allow_html=True)

    # Cards de Segmentos
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**Setor Elétrico**\n\nUmidade, tempo de experiência e tipo de equipamento.")
    with c2:
        st.warning("**Construção Civil**\n\nAltura, turno de trabalho e descanso entre jornadas.")
    with c3:
        st.error("**Indústria Química**\n\nTempo de exposição e compatibilidade de substâncias.")

    st.markdown("""
    <div class="content-text">
    Cada segmento possui sua própria "impressão digital" de perigo. A IA brilha justamente aqui: ela ajuda o gestor a descobrir quais dessas variáveis, 
    muitas vezes ignoradas no dia a dia, possuem maior peso estatístico na ocorrência de uma fatalidade.
    </div>
    """, unsafe_allow_html=True)

with col_nav:
    st.markdown("### 🚀 Navegação")
    st.write("Explore as ferramentas desenvolvidas neste projeto:")
    
    # Botões de Navegação
    if st.button("📊 Acessar Dashboard Estatístico", use_container_width=True):
        st.switch_page("pages/01_Dashboard.py")
    
    if st.button("🔮 Acessar Simulador Preditivo", use_container_width=True):
        st.switch_page("pages/02_Simulador.py")
    
    st.markdown("---")
    st.markdown("""
    **Pilares da Tecnologia:**
    1. Identificação de Padrões
    2. Antecipação de Cenários
    3. Gestão de Recursos
    """)

# Seção Final (Largura Total)
st.markdown('<h3 class="section-header">Por que usar Machine Learning na Segurança do Trabalho?</h3>', unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("#### 🔍 Padrões Complexos")
    st.write("A IA cruza milhares de variáveis simultaneamente para identificar combinações fatais invisíveis em análises manuais.")
with f2:
    st.markdown("#### ⏳ Antecipação")
    st.write("O modelo preditivo estima a probabilidade de um incidente se tornar um 'caso crítico', permitindo intervenções reais.")
with f3:
    st.markdown("#### 🎯 Eficiência")
    st.write("Empresas focam esforços onde o modelo aponta maior risco estatístico, otimizando o investimento em prevenção.")

st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
st.markdown('### O Propósito deste Projeto')
st.markdown("""
Este ecossistema foi desenvolvido para demonstrar a aplicação prática da Ciência de Dados na proteção da vida. 
Através de uma base de dados robusta, unimos o **Dashboard Estatístico**, que nos conta o que aconteceu, ao 
**Simulador Preditivo**, que nos alerta sobre o que pode acontecer.
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p style="text-align: center; font-style: italic; color: #1f77b4;">"A tecnologia serve à vida. O dado é o guia, mas a prevenção é o objetivo final."</p>', unsafe_allow_html=True)