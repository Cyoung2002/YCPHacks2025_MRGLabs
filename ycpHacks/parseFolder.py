import glob
import os

from ycpHacks.DemoPlot import create_demo_plot


#Main class to parse through the folder supplied and "obtain" the name of each csv
#Goal of this class is to successfully use the names to be supplied to DemoPlot to create each graph
#Make generic after the fact -- too hardcoded for now
def parseFolder():
    print("Parsing Folder")
    #Directory for where the folder full of CVS will be
    base_dir = r"C:\YCPHacks2025\YCPHacks2025_MRGLabs\Uploaded CSVs"

    #Debug
    print("Script started!")
    print(f"Looking in: {base_dir}")

    if not os.path.exists(base_dir):
        print("Directory doesn't exist!")
        return

    #Hard coded baseline (could be passed as an argument, testing for now)
    baseline = "Mobilgrease 28.csv"
    #the list of all the file names that end with csv (the data set)
    listOfFiles = glob.glob(base_dir + "/*.csv")
    #Debug line
    print(f"Found files: {listOfFiles}")

    #go through the entire list and make a demo plot for each.
    for i, filename in enumerate(listOfFiles):
        img_buffer = create_demo_plot(baseline, filename)
        output_name = f"plot_{i+1:03d}.png"
        save_dir = r"C:\YCPHacks2025\YCPHacks2025_MRGLabs\Generated Graphs"
        os.makedirs(save_dir, exist_ok=True)  # create folder if it doesn’t exist

        #More debug
        print(f"Output directory ready: {save_dir}")

        print("Basic structure works!")

        save_path = os.path.join(save_dir, output_name)

        with open(save_path, 'wb') as f:
            f.write(img_buffer.getvalue())

        print(f" Image saved as: {save_path}")

if __name__ == "__main__":
    print("Hello, let's parse!")
    parseFolder()