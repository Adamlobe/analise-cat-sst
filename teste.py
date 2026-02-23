# %%
import pandas as pd
pd.set_option('display.max_columns', None)

# %%
df = pd.read_csv('D.SDA.PDA.005.CAT.202512/D.SDA.PDA.005.CAT.202512.csv', sep=';',encoding='latin-1', nrows=1000)
df['Data Nascimento'] = pd.to_datetime(df['Data Nascimento'], errors='coerce')


#%%
df['Data Acidente'] = pd.to_datetime(df['Data Acidente'], errors='coerce')
df['Data  Afastamento'] = pd.to_datetime(df['Data  Afastamento'], errors='coerce')
df['Data Despacho Benefício'] = pd.to_datetime(df['Data Despacho Benefício'], errors='coerce')
df['Data Emissão CAT'] = pd.to_datetime(df['Data Emissão CAT'], errors='coerce')
df['Idade'] = (df['Data Acidente'] - df['Data Nascimento']).dt.days // 365
df.head()

#%%
features = [
    'Idade',
    'CBO',
    'CNAE2.0 Empregador',
    'Sexo',
    'Tipo do Acidente',
    'UF Munic. Empregador',
    'Agente  Causador  Acidente'
]
df_features = df[features].copy()
df_features.dtypes

#%%
df_features = pd.get_dummies(df_features, prefix=["Sexo", "Tipo do Acidente",
                                                  'UF Munic. Empregador','Agente  Causador  Acidente'])

# %%
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

scaler = StandardScaler()

df_escalonado = scaler.fit_transform(df_features)

#%%
inercias = []
K = range(1, 15) # Vamos testar de 1 a 10 grupos

for k in K:
    modelo = KMeans(n_clusters=k, random_state=42)
    modelo.fit(df_escalonado)
    inercias.append(modelo.inertia_)

# Agora vamos desenhar o gráfico
plt.figure(figsize=(8, 5))
plt.plot(K, inercias, 'bx-')
plt.xlabel('Número de Clusters (k)')
plt.ylabel('Inércia (Soma dos Quadrados das Distâncias)')
plt.title('Método do Cotovelo para encontrar o K ideal')
plt.show()

#%%
kmeans_final = KMeans(n_clusters=6, random_state=42, n_init=10)

df_final = df_features.copy()
df_final['Cluster'] = kmeans_final.fit_predict(df_escalonado)

print(df_final['Cluster'].value_counts())

#%%
# Ver as características principais de cada grupo
analise_clusters = df_final.groupby('Cluster').agg({
    'Idade': 'mean',
    'Tipo do Acidente_Típico              ': 'mean', # Isso mostra a % de acidentes típicos
    'Sexo_Masculino           ': 'mean'           # Isso mostra a % de homens
}).round(2)

analise_clusters

#%%
import seaborn as sns

# Definindo o estilo visual
plt.figure(figsize=(10, 6))
sns.set_theme(style="whitegrid")

# Criando o gráfico de dispersão
# Vamos usar Idade vs Sexo_Masculino, com cores baseadas no Cluster
scatter = sns.scatterplot(
    data=df_final, 
    x='Idade', 
    y='Sexo_Masculino           ', 
    hue='Cluster', 
    palette='viridis', 
    s=100, 
    alpha=0.7
)

plt.title('Distribuição dos Clusters por Idade e Sexo', fontsize=15)
plt.xlabel('Idade do Trabalhador', fontsize=12)
plt.ylabel('Sexo Masculino (0=Não, 1=Sim)', fontsize=12)
plt.legend(title='Perfil (Cluster)', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()
# %%
