import pandas as pd
import matplotlib.pyplot as plt

sample_base = pd.read_csv("C:\YCPHacks25\YCPHacks2025_MRGLabs\ycpHacks\104345.csv")

plt.title("Test Plot")
plt.plot(sample_base.cm-1, sample_base.A, linewidth = 1)

plt.show()

