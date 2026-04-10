# %%
# Importação das bibliotecas para realizar a concatenação das tabelas e e processo de exploração dos dados
import pandas as pd
import os
import glob
import zipfile
pd.set_option('display.max_columns', None)

# %%
diretorio = 'arquivos_zipados/'
todos_os_dados = []

arquivos_zip = glob.glob(os.path.join(diretorio, "*.ZIP"))

#%%
for zip_file in arquivos_zip:
    with zipfile.ZipFile(zip_file, 'r') as z:
        for nome_arquivo in z.namelist():
            if nome_arquivo.endswith('.csv'):
                with z.open(nome_arquivo) as f:
                    df_temp = pd.read_csv(f, sep=';', encoding='latin1')
                    todos_os_dados.append(df_temp)

# Concatenação dos dados em único DataFrame
df = pd.concat(todos_os_dados, ignore_index=True)

#%% 
# Verificação das colunas e seus tipos
df.info()

#%%
# Ajuste de algumas colunas para correta tipagem
df['Data Nascimento'] = pd.to_datetime(df['Data Nascimento'], errors='coerce')
df['Data Acidente'] = pd.to_datetime(df['Data Acidente'], errors='coerce')
df['Data  Afastamento'] = pd.to_datetime(df['Data  Afastamento'], errors='coerce')
df['Data Despacho Benefício'] = pd.to_datetime(df['Data Despacho Benefício'], errors='coerce')
df['Data Emissão CAT'] = pd.to_datetime(df['Data Emissão CAT'], errors='coerce')

#%%
# Criação de coluna para verificar a Idade do acidentado
df['Idade'] = (df['Data Acidente'] - df['Data Nascimento']).dt.days // 365

# %% Algumas colunas tinham espaços sobressalentes em virtude da sua informação
df['Indica Óbito Acidente'] = df['Indica Óbito Acidente'].str.replace(' ', '', regex=False)
df['Indica Óbito Acidente'].unique()

# %% Verificando dados de óbitos
df[df['Indica Óbito Acidente'] == 'Sim'].sample(n=5)

#%% Verificando as colunas para criar as variáveis do modelo de Classificação
df.columns

# %% 
# Variáveis escolhidas de forma analítica
features = [
    'Data Acidente',
    'Indica Óbito Acidente',
    'Agente  Causador  Acidente',
    'CBO',
    'CID-10',
    'Natureza da Lesão',
    'Parte Corpo Atingida',
    'Sexo',
    'Tipo do Acidente',
    'UF Munic. Empregador',
    'Idade'
]
df_features = df[features].copy()
# Nota: apesar de tratar algumas colunas acima, nem todas foram utilizadas, faz parte do processo...

#%% Verificando os tipos de dados das variáveis e as se possuímos linhas nulas
df_features.info()

#%% Exclusão das linhas que não possui idades
df_features = df_features.dropna(subset=['Idade'])

#%% No dataset, possui diversos códigos CID, para não criar ruídos no modelo, foi sumarizados os tipos de CID
df_features['CID-10'].value_counts()

def mapear_cid(primeira_letra):
    if primeira_letra in ['A', 'B']: return 'A_B_Infecciosas'
    if primeira_letra in ['C', 'D']: return 'C_D_Neoplasias'
    if primeira_letra == 'E': return 'E_Endocrinas'
    if primeira_letra == 'F': return 'F_Mentais'
    if primeira_letra == 'G': return 'G_Sistema Nervoso'
    if primeira_letra == 'H': return 'H_Olhos_Ouvidos'
    if primeira_letra == 'I': return 'I_Circulatorio'
    if primeira_letra == 'J': return 'J_Respiratorio'
    if primeira_letra == 'K': return 'K_Digestivo'
    if primeira_letra == 'M': return 'M_Osteomuscular'
    if primeira_letra in ['S', 'T']: return 'S_T_Lesoes_Envenenamento'
    if primeira_letra in ['V', 'W', 'X', 'Y']: return 'V_W_X_Y_Causas_Externas'
    if primeira_letra == 'Z': return 'Z_Fatores_Saude'
    return 'Outros'

df_features['CID_Descricao_Grupo'] = df_features['CID-10'].str[0].apply(mapear_cid)
# Exclusão da coluna 'CID-10'
# Para esta parte, foi feito um estudo das doenças do CID-10 através do link https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/acidente_trabalho_incapacidade/tabelas-cid-10
df_features = df_features.drop('CID-10', axis=1)
df_features.sample(n=5)

#%%
df_features['Sexo'] = df_features['Sexo'].str.replace(' ', '', regex=False)
df_features = df_features[df_features['Sexo'].isin(['Masculino', 'Feminino'])]
df_features['Sexo'].value_counts()

# %% A variável 'Agente Causador Acidente' possui uma cauda longa em sua distribuição, devido a isso, vamos considerar valores que se repetem pelo menos 1000 vezes.

