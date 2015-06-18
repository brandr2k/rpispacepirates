import pygame
from pygame.locals import *
import os
import math
import platform
import socket   #for sockets
import sys  #for exit
import time

import select
#import thread
import threading

#from thread import *
from Queue import *


## networking - connect to this host
PORT=1701

## HOST Select from Command Lioe
HOST= sys.argv[1] if len(sys.argv) >= 7 else '127.0.0.1'

CONSOLELIST=["HELM","WEAPONS","ENGINEERING","COMMS","SENSORS","DAMAGECONTROL","CAPTAIN","STATUS"]

## Station Select from Command Line
TMPCONSOLE = sys.argv[2].upper() if len(sys.argv) >= 3 else 'MAINSCREEN'
if TMPCONSOLE in CONSOLELIST:
    CONSOLE=TMPCONSOLE.upper()
else:
    print "CONSOLE Not Found"
    CONSOLE="MAINSCREEN"
print "Console: ",CONSOLE

SVRCONN=0
count=0

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


def main():
        ## OS Detection to check the video system
        thisplatform=platform.system()
        if thisplatform=="Linux":
            print "Linux Yay!"

        else:
            print "Not Linux, BOO!"
            
        
def defprocessdata(input):
  
        
        
def checkcmd(cmd):
    ##check cmd and run
    indata = cmd.split( )
    if indata[0]=="cmd_SHUTDOWN":
        os._exit(1)
    elif indata[0]=="cmd_offline":
        setoffline()
    elif indata[0]=="cmd_online":
        setonline()
    else:
        print "Unknown command"
        

def listenerloop(soc, stop_event):  ##Threading this due to hangups between pygame listening for events and listening for incoming data from network
    ## Prints don't work here, need to do something to show that it's working.
    setonline() ## Clear offline message
    while(not stop_event.is_set()):
        ##Network listener       
        if SVRCONN==1:
            #global reply
            reply, addr = soc.recvfrom(1024) #(1024)
            if reply:
                if debug: print 'Server reply : ' + reply
                if reply=="OK" or reply=="HELLO":
                    ## We're connected
                    if debug: print reply #Printing doesn't work
                elif "cmd_" in reply:
                    checkcmd(reply)
                else:
                    ## split out list of strings for building GUI
                    text, type, line,col=reply.split(',')
                    #rendertext(text, type, line,col)
                    processnetdata(reply)
            else:
                if debug: print "No reply"  ##Printing Doesn't work
        
def eventloop():
    setoffline() #Set console offline screen, incase we can't connect to server
    ## Event loop
    #startnet()
    #mythread=thread.start_new_thread(target=listenerloop, (s,))  ## doesn't work - keeping for prosperity
    print "Starting Thread..."
    mythread_stop=threading.Event()
    mythread=threading.Thread(target=listenerloop, args=(s,mythread_stop)).start()   ##working (at the moment)
    print "Server Connection status =", SVRCONN
    print "Thread Started"
    KEYCOUNT=0
    while 1:    
        for event in pygame.event.get():
            ##Quit
            if event.type == QUIT:
                print "Exiting"
                sendtoserver("DISCONNECT-"+CONSOLE)
                mythread_stop.set()
                os.exit("Exiting")
            ## Key Down
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sendtoserver("DISCONNECT-"+CONSOLE)
                    mythread_stop.set()
                    return
                elif  event.key == K_F12:  
                    sendtoserver("DISCONNECT-"+CONSOLE)
                    mythread_stop.set()
                    mythread=threading.Thread(target=listenerloop, args=(s,)).start()
                    return
                else:
                    print "key pressed %s" % (event.key)
                    if debug: rendertext(str(event.key),"descript",0,3)
                    keypress=CONSOLE+"-KEY_"+str(event.key)
                    #sendtoserver(event.key)
                    KEYCOUNT=KEYCOUNT + 1
                    sendtoserver(keypress)
                #drawscreen()
                print KEYCOUNT
        #if debug: print "end running event loop"
        if debug: print "."
        time.sleep(0.1)
        
def setonline():
  print("Online")

def setoffline():
  print("Offline")


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print "Creating socket..."
    SVRCONN=1
    sendtoserver("CONNECT-"+CONSOLE)
except socket.error:
    
    print 'Failed to create socket'
    SVRCONN=2


if __name__ == '__main__': 
    main()
    eventloop()