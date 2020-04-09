Description:

	This script parses data from NetApp Cloud Insight on powered off VM servers and their powered off duration in days

Requirements:

	* python 3.8
	* python pymongo
	* python prettytable
	* Mongodb instance
		- If you don't have a mongodb instance make below change to code, to directly print update on screen
			- Uncomment: #prnt_table(RptDic)
			- Comment: update_db(RptDic)