df_features['Agente  Causador  Acidente'].value_counts().to_excel('analise_agentes.xlsx')
df_agentes = pd.read_excel('agentes_regularizados.xlsx')
df_agentes.head()
# Nesta parte, para fácil visualização utilizamos outras ferramentas para padronizar os agentes causados
# **Importante comentar que foi feito uma sumarização técnica dos agentes, conforme os conceitos de segurança do trabalos e suas Normas Regulamentadoras.

# %% Mergeando os agentes padronizados
df_features = pd.merge(
    df_features,
    df_agentes[['Agente  Causador  Acidente', 'AGENTES_AGRUPADOS']],
    how='left'
)
df_features = df_features.drop('Agente  Causador  Acidente', axis=1)

#%% 
# Ajuste da padronização das lesões também
mapeamento_lesoes = {
    'Lesao Imediata': 'Lesões Traumáticas Gerais',
    'Fratura': 'Lesões Ósseas e Articulares',
    'Corte, Laceracao, Fe': 'Cortes e Ferimentos Abertos',
    'Contusao, Esmagament': 'Lesões por Impacto/Pressão',
    'Escoriacao, Abrasao': 'Cortes e Ferimentos Abertos',
    'Distensao, Torcao': 'Lesões Ósseas e Articulares',
    'Outras Lesoes, Nic': 'Outras Lesões / Não Clas.',
    'Luxacao': 'Lesões Ósseas e Articulares',
    'Lesao Imediata, Nic': 'Lesões Traumáticas Gerais',
    'Queimadura ou Escald': 'Queimaduras e Efeitos Térmicos',
    'Doenca, Nic': 'Doenças e Inflamações',
    'Lesoes Multiplas': 'Lesões Traumáticas Gerais',
    'Inflamacao de Articu': 'Doenças e Inflamações',
    'Queimadura Quimica (': 'Queimaduras e Efeitos Térmicos',
    'Amputacao ou Enuclea': 'Lesões Gravíssimas/Sistêmicas',
    'Doenca Contagiosa ou': 'Doenças e Inflamações',
    'Perda ou Diminuicao': 'Danos Sensoriais/Cognitivos',
    'Concussao Cerebral': 'Danos Sensoriais/Cognitivos',
    'Choque Eletrico e El': 'Lesões Gravíssimas/Sistêmicas',
    'Envenenamento Sistem': 'Lesões Gravíssimas/Sistêmicas',
    'Hernia de Qualquer N': 'Lesões de Partes Moles',
    'Dermatose (Erupcao,': 'Doenças e Inflamações',
    'Asfixia, Estrangulam': 'Lesões Gravíssimas/Sistêmicas',
    'Efeito de Radiacao (': 'Queimaduras e Efeitos Térmicos',
    'Pneumoconiose (Silic': 'Doenças e Inflamações',
    'Congelamento, Geladu': 'Queimaduras e Efeitos Térmicos',
    'Intermacao, Insolaca': 'Queimaduras e Efeitos Térmicos'
}

def sintetizar_lesoes(dataframe, nome_coluna):
    dataframe[nome_coluna] = dataframe[nome_coluna].astype(str).str.strip()
    dataframe['NATUREZA_LEZAO_AJUSTADA'] = dataframe[nome_coluna].map(mapeamento_lesoes)  
    dataframe['NATUREZA_LEZAO_AJUSTADA'] = dataframe['NATUREZA_LEZAO_AJUSTADA'].fillna(dataframe[nome_coluna])
    return dataframe

df_features = sintetizar_lesoes(df_features, 'Natureza da Lesão')
df_features.sample(n=5)

#%%
mapeamento_completo = {
    # Membros Superiores
    'Dedo': 'Dedos',
    'Mao (Exceto Punho ou': 'Mão',
    'Braco (Entre O Punho': 'Braço',
    'Braco (Acima do Coto': 'Braço',
    'Antebraco (Entre O P': 'Antebraço',
    'Punho': 'Punho',
    'Cotovelo': 'Cotovelo',
    'Ombro': 'Ombro',
    'Membros Superiores,': 'Membros Superiores (Geral)',

    # Membros Inferiores
    'Pe (Exceto Artelhos)': 'Pé',
    'Joelho': 'Joelho',
    'Perna (Entre O Torno': 'Perna',
    'Perna (Do Tornozelo,': 'Perna',
    'Articulacao do Torno': 'Tornozelo',
    'Coxa': 'Coxa',
    'Artelho': 'Dedos do Pé',
    'Membros Inferiores,': 'Membros Inferiores (Geral)',

    # Cabeça e Pescoço
    'Olho (Inclusive Nerv': 'Olhos',
    'Cabeca, Nic': 'Cabeça',
    'Cabeca, Partes Multi': 'Cabeça',
    'Face, Partes Multipl': 'Face',
    'Boca (Inclusive Labi': 'Boca',
    'Cranio (Inclusive En': 'Crânio',
    'Nariz (Inclusive Fos': 'Nariz',
    'Mandibula (Inclusive': 'Mandíbula',
    'Ouvido (Externo, Med': 'Ouvidos',
    'Pescoco': 'Pescoço',

    # Tronco e Órgãos
    'Dorso (Inclusive Mus': 'Dorso/Costas',
    'Torax (Inclusive Org': 'Tórax',
    'Quadris (Inclusive P': 'Quadril',
    'Abdome (Inclusive Or': 'Abdômen',
    'Tronco, Parte Multip': 'Tronco',
    'Tronco, Nic': 'Tronco',

    # Outros / Sistemas
    'Partes Multiplas - A': 'Partes Múltiplas',
    'Sistema Nervoso': 'Sistemas Internos',
    'Aparelho Respiratori': 'Sistemas Internos',
    'Aparelho Digestivo': 'Sistemas Internos',
    'Aparelho Circulatori': 'Sistemas Internos',
    'Aparelho Genito-Urin': 'Sistemas Internos',
    'Sistemas e Aparelhos': 'Sistemas Internos',
    'Sistema Musculo-Esqu': 'Sistemas Internos',
    'Localizacao da Lesao': 'Não Especificado'
}

