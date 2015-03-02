import socket
import sys
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 1701 # Arbitrary non-privileged port

def sendtoclient(sendmsg, sendaddr):
	s.sendto(sendmsg, sendaddr)
	
 
def drawhelm():
	sendtoclient('"=HELM=","title",0,0',)
	#rendertext("=ENGINEERING=","title",0,0)
	rendertext("ENERGY:","descript",1,2)
	rendertext("1000","info",1,3)
	rendertext("HEADING:","descript",2,0)
	rendertext("000","active",2,1)
	rendertext("IMPULSE:","descript",3,0)
	rendertext("OFF","value",3,1)
	rendertext("WARP:","descript",4,0)
	rendertext("OFF","value",4,1)
	
	rendertext("REVERSE:","descript",2,2)
	rendertext("OFF","value",2,3)
	rendertext("DOCKING:","descript",3,2)
	rendertext("OFF","value",3,3)
	rendertext("SHIELDS:","descript",4,2)
	rendertext("DOWN","warn",4,3)
	
	rendertext("TARGET DIR:","descript",9,0)
	rendertext("208","info",9,1)
	rendertext("TARGET DIST:","descript",9,2)
	rendertext("1201","info",9,3)
	rendertext("MAIN VIEWER:","descript",10,1)
	rendertext("FRONT","info",10,2)
 
 
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
		print str(addr)
     
		if not data: 
			break
		CLIENT="NULL"
		if data=="CONNECT|HELM":
			CLIENT="HELM"
		#reply = 'OK...' + data
		reply='OK'
		s.sendto(reply , addr)
		print 'Message[' + addr[0] + ':' + str(addr[1]) + '] ('+CLIENT+') - ' + data.strip()
	except (KeyboardInterrupt, SystemExit):
		sys.exit()
     
s.close()