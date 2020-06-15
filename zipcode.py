import csv
import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(THIS_FOLDER, 'data/robust-zipcode-lat-long.csv')

zip_lat_long_table= {}
with open(my_file) as csvfile:
    readCSV = csv.reader(csvfile, delimiter =',')
    next(readCSV, None)
    for row in readCSV:

        lat_long_entry = [row[1], row[2]]

        zip_lat_long_table[row[0]]= lat_long_entry


def fetch_lat_long(zipcode):
    if zipcode in zip_lat_long_table:
        return zip_lat_long_table[zipcode]
    else:
        return None,None
