import sys
sys.path.append("../")
import socket
from Storage import Storage
import sqlite3 as db
import IP
import hashlib      # library for sha1 hashing
import variables
curr_port = variables.persistence_port

def start_listening():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host = socket.gethostname()               
	ip_ob = IP.IP()                           # Get the ip of the system (machine_ip for persistence)
	my_ip = ip_ob.get_my_ip()
	s.bind((my_ip,curr_port))                      #  select a port for binding
	s.listen(10)

	print "Ip of persistence is : ",my_ip
	stor = Storage()                          # database will be created only once

	print "Creating dummy table"
	#---------Dummy Table---------
	'''stor.add_new_server('10.0.0.9')
	server_id = hashlib.sha1('10.0.0.9').hexdigest()
	stor.add_id_server('10.0.0.9',server_id)
	#stor.add_load_server('172.31.1.1',4)
	stor.add_new_server('10.0.0.5')
	server_id = hashlib.sha1('10.0.0.5').hexdigest()
	stor.add_id_server('10.0.0.5',server_id)
	#stor.add_load_server('172.31.1.2',2)
	stor.add_new_server('10.0.0.7')
	server_id = hashlib.sha1('10.0.0.7').hexdigest()
	stor.add_id_server('10.0.0.7',server_id)
	#stor.add_load_server('172.31.1.3',8)
	stor.add_new_server('10.0.0.8')
	server_id = hashlib.sha1('10.0.0.8').hexdigest()
	stor.add_id_server('10.0.0.8',server_id)
	#stor.add_load_server('172.31.1.4',1)
	stor.add_new_server('10.0.0.1')
	server_id = hashlib.sha1('10.0.0.1').hexdigest()
	stor.add_id_server('10.0.0.1',server_id)
	#stor.add_load_server('172.31.1.5',3)
	stor.add_new_server('10.0.0.4')
	server_id = hashlib.sha1('10.0.0.4').hexdigest()
	stor.add_id_server('10.0.0.4',server_id)
	#stor.add_load_server('172.31.1.6',4)
	stor.add_new_server('10.0.0.3')
	server_id = hashlib.sha1('10.0.0.3').hexdigest()
	stor.add_id_server('10.0.0.3',server_id)
	#stor.add_load_server('172.31.1.7',4)
'''
	while True:

		conn, addr = s.accept()
		msg = conn.recv(1024)
		print msg
		new_ip = addr[0]                 # ip from the addr recieved after connection of master/server
		if msg.find("master") is not -1:
			if msg.find('1:JOIN') is not -1:
				try:
					A_server = stor.get_first_server(new_ip)
					stor.add_new_master(new_ip)     # new server added
					master_id = hashlib.sha1(new_ip).hexdigest()
					stor.add_id_master(new_ip,master_id) #adding id for the master
					conn.send(master_id +":"+A_server)
				except:
					print 'Error occured'
					conn.send('Master addition FAILED')				
			elif msg.find('2:HBEAT') is not -1:     
				try:
					stor.add_heartbeat_master(new_ip)      # updating the time when last ping came from the masters/servers
					conn.send('Master Hbeat UPDATED')
				except:
					print 'Error occured'
					conn.send('Master hbeat update FAILED')	
				pass
		elif msg.find("server") is not -1:
			if msg.find('1:JOIN') is not -1:
				try:
					status = stor.if_first_server()     # new server added
					if(str(status) is "0"):
						print "Adding the first server"
					else:		
						status = stor.get_first_server(new_ip)
					stor.add_new_server(new_ip)     # new server added
					status = str(status)
					server_id = hashlib.sha1(new_ip).hexdigest()        # nodeis from the server ip
					#server_id = str(server_id)
					server_id = stor.add_id_server(new_ip,server_id) #adding id for the server
					conn.send(server_id + ":" + status)                     # sending the nodeid to the server
				except:
					print 'Error occured'
					conn.send('Peer addition FAILED')				
			elif msg.find('2:HBEAT') is not -1:     
				try:
					stor.add_heartbeat_server(new_ip)      # updating the time when last ping came from the masters/servers
					conn.send('Peer hbeat UPDATED')
				except:
					print 'Error occured'
					conn.send('Peer Hbeat updation FAILED')	
			elif msg.find('IP_FROM_ID') is not -1:   
				id = msg[msg.rfind(':') + 1:]  
				try:
				#	print str(id)
					ip = stor.get_ip_from_nodeid(str(id))      # updating the time when last ping came from the masters/servers
					#print "ippppp ",ip
					conn.send(str(ip))
				except:
					print 'Error occured'
					conn.send('return of ip FAILED')	
			elif msg.find('2:LIST_OF_MASTERS') is not -1:     
				try:
					lis = stor.get_list_of_masters()      # updating the time when last ping came from the masters/servers
					conn.send(lis)
				except:
					print 'Error occured'
					conn.send('list of masters sending FAILED')	
				pass
		elif msg.find("client") is not -1:
			print "client detected"
			if msg.find('1:MASTER') is not -1:
				try:
					master_ip = stor.get_master()
					conn.send('Master ip:'+master_ip)
				except:
					print 'Error occured master ip'
					conn.send('Master allocation failed')
			elif msg.find('K-NEAREST') is not -1:
				filekey = msg[msg.rfind(':') + 1:]       #recieved  client_ip from the server
				try:
					server_ip = stor.get_k_nearest_server(filekey)
					conn.send(server_ip)
				except:
					print 'Error occured k nearest failed'
					conn.send('K nearest allocation failed')
			elif msg.find('2:SERVER1') is not -1:        # to get the server with least load
				try:
					server_ip = stor.get_server()
					conn.send(server_ip)
				except:
					print 'Error : get server failed'
					conn.send('get server failed')
			elif msg.find('2:SERVER2') is not -1:
				try:
					server_ip = stor.get_server()
					key = stor.get_filekey()
					conn.send(server_ip+":"+key)
				except:
					print 'server allocation failed'
					conn.send('get filekey allocation failed')
				pass


if __name__ == "__main__":

	start_listening()

