import socket
import sys
 
#HOST = '192.168.137.1'
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 1701 # Arbitrary non-privileged port

CLIENTLIST={}

def rendertext(sendmsg, sendaddr):  #send data to client
	print sendmsg
	s.sendto(sendmsg, sendaddr)
	

def drawhelm(addr):
	rendertext('=HELM=,title,0,0',addr)
	rendertext('ENERGY:,descript,1,2',addr)
	rendertext('1000,info,1,3',addr)
	rendertext('HEADING:,descript,2,0',addr)
	rendertext('000,active,2,1',addr)
	rendertext('IMPULSE:,descript,3,0',addr)
	rendertext('OFF,value,3,1',addr)
	rendertext('WARP:,descript,4,0',addr)
	rendertext('OFF,value,4,1',addr)
	
	rendertext('REVERSE:,descript,2,2',addr)
	rendertext('OFF,value,2,3',addr)
	rendertext('DOCKING:,descript,3,2',addr)
	rendertext('OFF,value,3,3',addr)
	rendertext('SHIELDS:,descript,4,2',addr)
	rendertext('DOWN,warn,4,3',addr)
	
	rendertext('TARGET DIR:,descript,9,0',addr)
	rendertext('208,info,9,1',addr)
	rendertext('TARGET DIST:,descript,9,2',addr)
	rendertext('1201,info,9,3',addr)
	rendertext('MAIN VIEWER:,descript,10,1',addr)
	rendertext('FRONT,info,10,2',addr)
	
 
# Datagram (udp) socket
try :
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print 'Socket created'
	
except socket.error, msg :
	print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()
 
 
# Bind socket to local host and port
try:
	s.bind((HOST, PORT))
	print "Listening on port %s ..." %  (PORT)
except socket.error , msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()
     
print 'Socket bind complete'
 
#now keep talking with the client
while 1:
	try:
		# receive data from client (data, addr)
		d = s.recvfrom(1024)
		data = d[0]
		addr = d[1]
		#print str(addr)
     
		if not data: 
			break
		print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
		CLIENT="NULL"
		if data=="CONNECT-HELM":
			CLIENT="HELM"
			print "Sending screen setup data.."
			drawhelm(addr)
			print "Done sending screen setup data"
			if CLIENTLIST.has_key("HELM"):
				print "HELM already here"
			else:
				CLIENTLIST["HELM"]=addr

	except (KeyboardInterrupt, SystemExit):
		sys.exit()
     
s.close()