import sqlite3
import time
import datetime




conn = sqlite3.connect('motiveQuote.db')
c = conn.cursor()
sql = "SELECT * FROM stuffToPlot WHERE author =?"

wordUsed = 'Michael Jordan'


"""
def readData():
	for row in c.execute(sql,[(wordUsed)]):


		line = str(row).replace(')','').replace('(','').split(",")
		print line
readData()

"""

for row in c.execute(sql,[(wordUsed)]):
	print row[2]