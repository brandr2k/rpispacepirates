import socket   #for sockets
import sys  #for exit
	

## networking - connect to this host
HOST="127.0.0.1"
PORT=1701
CONSOLE="GAMEMASTER"

debug=1  #print to screen for debugging
	
def sendtoserver(msg):
	## Send messages to server
	msg=str(msg)
	try :
		#Set the whole string
		if debug: print "sending message"
		s.sendto(msg, (HOST, PORT))
	except socket.error, msg:
		if debug: print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		if DRAWN=="1":
			rendertext("CONSOLE OFFLINE","CLEAR",5,1)
			#drawscreen()
		else:
			print "CONSOLE OFFLINE"
			print "retrying in 5 seconds"
			#time.sleep(5)
			#serverconnect()    
	

def eventloop():  
	
	while 1:
		if debug: print "running network loop"
		#Network listener
		if SVRCONN==1:
			
			#global reply
			#print "loop: server is connected"
			reply, addr = s.recvfrom(1024) #(1024)
			print "."
			if reply:
				
				if debug: print 'Server reply : ' + reply
				if reply=="OK" or reply=="HELLO":
					if debug: print reply
				else:
					#split out list of strings for building GUI
					text, type, line,col=reply.split(',')
					sendtoserver("Hello");
					print "text"+text
			else:
				if debug: print "No reply"
		msg = raw_input('--> ')
		sendtoserver(msg)

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print "Creating socket..."
	SVRCONN=1
	sendtoserver("CONNECT-"+CONSOLE)
except socket.error:
	print 'Failed to create socket'
	SVRCONN=2


if __name__ == '__main__': 
	#main()
	eventloop()