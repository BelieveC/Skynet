import sqlite3 as db
import datetime, time
import random
import os
import hashlib
import ipaddress
from cachetools import LRUCache

CACHE = LRUCache(maxsize=10)

class Storage():

	def __init__(self):
		os.remove('master.db')              # to delete the already created database
		self.conn = db.connect('master.db')
		#self.start_nodeid = 1146            # start nodeid for peers
		#self.start_filekey = 1146
		self.cursor = self.conn.cursor()
		self.nodeids = [1146,2015,1040]
		self.node_ind = 0;
		self.fileids = [2014,1145,1041]
		self.file_ind = 0
		self.cursor.execute('CREATE TABLE master_servers (master_id ,ip, timestamp)')       # table for masters
		self.cursor.execute('CREATE TABLE peer_servers (server_id ,ip, timestamp, load)')   # table for servers


	def add_new_server(self, add_ip):
		query = 'SELECT COUNT(*) FROM peer_servers'                 # to get the number of rows present in table 
		rows = self.cursor.execute(query).fetchone()[0]
		#print "size :",rows
		try:
			query = 'INSERT INTO peer_servers (ip,load) VALUES (?,?)' 
			self.cursor.execute(query, (add_ip,0 ))
			self.conn.commit()                                     # to save changes
		except db.IntegrityError:
			self.add_heartbeat(add_ip)

	def if_first_server(self):
		query = 'SELECT COUNT(*) FROM peer_servers'                 # to get the number of rows present in table 
		rows = self.cursor.execute(query).fetchone()[0]
		return rows

	def add_heartbeat_server(self, add_ip):
		query = 'UPDATE peer_servers SET timestamp=? WHERE ip=?'
		self.cursor.execute(query, (time.time(), add_ip))
		self.conn.commit()
     
	def add_load_server(self, add_ip, load):                       # load is number of clients attached
		query = 'UPDATE peer_servers SET load=? WHERE ip=?'
		self.cursor.execute(query, (load, add_ip))
		self.conn.commit()
	
	def add_id_server(self, add_ip, server_id):                       # setting server_id to every server as unique identifier
		#query = 'SELECT COUNT(*) FROM peer_servers'                 # to get the number of rows present in table 
		#rows = self.cursor.execute(query).fetchone()[0]
		query = 'UPDATE peer_servers SET server_id=? WHERE ip=?'
		#self.cursor.execute(query, (server_id, add_ip))           # nodeid using hashlib
		self.cursor.execute(query, (self.nodeids[self.node_ind], add_ip))            # dummy nodeid
		#self.start_nodeid += 96
		self.node_ind += 1
		self.conn.commit()
		return str(self.nodeids[self.node_ind-1])
		#return str(self.start_nodeid - 96)

	def get_first_server(self,new_ip):
		query = 'SELECT ip FROM peer_servers'
		rows = self.cursor.execute(query).fetchall()
		diff = 100000000000000000000000000
		ans = ""
		new_ip = ipaddress.IPv4Address(unicode(new_ip))
		for ip in rows:
			iip = ip[0]
			ip = ipaddress.IPv4Address(unicode(ip[0]))
			new_diff = abs(int(new_ip) - int(ip))
			if(diff > new_diff):
				diff = new_diff
				ans = iip
		return ans

	def get_server(self):
		#print "getting master"
		query = 'SELECT ip FROM peer_servers ORDER BY load'                 # to get the number of rows present in table 
		rows = self.cursor.execute(query).fetchone()[0]
		#print rows
		return rows

	def get_list_of_masters(self):
		query = 'SELECT ip FROM master_servers'                 # to get the number of rows present in table 
		rows = self.cursor.execute(query).fetchall()
		new_list = ""
		for i in rows:
			new_list = new_list + " " + i[0]
		#print new_list
		return new_list

	def add_new_master(self, add_ip):
		try:
			query = 'INSERT INTO master_servers (ip) VALUES (?)' 
			self.cursor.execute(query, (add_ip, ))
			self.conn.commit()
			CACHE['master'] = add_ip                                    # to save changes
		except db.IntegrityError:
			self.add_heartbeat(add_ip)

	def add_heartbeat_master(self, add_ip):
		query = 'UPDATE master_servers SET timestamp=? WHERE ip=?'
		self.cursor.execute(query, (time.time(), add_ip))
		self.conn.commit()

	def add_id_master(self, add_ip, master_id):                       # setting master_id to every master as unique identifier
		query = 'SELECT COUNT(*) FROM master_servers'                 # to get the number of rows present in table 
		rows = self.cursor.execute(query).fetchone()[0]
		query = 'UPDATE master_servers SET master_id=? WHERE ip=?'
		self.cursor.execute(query, ("100", add_ip))
		self.conn.commit()

	def get_master(self):
		#print "getting master"
		try:
			if CACHE['master']:
				return CACHE['master']
		except:
			print "Cache not present"

		query = 'SELECT COUNT(*) FROM master_servers'                 # to get the number of rows present in table 
		rows = self.cursor.execute(query).fetchone()[0]
		query = 'SELECT ip from master_servers ORDER BY RANDOM() LIMIT 1'    # to get a random master from the persistence
		n = random.randint(0,4)
		ip = self.cursor.execute(query).fetchone()[0]
		return ip

	def get_ip_from_nodeid(self,nodeid):
		query = 'SELECT ip FROM peer_servers where server_id = ?'                 # to get the number of rows present in table 
		rows = self.cursor.execute(query,(int(nodeid),)).fetchone()[0]
		#print rows
		return rows

	def get_filekey(self):
		key = self.fileids[self.file_ind]
		self.file_ind += 1
		return str(key)

	def get_k_nearest_server(self,filekey):
		query = 'SELECT server_id,ip FROM peer_servers ORDER BY server_id'              # to get the number of rows present in table 
		rows = self.cursor.execute(query).fetchall()
		new_list = ""
		i = 0
		#print rows
		while(i<len(rows)):
			if(filekey>rows[i][0]):
				i += 1
			else:
				break

		if(i>=len(rows)):
			i -= 1

		return rows[i][1]		

		# for more than 1 nearest server
		'''print rows
		print i
		k = 2
		ind = i
		while(ind>=0 and k>0):
			new_list = new_list + " " + rows[ind][1]
			ind -= 1;
			k -= 1;
		
		ind = i+1
		k = 2
		while(ind<len(rows) and k>0):
			new_list = new_list + " " + rows[ind][1]
			ind += 1;
			k -= 1;
		'''
		#return new_list


	def clean(self):
		# must remove outdated entries
		pass
'''
stor = Storage()

print "Creating dummy table"
#---------Dummy Table---------
stor.add_new_server('172.17.14.23')
stor.add_id_server('172.17.14.23','1146')
stor.add_new_server('172.17.14.7')
stor.add_id_server('172.17.14.7','2015')
stor.add_new_server('172.17.14.2')
stor.add_id_server('172.17.14.2','1040')

print stor.get_k_nearest_server("2014")
'''