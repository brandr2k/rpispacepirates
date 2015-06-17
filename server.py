import socket
import sys
import string
 
#HOST = '192.168.137.1'
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 1701 # Arbitrary non-privileged port

#keypress=""
CLIENTLIST=dict()

#SHIPSTATS={"posx":0, "posy":0, "posz":0, "shieldstr":0,"shieldstatus":"down","dir":0, "name":"Hiro-Maru","faction":"pirates","wantedlevel":0,"money":0,"alertstatus":"green"}
SHIPSTATS={"shipid":0,"last_time":0, "posx":0, "posy":0, "posz":0,"h_speed":0,"v_speed":0,"pitch":0,"direction":0,"roll":0,"pitchrate":0,"yaw":0,"rollrate":0,"power_setting":0,"damage":0}
ABLETOMOVE=1
DOCKED=0
DIRECTIONCHANGE=0

def sendtoms(sendmsg,addr):  #send data to mainscreen
    print sendmsg
    s.sendto(sendmsg, addr)

def rendertext(sendmsg, sendaddr):  #send data to client
    print sendmsg, sendaddr
    s.sendto(sendmsg, sendaddr)
    
def sendcommand(cmd, thisconsole): ## Send commands to clients
    if thisconsole in CLIENTLIST:
        print "Sending CMD: ",cmd, " to : ", CLIENTLIST[thisconsole]
        s.sendto(cmd, CLIENTLIST[thisconsole])

def cmd_shutdown():
    for val in CLIENTLIST.values():
        print "Sending Shutdown to Client at ",val
        s.sendto("SHUTDOWN", val)


def drawhelm(addr):
    ## Clear Console Offline line
    rendertext(' ,CLEAR,5,1',addr)    
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
    

def drawweapons(addr):
    ## Clear Console Offline line
    rendertext(' ,CLEAR,5,1',addr)
    rendertext('=WEAPONS=,title,0,0',addr)
    rendertext('SHIP STATUS:,descript,0,2',addr)
    rendertext('RED ALERT,warn,0,3',addr)
    rendertext('SHIELDS,descript,1,2',addr)
    rendertext('OFF,warn,1,3',addr)
    rendertext('TARGET:,descript,2,0',addr)
    rendertext('X33,value,2,1',addr)
    rendertext('DISTANCE:,descript,2,2',addr)
    rendertext('1020k,value,2,3',addr)
    rendertext('STATUS:,descript,3,0',addr)
    rendertext('LOCKED,warn,3,1',addr)
    rendertext('WEAPON:,other,4,2',addr)
    rendertext('IN STOCK,other,4,3',addr)
    rendertext('EMP:,descript,5,2',addr)
    rendertext('2,value,5,3',addr)
    rendertext('MISSILES:,descript,6,2',addr)
    rendertext('14,value,6,3',addr)
    rendertext('BEAM FREQ:,descript,7,0',addr)
    rendertext('A,info,7,1',addr)
    rendertext('TUBE 1:,descript,8,0',addr)
    rendertext('MISSILE,info,8,1',addr)
    rendertext('LOADED,warn,8,2',addr)
    rendertext('TUBE 2:,descript,9,0',addr)
    rendertext('EMP,info,9,1',addr)
    rendertext('LOADED,warn,9,2',addr)
    rendertext('TUBE 3:,descript,10,0',addr)
    rendertext(' ,info,10,1',addr)
    rendertext('EMPTY,info,10,2',addr)

def processkey(station,key):
    if station=="helm":
        if key=="276": #left
            print "Left pressed ", station
            if ABLETOMOVE!=0:
                updatedir(-1)
        elif key=="275": #right
            print "Right pressed ", station
            if ABLETOMOVE!=0:
                updatedir(1)
        elif key=="273": #up
            print "Up pressed ", station
        elif key=="274": #down
            print "Down pressed ", station
        elif key=="32": #space
            print "space pressed ", station
        elif key=="49": #1
            print "1 pressed ", station
        elif key=="50": #2
            print "2 pressed ", station
        elif key=="51": #3
            print "3 pressed ", station
        elif key=="52": #4
            print "4 pressed ", station
        elif key=="113": #q
            print "q pressed ", station
        elif key=="119": #w
            print "w pressed ", station
        elif key=="101": #e
            print "e pressed ", station
        elif key=="114": #r
            print "r pressed ", station
        else:
            print key

def updatedir(direction):
    global SHIPSTATS
    shipdir=int(SHIPSTATS["dir"])
    currentdirection = (shipdir + direction) % 360
    dir = '%03d' % currentdirection ## Padding
    print "Direction now: ",dir
    SHIPSTATS["dir"]=currentdirection
    sendtext="%s,active,2,1" % (dir)
    addr=CLIENTLIST["HELM"]
    print "Sending to HELM", sendtext, addr
    rendertext(sendtext,addr)
 
def updateshipname(name):
   print 'Update shipname here'
    
    
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
        else:
            rendertext("OK",addr)
        print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
        CLIENT="NULL"
        if data=="CONNECT-MAINSCREEN":
            CLIENT="MAINSCREEN"
            if CLIENTLIST.has_key("MAINSCREEN"):
                print "MAINSCREEN already here"
            else:
                CLIENTLIST["MAINSCREEN"]=addr    
        elif data=="CONNECT-HELM":
            CLIENT="HELM"
            print "Sending screen setup data.."
            drawhelm(addr)
            print "Done sending screen setup data"
            if CLIENTLIST.has_key("HELM"):
                print "HELM already here"
            else:
                CLIENTLIST["HELM"]=addr
        elif data=="CONNECT-WEAPONS":
                        CLIENT="WEAPONS"
                        print "Sending screen setup data.."
                        drawweapons(addr)
                        print "Done sending screen setup data"
                        if CLIENTLIST.has_key("WEAPONS"):
                                print "WEAPONS already here"
                        else:
                                CLIENTLIST["WEAPONS"]=addr
        elif 'HELM-KEY_' in data:
            keypress=data.strip('HELM-KEY_')
            print "key recv from helm: ",keypress
            ## Send keys to mainscreen
            #sendtoms(keypress,CLIENTLIST["MAINSCREEN"])
            processkey("helm",keypress)
        elif 'sendtoall_' in data:
            gmdata=data.strip('sendtoall_')
            print "Sending to every screen; ", gmdata
            rendertext(gmdata+',title,0,0', CLIENTLIST["HELM"])
        elif 'cmd_' in data:
            mycmd=data.split( )
            try:
                sendcommand(mycmd[0],mycmd[1])
            except IndexError:
                print "Incomplete command"
            
        elif data=="echo":
            rendertext(data, sendaddr)
        else :
            print "unreconized data: ",data
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
s.close()
