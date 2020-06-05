import csv

zip_lat_long_table= []
with open('zipcode-lat-long.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter =',')
    next(readCSV, None)
    for row in readCSV:
        print(row)
        zip_lat_long_table[str(row[0])]= row[1],row[2]
        
print(zip_lat_long_table)

