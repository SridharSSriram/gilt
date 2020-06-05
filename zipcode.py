import csv

zip_lat_long_table= {}
with open('zipcode-lat-long.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter =',')
    next(readCSV, None)
    for row in readCSV:
        
        lat_long_entry = [row[1], row[2]]

        zip_lat_long_table[row[0]]= lat_long_entry
        

def fetch_lat_long(zipcode):
    return zip_lat_long_table[zipcode]