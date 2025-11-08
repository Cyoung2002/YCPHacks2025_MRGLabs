import pandas as pd

df = pd.read_csv('/Users/caroline/PycharmProjects/YCPHacks2025_MRGLabs/ycpHacks/Mobilgrease 28.csv', usecols=range(0,1))

subset = df.iloc[3:3454]

print(subset)
#show first 5 rows
print(df.head())

#show column names
print(df.columns)

#show number of rows and columns
print(df.shape)

#Access one column
#print(df['A'])

#filter data
#filtered = df[df['A'] < 4000]
#print(filtered)

# Access a specfic row
print(df.iloc[0])#first row
