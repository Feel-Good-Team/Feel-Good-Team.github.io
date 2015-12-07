import sqlite3
import time
import datetime
from xlrd import open_workbook


conn = sqlite3.connect('motiveQuote.db')
c = conn.cursor()

def tableCreate():
	c.execute("CREATE TABLE stuffToPlot(ID INT, quote TEXT, author TEXT, majortheme TEXT, minortheme TEXT)")




"""
Open Excel file named simple.xlsx where all quotes are.
"""
book = open_workbook('simple.xlsx',on_demand=True)
sheet = book.sheet_by_name("Sheet1")

# Number of columns
num_cols = sheet.ncols
# Number of rows
nrows = sheet.nrows   




def dataEntry():
    idForDb = -1


    # Iterate through rows
    for row_idx in range(0, sheet.nrows):
        # Get cell object (quote) by row, col
        cell_obj_quote = sheet.cell(row_idx, 0)  
        quote = cell_obj_quote.value
        
        cell_obj_author = sheet.cell(row_idx, 1)
        author = cell_obj_author.value
        
        cell_obj_maj = sheet.cell(row_idx, 2)
        majortheme = cell_obj_maj.value
        
        cell_obj_min = sheet.cell(row_idx, 3)
        minortheme = cell_obj_min.value
        
        idForDb = idForDb + 1

        c.execute("INSERT INTO stuffToPlot (ID, quote, author, majortheme, minortheme) VALUES (?,?,?,?,?)", 
            (idForDb, quote, author, majortheme, minortheme))

        conn.commit()


dataEntry()
