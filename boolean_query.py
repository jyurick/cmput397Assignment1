import sqlite3
import sys


# if len(sys.argv) != 3:
# 	print("Requires two command line arguments. i.e python3 boolean_query.py db_filename query")
# 	quit()

# db_name = sys.argv[1]
#query = sys.argv[1]
db_name = "movies.sql"
conn = sqlite3.connect(db_name)


def andOperation(pList1, pList2):
	postings = list()
	x = 0
	y = 0

	while x < len(pList1) and y < len(pList2):
		if pList1[x] > pList2[y]:
			y += 1

		elif pList1[x] < pList2[y]:
			x += 1

		else:
			postings.append(pList1[x])
			x += 1
			y += 1

	return postings

def orOperation(pList1, pList2):
	postings = list()
	x = 0
	y = 0

	while x < len(pList1) and y < len(pList2):
		if pList1[x] > pList2[y]:
			postings.append(pList2[y])
			y += 1

		elif pList1[x] < pList2[y]:
			postings.append(pList1[x])
			x += 1

		else:
			postings.append(pList1[x])
			x += 1
			y += 1

	if x == len(pList1):
		while y < len(pList2):
			postings.append(pList2[y])
			y += 1

	elif y == len(pList2):
		while x < len(pList1):
			postings.append(pList1[x])
			x += 1		

	return postings

def lookupPhrase(phrase):
	pass
	

def lookupPostings(term):
	if term.count('"') == 2:
		return lookupPhrase(term)
	#Returns a list of document ids that contain the term
	stmt = "SELECT DOCID FROM LISTINGS WHERE TERM = ? ORDER BY DOCID ASC"
	p = (term.lower(), )
	curs = conn.execute(stmt, p)
	docIds = list()

	for row in curs:
		docIds.append(row[0])

	return docIds

def simplify_query(query):

	#print("Analyzing:" + query)
	qLength = len(query)
	subList = list()
	for x in range(qLength):

		subFound = False
		if query[x] == '(':
			y = qLength - 1
			while y >= x:
				if query[y] == ')':
					subFound = True
					break
				y -= 1

		if subFound == True:
			subList = simplify_query(query[x+1:y])
			query = query[:x] + "SUB" + query[y+1:]
			break
	print(query)

	x = 0
	while x < len(query):
		if query[x] == '"':
			x += 1
			while query[x] != '"':
				if query[x] == ' ':
					query = query[:x] + '_' + query[x+1:]
				x += 1
		x += 1

	print(query)
	queryList = query.split()
	simpleQuery = list()
	for x in range(len(queryList)):
		if queryList[x] not in ("AND", "OR"):
			if queryList[x] == "SUB":
				simpleQuery.append(subList)
			else:
				simpleQuery.append(lookupPostings(queryList[x]))
		else:
			simpleQuery.append(queryList[x])
	print(simpleQuery)
	while len(simpleQuery) >= 3:
		copy = list()
		length = len(simpleQuery)
		if simpleQuery[1] == "AND":
			copy.append(andOperation(simpleQuery[0], simpleQuery[2]))
		elif simpleQuery[1] == "OR":
			copy.append(orOperation(simpleQuery[0], simpleQuery[2]))
		for x in range(3,length):
			copy.append(simpleQuery[x])
		simpleQuery = copy

	#print(simpleQuery)
	return simpleQuery[0]




if __name__ == "__main__":
	print(simplify_query('"stemming should" OR "stemming increases"'))
	#print(orOperation([1],[1,4,6,8, 9, 10, 11 ,12]))

conn.close()









