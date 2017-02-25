import sqlite3
import sys

db_name = sys.argv[1]
conn = sqlite3.connect(db_name)

stmt = 	"""
		SELECT TERM, DOCID, POSITIONS
		FROM LISTINGS
		ORDER BY TERM ASC;
		"""

curs = conn.execute(stmt)
count = 0
docPositions = dict()

for row in curs:
	if count == 0:
		old_term = row[0]
		print(old_term + "\t", end = '')

	term = row[0]
	docid = row[1]
	positions = row[2]


	if term != old_term:
		print("\n"+term + "\t" + docid + ":"+ str(positions) + ";", end = '')
	else:
		print(docid + ":"+ str(positions) + ";", end = '')
	

	old_term = term
	count += 1



conn.close()