# Aplicando a padronização de uma só vez
df_features['Parte Corpo Atingida'] = df_features['Parte Corpo Atingida'].replace(mapeamento_completo)

# Verificando o resultado final
df_features['Parte Corpo Atingida'].value_counts()

#%%
# Criando mais features, pois achei que poderia identificar sazionalidade ao modelo.
df_features['Mes_Acidente'] = df_features['Data Acidente'].dt.month
df_features['Dia_Semana'] = df_features['Data Acidente'].dt.dayofweek
df_features = df_features.drop('Data Acidente', axis=1)

#%%
# Verificando a quantidade de funções existentes
df_features['CBO'].value_counts()

#%% 
# Foi escolhido utilizar apenas o grupo da ocupação, para o modelo não apresentar overfiting
df_features['CBO'] = df_features['CBO'].astype(str)
df_features['CBO'] = df_features['CBO'].str[:4]

#%%
df_features['Indica Óbito Acidente'].value_counts()

#%%
# Definição do target
df_features['target'] = df_features['Indica Óbito Acidente'].map({
    'Não': 0,
    'Sim': 1
})
df_features = df_features.drop('Indica Óbito Acidente', axis=1)

df_features['target'].value_counts()

#%%
df_features.to_parquet('data_viz.parquet', index=False, engine='fastparquet')

# %%
# Inicio do Modelo
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

X = df_features.drop('target', axis=1)
y = df_features['target']

#separação das variáveis categóricas e numéricas
categoricas = X.select_dtypes(include=['object', 'string']).columns.tolist()
numericas = X.select_dtypes(exclude='object').columns.tolist()

# Pré-processador
preprocessador = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categoricas),
        ('num', 'passthrough', numericas)
    ]
)

# Pipeline completo
modelo = Pipeline(steps=[
    ('preprocessamento', preprocessador),
    ('classificador', RandomForestClassifier(
        class_weight='balanced', # Como os dados estão desbalanceados, foi utilizado esse parâmetro
        n_estimators=200,
        random_state=42
    ))
])

# %%
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# %%
modelo.fit(X_train, y_train)

# %%
#Escolha do threshold padrão
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

y_pred = modelo.predict(X_test)
y_proba = modelo.predict_proba(X_test)[:, 1]

print("Matriz de Confusão (threshold 0.5):")
print(confusion_matrix(y_test, y_pred))

print("\nRelatório de Classificação (threshold 0.5):")
print(classification_report(y_test, y_pred))

print("ROC-AUC:", roc_auc_score(y_test, y_proba))

# %%
'''
Dado o forte desbalanceamento da base, o threshold padrão de 0.5 mostrou-se inadequado, 
resultando em baixa sensibilidade para a classe minoritária.

Optou-se por reduzir o threshold para 0.1 com o objetivo de maximizar o recall da
classe positiva (óbitos), priorizando a identificação de casos críticos.

Essa escolha aumenta o número de falsos positivos, reduzindo a precisão, 
porém diminui significativamente o risco de falsos negativos — que, neste contexto, 
possuem maior impacto analítico e estratégico.
'''

threshold = 0.1
y_pred_01 = (y_proba >= threshold).astype(int)

print("Matriz de Confusão (threshold 0.1):")
print(confusion_matrix(y_test, y_pred_01))

print("\nRelatório de Classificação (threshold 0.1):")
print(classification_report(y_test, y_pred_01))

# %%
# Curva Precision-Recall 

from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt

precision, recall, thresholds = precision_recall_curve(y_test, y_proba)

plt.figure()
plt.plot(recall, precision)
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Curva Precision-Recall")
plt.show()

# %%
# Curva ROC

from sklearn.metrics import roc_curve, roc_auc_score

fpr, tpr, roc_thresholds = roc_curve(y_test, y_proba)
roc_auc = roc_auc_score(y_test, y_proba)

plt.figure()
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.3f}")
plt.plot([0, 1], [0, 1], linestyle="--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Curva ROC")
plt.legend()
plt.show()

#%%
import joblib

# Salva o pipeline completo (inclui o pré-processamento e a Random Forest)
joblib.dump(modelo, 'modelo.pkl')