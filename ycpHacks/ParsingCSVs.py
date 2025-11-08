import csv

with open('mobilegrease 28.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    for row in reader:
        print(row)