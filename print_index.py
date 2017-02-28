import sqlite3
import sys

#takes in system argument as the sqlite3 db_Name and connects to it
db_name = sys.argv[1]
conn = sqlite3.connect(db_name)

#selects data required and orders it by term and docid
stmt = 	"""
		SELECT TERM, DOCID, POSITIONS
		FROM LISTINGS
		ORDER BY TERM, DOCID ASC;
		"""

curs = conn.execute(stmt)
count = 0
docPositions = dict()


for row in curs:
	#in the very first row, print the term and then set old_term to that term
	if count == 0:
		old_term = row[0]
		print(old_term + "\t", end = '')

	term = row[0]
	docid = row[1]
	positions = row[2]

	#once a new term is found, print a newline, the new term and the
	#first doc/positions for the term
	if term != old_term:
		print("\n"+term + "\t" + docid + ":"+ str(positions) + ";", end = '')
	#if the term is the same as the old_term, print the doc/positions along the same line
	else:
		print(docid + ":"+ str(positions) + ";", end = '')
	

	old_term = term
	count += 1



conn.close()