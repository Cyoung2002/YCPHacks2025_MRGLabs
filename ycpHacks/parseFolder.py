import glob
import os

from ycpHacks.DemoPlot import create_demo_plot


#Main class to parse through the folder supplied and "obtain" the name of each csv
#Goal of this class is to successfully use the names to be supplied to DemoPlot to create each graph
#Make generic after the fact -- too hardcoded for now
def parseFolder():

    #Directory for where the folder full of CVS will be
    base_dir = r"C:\YCPHacks2025\YCPHacks2025_MRGLabs\Uploaded CSVs"
    #Hard coded basline (could be passed as an arguement, testing for now)
    baseline = "Mobilgrease 28.csv"
    #the list of all the file names that end with csv (the data set)
    listOfFiles = glob.glob(base_dir + "/*.csv")

    #go through the entire list and make a demo plot for each.
    for filename in listOfFiles:
        create_demo_plot(baseline, filename)
