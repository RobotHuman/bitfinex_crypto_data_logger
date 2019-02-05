#This script will record all transactions that happen on bitfinex for a given trading pair along with a snapshot of the order book
#and store it all in a mongodb database.


import pymongo 
import urllib2
import simplejson
import time
from datetime import datetime
from colorama import Fore, Back, Style, init

trading_pair = 'btcusd'

#any pair available on bitfinex can be entered above

init()
mongo = pymongo.Connection() 
mongo_db = mongo['NAME OF YOUR DATABASE']
mongo_collection = mongo_db['my_collection']


def DBme(transactions, book, time):
  	#takes transaction and book data and a timestamp and enters it into the database
  
	insert_id = mongo_collection.insert({     'ide':'ide',
	'my_time': time,     
	'transactions': transactions,  
	'book': book })

def SimpleJason(url): 
	#Jason, such a simple man
	#SimpleJason simplifies simplejson
	#it takes a url and submits a json request and returns the results

	req = urllib2.Request(url)
	opener = urllib2.build_opener()
	f = opener.open(req, timeout = 10)
	return simplejson.load(f)#f.read()

def Book(trading_pair):
	#grabs order book data for a given trading pair
	try:
		data = SimpleJason("https://api.bitfinex.com/v1/book/" + trading_pair)
	except:
		data = {}
	return data

def Transactions(trading_pair):
	#grabs transaction data for a given trading pair
	try:
		data = SimpleJason("https://api.bitfinex.com/v1/trades/"+ trading_pair)
	except:
		data = []
	return data


def Filter(transactions, previoustransactions):
	#takes current transaction data and the previous transaction data and it
 	#eliminates transactions that were in the previous transaction data so 
 	#no transactions appear more than once in the database.  It returns a
 	#filtered dictionary of transactions.
  

	filtered =[]
	for i in range(len(transactions)):
		if(i != 0 and len(previoustransactions) > 0):
			if(transactions[i] == previoustransactions[0]):
				x = i
				while(x>=0):
					filtered.append(transactions[x])
					x=x-1
					
	previoustransactions = transactions
	return filtered, previoustransactions



###### catch data that might have been missed after a crash
book = Book(trading_pair)
previoustransactions = Transactions(trading_pair)
time_now = datetime.now()
DBme(previoustransactions,book, time_now)



#main loop

while(True):
	book = Book(trading_pair)
	transactions = Transactions(trading_pair)
	time_now = datetime.now()
	filtered, previoustransactions = Filter(transactions, previoustransactions)
	
	for x in filtered:
		x['mytime'] = time_now
		if x['type'] == 'buy':
			print Back.GREEN + 'price: ', x['price'], 'amount: ',x['amount'], ' ', time_now.hour, ':', time_now.minute,":",time_now.second,' ' + Style.RESET_ALL
		if x['type'] == 'sell':
			print Back.RED + 'price: ', x['price'], 'amount: ',x['amount'], ' ', time_now.hour, ':', time_now.minute,":",time_now.second,' ' + Style.RESET_ALL
		Style.RESET_ALL
	
	DBme(filtered,book, time_now)
	time.sleep(5)

mongo_documents = mongo_collection.find({     'ide': 'ide'}) 
for this_document in mongo_documents:     
	print this_document
