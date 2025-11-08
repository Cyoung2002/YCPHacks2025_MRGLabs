import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('104345.csv')
da = pd.read_csv('Mobilgrease 28.csv')

df = pd.read_csv('104345.csv', skiprows=1)
da = pd.read_csv('Mobilgrease 28.csv', skiprows=1)

print(df.head())

plt.plot(df['cm-1'], df['A'])

plt.xlabel('cm-1')
plt.ylabel('A')

plt.show()