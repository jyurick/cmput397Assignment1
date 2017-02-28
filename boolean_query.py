import sqlite3
import sys


if len(sys.argv) != 3:
	print("Requires two command line arguments. i.e python3 boolean_query.py db_filename \"query\"")
	quit()

db_name = sys.argv[1]
query = sys.argv[2]
#print("Query: "+ query)

#db_name = "movies.sql"
conn = sqlite3.connect(db_name)




def orOperation(pList1, pList2):
	'''
	Parameters:
		- pList1: first sorted list of docIds
		- pList2: second sorted list of docIds

	Transverses each list and adds every unique docId to the postings list.

	Returns: List of docIds that are in pList1 or pList2
	'''
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

def andOperation(pList1, pList2):
	'''
	Parameters:
		- pList1: first sorted list of docIds
		- pList2: second sorted list of docIds

	Transverses each list and adds every docId that exists in both lists to the postings list.

	Returns: List of docIds that are in pList1 and pList2
	'''
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

def positionOperation(t1List, t2List):
	'''
	Parameters:
		- t1List: List of tuples of format (docId, positions) sorted by docId for term 1
		- t2List: List of tuples of format (docId, positions) sorted by docId for term 2

	Transverses each list and adds every docId that appears in both lists
	having a position in t1List that is one less than a position in t2List

	Returns: Sorted List of docIds that satisfies the above requirement

	'''
	postings = list()
	x = 0
	y = 0

	while x < len(t1List) and y < len(t2List):
		#step lists indexes along each list until identical docIds are found
		if t1List[x][0] > t2List[y][0]:
			y += 1

		elif t1List[x][0] < t2List[y][0]:
			x += 1

		else:
			#once identical docIds are found, prepare position lists for each term
			t1Positions = t1List[x][1].split(',')
			t2Positions = t2List[y][1].split(',')
			for a in range(len(t1Positions)):
				t1Positions[a] = int(t1Positions[a])

			for b in range(len(t2Positions)):
				t2Positions[b] = int(t2Positions[b])

			togetherFound = False
			a = 0
			b = 0
			while a < len(t1Positions) and b < len(t2Positions) and togetherFound == False:
				#similar to the AND operation, step along each list of positions until 
				#the end of the lists are reached or positions are found where the 
				#t1Position = t2Position - 1
				if t1Positions[a] + 1 < t2Positions[b]:
					a += 1
				elif t1Positions[a] + 1 > t2Positions[b]:
					b += 1
				else:
					#to positions are found together, add that posting to the postings list
					togetherFound = True
					postings.append(t1List[x][0])

			x += 1
			y += 1

	#return list of postings found that fulfills the requirements
	return postings



def lookupPhrase(phrase):
	'''
	Parameters:
		- phrase: String representing phrase in the format "word1_word2_word3"

	Returns: Sorted List of docIds that contain all words in the phrase in succession.
	'''
	phrase.replace('"', '')

	#termDocPositions is a dictionary in format {term: [(docid1, positions1), (docid2, positions2)]}
	termDocPositions = dict()
	docIds = list()
	terms = phrase.split('_')
	for x in range(len(terms)):
		terms[x] = terms[x].lower()

	for term in terms:
		termDocPositions.setdefault(term, [])
		stmt = "SELECT DOCID, POSITIONS FROM LISTINGS WHERE TERM = ? ORDER BY DOCID ASC"
		p = (term, )
		curs = conn.execute(stmt, p)
		for row in curs:
			#add (docid, positions) tuples to term key in the termDocPositions dictionary
			docid = row[0]
			positions = row[1]
			termDocPositions[term].append((docid,positions))

	x = 0
	while x < len(terms) - 1:
		#checking the terms 2 at a time i.e with 4 terms generate positional postings list for
		#term1 and term2, term2 and term3, term3 and term4
		positionalAND = positionOperation(termDocPositions[terms[x]], termDocPositions[terms[x+1]])
		if x == 0:
			#if checking the first two terms, add all postings to result list
			docIds = positionalAND
		else:
			#update result list to contain all docids that exist in the old result list as well as
			#the new list returned from the positionOperation
			docIds = andOperation(docIds, positionalAND)
		x += 1

	return docIds

	


	

def lookupPostings(term):
	'''
	Paramaters: 
		- term: String representing term to be searched

	Returns: list of docIds that contain the term
	'''

	#If there are two double quotation, the term is a phrase and should be 
	#analyzed using the lookupPhrase function
	if term.count('"') == 2:
		return lookupPhrase(term[1:-1])
	

	stmt = "SELECT DOCID FROM LISTINGS WHERE TERM = ? ORDER BY DOCID ASC"
	p = (term.lower(), )
	curs = conn.execute(stmt, p)
	docIds = list()

	#store all docIds returned from the query in a list of docIds. This listed will
	#be sorted from the query.
	for row in curs:
		docIds.append(row[0])

	return docIds

