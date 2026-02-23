# %%
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

df = pd.concat(todos_os_dados, ignore_index=True)

#%%
df['Data Nascimento'] = pd.to_datetime(df['Data Nascimento'], errors='coerce')
df['Data Acidente'] = pd.to_datetime(df['Data Acidente'], errors='coerce')
df['Data  Afastamento'] = pd.to_datetime(df['Data  Afastamento'], errors='coerce')
df['Data Despacho Benefício'] = pd.to_datetime(df['Data Despacho Benefício'], errors='coerce')
df['Data Emissão CAT'] = pd.to_datetime(df['Data Emissão CAT'], errors='coerce')
df['Idade'] = (df['Data Acidente'] - df['Data Nascimento']).dt.days // 365
df.sample(5)

#%% Checando INFO das colunas
'''
df.info()
 #   Column                       Non-Null Count   Dtype         
---  ------                       --------------   -----         
 0   Agente  Causador  Acidente   579723 non-null  str           
 1   Data Acidente                579723 non-null  datetime64[us]
 2   CBO                          579723 non-null  int64         
 3   CBO.1                        579723 non-null  str           
 4   CID-10                       579723 non-null  str           
 5   CID-10.1                     579723 non-null  str           
 6   CNAE2.0 Empregador           579723 non-null  int64         
 7   CNAE2.0 Empregador.1         579723 non-null  str           
 8   Emitente CAT                 579723 non-null  str           
 9   Espécie do benefício         579723 non-null  str           
 10  Filiação Segurado            579723 non-null  str           
 11  Indica Óbito Acidente        579723 non-null  str           
 12  Munic Empr                   579723 non-null  str           
 13  Natureza da Lesão            579723 non-null  str           
 14  Origem de Cadastramento CAT  579723 non-null  str           
 15  Parte Corpo Atingida         579723 non-null  str           
 16  Sexo                         579723 non-null  str           
 17  Tipo do Acidente             579723 non-null  str           
 18  UF  Munic.  Acidente         579723 non-null  str           
 19  UF Munic. Empregador         579723 non-null  str           
 20  Data  Afastamento            504630 non-null  datetime64[us]
 21  Data Despacho Benefício      16 non-null      datetime64[us]
 22  Data Acidente.1              579723 non-null  str           
 23  Data Nascimento              579677 non-null  datetime64[us]
 24  Data Emissão CAT             229077 non-null  datetime64[us]
 25  Tipo de Empregador           579723 non-null  str           
 26  CNPJ/CEI Empregador          579723 non-null  int64         
 27  Idade                        579677 non-null  float64       
dtypes: datetime64[us](5), float64(1), int64(3), str(19)
memory usage: 123.8 MB
'''
# %%
df['Indica Óbito Acidente'] = df['Indica Óbito Acidente'].str.replace(' ', '', regex=False)
df['Indica Óbito Acidente'].unique()

# %% Verificando dados de óbitos
df[df['Indica Óbito Acidente'] == 'Sim'].sample(n=5)

#%% Verificando as colunas para criar as variáveis do modelo de Classificação
df.columns

# %% Variáveis escolhidas de forma analítica
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
    'UF  Munic.  Acidente',
    'UF Munic. Empregador',
    'Idade'
]
df_features = df[features].copy()

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
#Exclusão da coluna 'CID-10'
df_features = df_features.drop('CID-10', axis=1)
df_features.sample(n=5)

# %% A variável 'Agente Causador Acidente' possui uma cauda longa em sua distribuição, devido a isso, vamos considerar valores que se repetem pelo menos 1000 vezes.
# contagem_agentes = df_features['Agente  Causador  Acidente'].value_counts()
# agentes_raros = contagem_agentes[contagem_agentes < 1000].index
# df_features['Agente_Resumido'] = df_features['Agente  Causador  Acidente'].replace(agentes_raros, 'Outros/Raros')
# print(f"Reduzimos de {len(contagem_agentes)} para {df_features['Agente_Resumido'].nunique()} categorias!")

#%%
pd.set_option('display.max_rows', 300)
print(df_features['Agente  Causador  Acidente'].value_counts().to_string())

#%%
df_features['Sexo'] = df_features['Sexo'].str.replace(' ', '', regex=False)
df_features = df_features[df_features['Sexo'].isin(['Masculino', 'Feminino'])]
df_features['Sexo'].value_counts()

# %%
df_features.sample(n=5)

#%%
df_features['Agente  Causador  Acidente'].value_counts().to_excel('analise_agentes.xlsx')
df_agentes = pd.read_excel('agentes_regularizados.xlsx')
df_agentes.head()

# %%
df_features = pd.merge(
    df_features,
    df_agentes[['Agente  Causador  Acidente', 'AGENTES_AGRUPADOS']],
    how='left'
)
df_features = df_features.drop('Agente  Causador  Acidente', axis=1)

#%%
df_features['AGENTES_AGRUPADOS'].value_counts()

# %%
df_features['Natureza da Lesão'].value_counts()

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
    # Remove espaços em branco extras nas pontas para evitar erros de busca
    dataframe[nome_coluna] = dataframe[nome_coluna].astype(str).str.strip()
    
    # Cria a nova coluna com o agrupamento
    dataframe['NATUREZA_LEZAO_AJUSTADA'] = dataframe[nome_coluna].map(mapeamento_lesoes)
    
    # Caso algum valor não esteja no dicionário, mantém o original
    dataframe['NATUREZA_LEZAO_AJUSTADA'] = dataframe['NATUREZA_LEZAO_AJUSTADA'].fillna(dataframe[nome_coluna])
    
    return dataframe

df_features = sintetizar_lesoes(df_features, 'Natureza da Lesão')
df_features.sample(n=10)

#%%
