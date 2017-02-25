import sqlite3
import os
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import string
import time
import math

conn = sqlite3.connect('movies.sql')
stmt = "DROP TABLE IF EXISTS TERMS"
conn.execute(stmt)
stmt = "DROP TABLE IF EXISTS LISTINGS"
conn.execute(stmt)
stmt = "DROP TABLE IF EXISTS DOCUMENTS"
conn.execute(stmt)

stmt = 	"""
		CREATE TABLE TERMS (
			TERM 	VARCHAR(100),
			PRIMARY KEY (TERM) ON CONFLICT IGNORE
		)
		"""
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




def load_document_names():
	os.chdir(os.getcwd() + "/cmput397_2k_movies")
	print(os.getcwd())
	start_time = time.time()

	fileNames = list(os.listdir(os.getcwd()))
	N = len(fileNames)
	wordPositions = dict()
	postings = dict()

	
	
	for fileName in fileNames:
		position = 0
		wordPositions = dict()
		File = open(fileName, 'r')
		for line in File.readlines():
			tokens = word_tokenize(line)
			for t in tokens:
				if t not in stopwords.words('english') and t not in string.punctuation and t not in ("'s", "''", '""', "``"):
					if t not in wordPositions.keys():
						wordPositions[t.lower()] = str(position)
					else:
						wordPositions[t.lower()] += ","+str(position)
					position += 1

		docID = fileName
		for key in wordPositions.keys():
			tf = len(wordPositions[key].split(','))
			postings.setdefault(key, [0])
			postings[key][0] += tf
			postings[key].append([docID, tf, wordPositions[key]])

#term: [idf, [docid, tf, postings], [docid, tf, postings]]

	for key in postings.keys():
		df = postings[key][0]
		idf = max(math.log10(N/df),0)
		for x in range(1, len(postings[key])):
			p = (key, postings[key][x][0], postings[key][x][1], postings[key][x][2], idf, 0, )
			conn.execute("INSERT INTO LISTINGS VALUES(?,?,?,?,?,?)", p)
	

	print("Time:" + str((time.time()-start_time)/60))



if __name__ == "__main__":
	load_document_names()
	print("Hola Senor")

conn.commit()
conn.close()