def simplify_query(query):
	'''
	Parameters:
		- query: String query
	Returns: Sorted list of docs that satisfy the query
	'''

	qLength = len(query)
	subList = list()
	for x in range(qLength):

		subFound = False
		firstParenthesisFound = False
		#look for left parenthesis from the start of the query, if it is found look for the right
		#parenthesis from the end of the query
		if query[x] == '(':
			y = qLength - 1
			firstParenthesisFound = True
			while y >= x:
				if query[y] == ')':
					subFound = True
					break
				y -= 1
		#once both parenthesis are found, cut out the section of the subquery and replace it with the
		#word "SUB". Recursively call simplify_query on the subquery and store the result list
		#in subList to be used later
		if firstParenthesisFound and not subFound:
			print("Mismatched parenthesis in the query:" + query)

		if subFound == True:
			subList = simplify_query(query[x+1:y])
			query = query[:x] + "SUB" + query[y+1:]
			break



	x = 0
	while x < len(query):
		#look for phrases in the query. When a phrase is found replace all spaces within the phrase
		#with underscores
		if query[x] == '"':
			x += 1
			firstQuotationFound = True
			while query[x] != '"' and x < len(query):
				if query[x] == ' ':
					query = query[:x] + '_' + query[x+1:]
				x += 1
		x += 1

	#split the query into a list of the query items. If a query item is not "AND" or "OR", replace it
	#with a postings list of the documents that are returned for either the term or the phrase
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

	#while there are at least 3 items still in the simpleQuery list, it means there are still
	#AND or OR operations to do with the postings list. At the end of this while loop simpleQuery
	#should only contain one item, a postings list of the docs that satisfies the query.
	if len(simpleQuery) % 2 != 1:
		print("Expected an odd total of terms+operations+phrases in the query: " + query)
		quit()

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


	return simpleQuery[0]

def testOrOperation():
	if orOperation([1,2,3,4,5], [6,7,8,9]) != [1,2,3,4,5,6,7,8,9]:
		print("orOperation test 1 failed")
	if orOperation([], [6,7,8,9]) != [6,7,8,9]:
		print("orOperation test 2 failed")
	if orOperation([1,2,3,4,5], [3,4,5]) != [1,2,3,4,5]:
		print("orOperation test 3 failed")


def testAndOperation():
	if andOperation([1,2,3,4,5], [6,7,8,9]) != []:
		print("andOperation test 1 failed")
	if andOperation([7,8,10], [6,7,8,9]) != [7,8]:
		print("andOperation test 2 failed")
	if andOperation([1,2,3,4,5], [3,4,5]) != [3,4,5]:
		print("andOperation test 3 failed")
	if andOperation([1,2,3,4,5], []) != []:
		print("andOperation test 4 failed")



def testLookupPhrase():
	#this also tests the positionOperation
	if lookupPhrase("stemming_never") != ['doc1','doc2']:
		print("lookupPhrase test 1 failed")


	if lookupPhrase("stemming_should") != ['doc4']:
		print("lookupPhrase test 2 failed")

	if lookupPhrase("stemming_should_never") != []:
		print("lookupPhrase test 3 failed")


def testLookupPostings():
	if lookupPostings("boolean") != ['doc1','doc2']:
		print("lookupPostings test 1 failed")

	if lookupPostings("stemming") != ['doc1','doc2', 'doc3', 'doc4']:
		print("lookupPostings test 2 failed")

	if lookupPostings("argentina") != []:
		print("lookupPostings test 3 failed")

def testSimplifyQuery():
	if simplify_query("Stemming") != ['doc1', 'doc2', 'doc3', 'doc4']:
		print("simplify_query test 1 failed")

	if simplify_query("system AND (recall OR precision)") != ['doc1', 'doc2']:
		print("simplify_query test 2 failed")

	if simplify_query("system OR vocabulary OR while AND at OR should") != ['doc4']:
		print("simplify_query test 3 failed")

	if simplify_query('"stemming never" AND "stemming increases"') != []:
		print("simplify_query test 4 failed")

	if simplify_query('"stemming should" OR "stemming increases"') != ['doc3', 'doc4']:
		print("simplify_query test 5 failed")

	if simplify_query("(precision AND while) OR time") != ['doc4']:
		print("simplify_query test 6 failed")


def testEverything():
	testOrOperation()
	testAndOperation()
	testLookupPhrase()
	testLookupPostings()
	testSimplifyQuery()



if __name__ == "__main__":
	print(simplify_query(query))
	#testEverything()


conn.close()









