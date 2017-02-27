#vs_query [index location] [k] [scores] [term_1] [term_2] ... [term_n]
import sqlite3
import sys

conn = sqlite3.connect(sys.argv[1])
k = int(sys.argv[2])
displayScores = sys.argv[3]
docScores = dict()
docLengths = dict()
terms = set()
query = list()


for x in range(4,len(sys.argv)):
	terms.add(sys.argv[x])
	query.append(sys.argv[x])


stmt = 	"""
		SELECT DOCID, TF_IDF, IDF FROM LISTINGS WHERE TERM = ?
		"""
for term in terms:
	p = (term, )
	curs = conn.execute(stmt, p)
	tf = query.count(term)
	for row in curs:
		docName = row[0]
		tf_idf = float(row[1])
		idf = float(row[2])
		query_tf_idf = tf * idf

		docScores.setdefault(docName, 0)
		docScores[docName] = docScores[docName] + (tf_idf * query_tf_idf)

		docLengths.setdefault(docName, [])
		docLengths[docName].append(tf_idf)

for doc in docLengths.keys():
	lengths = docLengths[doc]
	vectorLength = 0
	for l in lengths:
		vectorLength += l**2
	vectorLength = vectorLength**(1/2)
	docLengths[doc] = vectorLength


scores = list()
for doc in docScores.keys():
	if docLengths[doc] != 0:
		scores.append((doc, docScores[doc]/docLengths[doc]))

sortedScores = sorted(scores, key=lambda x: -x[1])

k = min(len(docScores.keys()), k)
msg = ""
for x in range(k):
	
	if displayScores.lower() == 'y':
		msg += "(" + sortedScores[x][0] + "," + str(sortedScores[x][1]) + ")" 
	elif displayScores.lower() == 'n':
		msg += sortedScores[x][0]
	if x != k-1:
		msg += ","

print(msg)
					




















