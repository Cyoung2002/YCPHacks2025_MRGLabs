import os
from YCPHacks2025_MRGLabs.ycpHacks.DemoPlot import create_demo_plot

base_dir = r"C:\YCPHacks25\YCPHacks2025_MRGLabs\Uploaded CSVs"

img_buffer = create_demo_plot(os.path.join(base_dir, "91707_mobil_centaur.csv"), os.path.join(base_dir, "19231.csv"))

output_name = "test.png"
save_dir = r"C:\YCPHacks25\Generated Graphs"
os.makedirs(save_dir, exist_ok=True)  # create folder if it doesn’t exist

save_path = os.path.join(save_dir, output_name)

with open(save_path, 'wb') as f:
    f.write(img_buffer.getvalue())

print(f" Image saved as: {save_path}")
