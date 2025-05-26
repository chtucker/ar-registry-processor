import pandas as pd

df = pd.read_csv('data/extracted_names_v1.csv')
df.head(10).to_csv('data/debug_names_head.csv', index=False)
print('Saved first 10 rows to data/debug_names_head.csv') 