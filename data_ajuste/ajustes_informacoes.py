#%%
import pandas as pd

#%%
df = pd.read_parquet('data_viz.parquet')
df.columns

#%%
df_cbo = pd.read_csv('../cbo2002-familia.csv', sep=';', encoding='latin1')
df_cbo.columns

#%%
df['CBO'] = df['CBO'].astype(str)
df_cbo['CODIGO'] = df_cbo['CODIGO'].astype(str)

df_final = pd.merge(
    df,
    df_cbo,
    left_on='CBO',
    right_on='CODIGO',
    how='inner'
)
df_final.sample(10)

#%%
df_final.to_parquet('data_base.parquet', index=False)

# %%
