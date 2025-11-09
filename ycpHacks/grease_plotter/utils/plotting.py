import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def generate_plot(baseline_path, sample_path, output_path):
    # Read CSVs, skipping first row
    base = pd.read_csv(baseline_path, skiprows=1)
    sample = pd.read_csv(sample_path, skiprows=1)

    # Extract labels for the legend
    base_label = os.path.splitext(os.path.basename(baseline_path))[0]
    sample_label = os.path.splitext(os.path.basename(sample_path))[0]

    # Extract numeric y-data arrays for baseline and sample
    y_baseline = base['A'].to_numpy()
    y_sample = sample['A'].to_numpy()

    # Create figure and plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(base['cm-1'], base['A'], label=base_label, linewidth=0.3, color = 'green')
    ax.plot(sample['cm-1'], sample['A'], label=sample_label, linewidth=0.3, color = 'blue')

    # Invert x-axis
    ax.invert_xaxis()

    # Axis labels
    plt.xlabel('cm-1')
    plt.ylabel('A')

    diff = np.abs(y_baseline - y_sample)
    mean_diff = np.mean(diff)
    max_diff = np.max(diff)

    # Correlation coefficient
    corr = np.corrcoef(y_baseline, y_sample)[0, 1]

    # Mean Squared Error
    mse = np.mean((y_baseline - y_sample) ** 2)

    text = (f"Mean diff: {mean_diff:.3f}\n"
            f"Max diff: {max_diff:.3f}\n"
            f"Corr: {corr:.3f}\n"
            f"MSE: {mse:.4f}")

    plt.text(0.02, 0.98, text, transform=plt.gca().transAxes,
             verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7))

    # Legend
    plt.legend(
        loc='lower left',
        bbox_to_anchor=(0, -0.25),
        borderaxespad=0,
        frameon=False
    )

    # Save to output path
    fig.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f" Saved plot to {output_path}")
