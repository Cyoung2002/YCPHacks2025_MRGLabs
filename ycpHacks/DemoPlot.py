import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('104345.csv')

df = pd.read_csv('104345.csv', skiprows=1)
print(df.head())

plt.plot(df['cm-1'], df['A'])

plt.show()

