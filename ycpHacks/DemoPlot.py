import pandas as pd
import matplotlib.pyplot as plt

# Creating variables for obtaining csv file input for baseline and sample (currently just one)
baseline = input("Enter baseline: ")
sampleData = input("Enter sample data: ")

# Reading the imported csv files, skipping the first row since it is not needed data
base = pd.read_csv(baseline, skiprows=1)
sample = pd.read_csv(sampleData, skiprows=1)

# Plotting the data from the csv, will need to dynamically pull the names from the files later
plt.plot(base['cm-1'], base['A'], label='baseline', linewidth=1)
plt.plot(sample['cm-1'], sample['A'], label='sampledata', linewidth=1)

# Axis labels
plt.xlabel('cm-1')
plt.ylabel('A')

# Creating legend for plot
plt.legend()

# Generating the plot
plt.show()