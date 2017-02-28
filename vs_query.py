#vs_query [index location] [k] [scores] [term_1] [term_2] ... [term_n]
import sqlite3
import sys


conn = sqlite3.connect(sys.argv[1])
k = int(sys.argv[2])
displayScores = sys.argv[3]

terms = set()
query = list()
for x in range(4,len(sys.argv)):
	terms.add(sys.argv[x])
	query.append(sys.argv[x])

def cosineScore(k, displayScores, query):
	'''
	Parameters:
		- k: Int representing the number of results to display
		- displayScores: Char representing whether or not the scores should be displayed in the result. Expected: 'y' or 'n'
		- query: List of Strings representing the terms being queried
	'''
	docScores = dict()
	docLengths = dict()
	terms = set(query)
	#docScores is a dictionary in format {docid: Score}
	#docLengths is a dictionary in format {docid: [Length1, Length2, ...]} and will be used to store
	#the tf_idf values associated with terms that appear in each doc

	#add all terms from system arguments to a set of terms (terms) as well as a list of terms (query)



	stmt = 	"""
			SELECT DOCID, TF_IDF, IDF FROM LISTINGS WHERE TERM = ?
			"""
	#for each term in the set of terms
	for term in terms:
		p = (term, )
		curs = conn.execute(stmt, p)
		#count the number of times the term appears in the query
		tf = query.count(term)
		for row in curs:
			docName = row[0]
			tf_idf = float(row[1])
			idf = float(row[2])
			#calculate tf_idf weighting for the query. idf is functionally dependent on the term so the 
			#data from the index file can be used
			query_tf_idf = tf * idf

			#update docScores library by adding the Score calculated by term_tf_idf * query_tf_idf
			docScores.setdefault(docName, 0)
			docScores[docName] = docScores[docName] + (tf_idf * query_tf_idf)

			#update docLengths with the tf_idf value of the term for the doc
			docLengths.setdefault(docName, [])
			docLengths[docName].append(tf_idf)

	#for every docId in docLengths, change the value to the vector length associated with the document
	for doc in docLengths.keys():
		lengths = docLengths[doc]
		vectorLength = 0
		for l in lengths:
			vectorLength += l**2
		vectorLength = vectorLength**(1/2)
		docLengths[doc] = vectorLength

	#normalize each score stored in docScores using the corresponding vector lengths in docLengths
	#store a list of tuples in format (docId, score)
	scores = list()
	for doc in docScores.keys():
		if docLengths[doc] != 0:
			scores.append((doc, docScores[doc]/docLengths[doc]))

	#sort scores list by score decreasing
	sortedScores = sorted(scores, key=lambda x: -x[1])


	k = min(len(sortedScores), k)

	msg = ""
	#create message representing only the top k scores from the sorted scores list
	for x in range(k):
		#if the user chose to display scores, print the (docId, score) tuples,
		#if not pring only the docIds
		if displayScores.lower() == 'y':
			msg += "(" + sortedScores[x][0] + "," + str(sortedScores[x][1]) + ")" 
		elif displayScores.lower() == 'n':
			msg += sortedScores[x][0]
		if x != k-1:
			msg += ","

	return msg

def testCosineScore():
	if cosineScore(2, 'n', ['boolean','retrieval','recall']) != "doc2,doc1":
		print("CosineScore test 1 failed")

	if cosineScore(2, 'n', ['boolean','retrieval','precision']) != "doc1,doc2":
		print("CosineScore test 2 failed")

	if cosineScore(2, 'n', ['vocabulary','indexing','time','query']) != "doc4,doc3":
		print("CosineScore test 3 failed")

if __name__ == "__main__":
	#testCosineScore()
	print(cosineScore(k, displayScores, query))
						




















