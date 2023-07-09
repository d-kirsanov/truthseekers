import pandas as pd
import plotly.express as px
import sys


df = pd.read_csv(sys.argv[1])

df['iq'] = df['iq'].apply(lambda x: x/100)
df['truth'] = df['truth'].apply(lambda x: x/10000)

fig = px.line(df, x = 'gen', y = ['error','iq','truth'], title='evolution of truth seekers')
fig.show()
