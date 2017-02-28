import sqlite3
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import time
import math
import sys



if len(sys.argv) != 2:
	print("Expected 2 system arguments in the format: create_index.py indexDataDirectory")
	quit()

def remakeTable(conn):
	'''
	Paramaters: 
		- conn: sqlite3 database connection
	Drops table LISTINGS in the sqlite3 database if it exists and then (re)create it.
	'''
	stmt = "DROP TABLE IF EXISTS LISTINGS"
	conn.execute(stmt)


	stmt = 	"""
			CREATE TABLE LISTINGS (
				TERM 		VARCHAR(100),
				DOCID		VARCHAR(20),
				TF			INT,
				POSITIONS 	VARCHAR(200),
				IDF			INT,
				TF_IDF		INT)
			"""
	conn.execute(stmt)

def testTf(postings):
	for term in postings.keys():
		for x in range(1,len(postings[term])):
			positions = postings[term][x][2]
			tf = len(positions.split(','))
			if tf != int(postings[term][x][1]):
				doc = postings[term][x][0]
				print("The tf value is wrong for term " + term + " and doc " + doc)
				print(postings[term][x])

def testIdf(postings):
	for term in postings.keys():
		idf = postings[term][0]
		if idf != len(postings[term]) - 1:
			print("The idf is incorrect for term: " + term)
			print(postings[term])


def load_document_terms(directory):
	'''
	Parameters: 
		- dbName: String name of the database for the index to be stored in
		- directors: String name of the directory where the raw data is stored 
	'''
	conn = sqlite3.connect('a1.sql')

	#create the table in the database
	remakeTable(conn)

	#change directory to the directory of the raw data
	os.chdir(os.getcwd() + directory)
	start_time = time.time()


	fileNames = list(os.listdir(os.getcwd()))
	N = len(fileNames)
	wordPositions = dict()
	postings = dict()

	#wordPositions stores a dictionary in the format {term: positions} and will be rewritten for each doc
	#postings will store a dictionary in format {term: [idf, [docid, tf, positions], [docid, tf, positions]]}


	
	for fileName in fileNames:
		position = 0
		wordPositions = dict()
		File = open(fileName, 'r')

		#for every line in the file
		for line in File.readlines():
			#tokenize each line and lower each token
			tokens = word_tokenize(line)
			for x in range(len(tokens)):
				tokens[x] = tokens[x].lower()


			for t in tokens:
				position += 1
				#filter out tokens that are only punctuation or extra punctuation cases
				if t not in string.punctuation and t not in ("'s", "''", '""', "``"):
					if t not in wordPositions.keys():
						wordPositions[t.lower()] = str(position)
					else:
						wordPositions[t.lower()] += ","+str(position)
					

		#docID = fileName.split('.')[0]
		docID = fileName.split('_')[1]

		#populate the postings dictionary with the postings in the doc
		for key in wordPositions.keys():
			tf = len(wordPositions[key].split(','))
			postings.setdefault(key, [0])
			postings[key][0] += 1
			postings[key].append([docID, tf, wordPositions[key]])

	'''
	These testing functions will test the correctness of the Idf and Tf values stored in the postings dictionary
	'''
	testIdf(postings)
	testTf(postings)


	#calculate the df, idf and tf_idf from the data in postings dictionary and insert the data
	#the database
	for key in postings.keys():
		df = postings[key][0]
		idf = max(math.log10(N/df),0)
		for x in range(1, len(postings[key])):
			tf_idf = idf * postings[key][x][1]
			p = (key, postings[key][x][0], postings[key][x][1], postings[key][x][2], idf, tf_idf, )
			conn.execute("INSERT INTO LISTINGS VALUES(?,?,?,?,?,?)", p)
	

	#display the time it took to create the index
	print("Time:" + str((time.time()-start_time)/60) + " s")

	conn.commit()
	conn.close()





if __name__ == "__main__":
	directory = "/" + sys.argv[1]

	load_document_terms(directory)


