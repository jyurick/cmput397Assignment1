# cmput397Assignment1
This directory contains a group of python programs that are designed to create and perform
search operations on an inverted-index file stored in an sqlite3 database.

1. create_index.py:
*****************************************************************************************************
Execution: python3 create_index.py directoryName

In this case directoryName is the name of the directory which contains the text files that
are to be indexed. This program assumes this file is already in the current working directory. The
terms in this file are tokenized using the NLTK tokenizer which must be installed on the machine. 
The tokenization step also removes any standalone punctuation as well as a few other punctuation cases.
The tokenization step does not remove stopwords, this decision was made so that it is possible for 
stopwords to be included in the terms and phrases for the boolean_query program. It was also found that removing stopwords increased the time take to create the index. 

An sql file names 'a1.sql' will be made in the current working directory that contains a single table
name "LISTINGS". The time it took to create the index is also printed to the terminal.

Test functions:
The test functions testTf() and testIdf() were designed to test the correctness of the tf and idf
values stored in the postings dictionary before the data from the dictionaries is inputted into the 
sqlite3 database.

***PLEASE NOTE***: 
If the index is being created to be used with the test functions described in the different programs below, line 104 in this script needs to be uncommented and line 105 needs to be commented. This is because the document names are in different formats in the documents file and the cmput397_2k_movies file

2. print_index.py:
*****************************************************************************************************
Execution: python3 print_index.py a1.sql

This program will print out all terms in the index followed by the docids and positions that each 
term appears in. Terms are printed in alphabetical order in the format:
term1	doc2:1,5,6;doc2:5,8,9;doc4:6,7,8,9;

The numbers following each docID represents the position in that doc in which the term appears.

3. boolean_query.py
*****************************************************************************************************
Execution: python3 boolean_query.py a1.sql 'query'

This program will return the result of the query provided in 'query'. The query can take in terms, operators(OR, AND)
and phrases in the form of "term1 term2 term3". The result of this program is a sorted list of the docIDs of all 
documents which satisfy the query.

Test Functions:
Individual unit test functions are written to test each function in the program including:
testOrOperation(), testAndOperation(), testLookupPhrase(), testLookupPostings, testSimplifyQuery()

There is also a test function named testEverything() that will run all of the test functions above.
The test functions assume that the test are being run on an index database that is populated using 
the documents folder supplied in the original Assignment sample code. The tests in testSimplifyQuery()
run the same queries and expect the same results as were supplied in boolean_test_cases.txt

4. vs_query.py
*****************************************************************************************************
Execution: python3 vs_query.py a1.sql k scores term1 term2 ... termn
k: the amount of documents to be returned by the program. If there aren't k documents to be returned,
the program will return all documents available that didn't have a score of 0.

scores: expected to be 'y' if the user wants the scores and docIDs of each document printed in the result and 'n' if the user wants only the docIDs to be returned.

Test Functions:
The test function testCosineScore() tests results of different term queries. The test function assume that the test are being run on an index database that is populated using the documents folder supplied in the original Assignment sample code.


