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
TMPCONSOLE = sys.argv[2].upper() if len(sys.argv) >= 3 else 'HELM'
if TMPCONSOLE in CONSOLELIST:
    CONSOLE=TMPCONSOLE.upper()
else:
    print "CONSOLE Not Found"
    CONSOLE="HELM"
print "Console: ",CONSOLE

debug=1  #print to screen for debugging

## screen setup
SCREENRES=(640, 480)

DEFAULTFONT='assets/fonts/leaguegothic-regular-webfont.ttf'
DEFAULTFONTSIZE=42
DEFAULTFONTPAD=DEFAULTFONTSIZE
##color for fonts
COLORTITLE=(128,0,0)
COLORDESCRIPT=(255,255,255)
COLORVALUE=(0,0,128) #(0,0,0)
##color for alerts
COLORALERTRED=(255,0,0)
COLORALERTYELLOW=(255,255,0)
COLORALERTBLUE=(0,0,255)
COLORALERTYELLOW=(128,128,0)
##color for background
COLORDEFAULTBACK=(0,0,0)
COLORDEFAULTVALUEBACK=(26,26,26)
##color for boxes
COLORON=(0,0,255)
COLOROFF=(128,128,0)
COLORACTIVE=(0,0,255)
COLORDANGER=(255,0,0)
COLORINFO=(153,153,153)
COLOROTHER=(255,102,0)
COLORSELECTED=(128,128,0)

##Boxes
MARGIN=5

##random check variables
DRAWN=0

SVRCONN=0
count=0


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

def drawscreen():
    ## render to screen
    screen.blit(background, (0, 0))
    pygame.display.flip()
    
def rendertext(text,type,line,col):
    ## Display text to screen
    print "Rendering screen"
    col=int(col)
    line=int(line)
    text=str(text)
    type=str(type)
    if debug: print text+" | "+type+" | "+ str(line)+" | "+str(col)
    font = pygame.font.Font(DEFAULTFONT, DEFAULTFONTSIZE)    
    bg=0
    if type=="title":
        COLOR=COLORTITLE
    elif type=="descript":
        COLOR=COLORDESCRIPT
    elif type=="value":
        COLOR=COLORVALUE
        bg=1
    elif type=="warn":
        COLOR=COLORDANGER
        bg=1
    elif type=="info":
        COLOR=COLORINFO
        bg=1
    elif type=="active":
        COLOR=COLORON
        bg=1
    elif type=="CLEAR":
        COLOR=COLORDANGER
        background.fill(COLORDEFAULTBACK)
    else:
        COLOR=COLOROTHER
    if line==0:
        myline=0
    else:
        myline=line*DEFAULTFONTPAD
    if col==0:
        mycol=col+5
    else:
        mycol=(158+5)*col
    mypos=(mycol,myline)
    pygame.draw.rect(background,COLORDEFAULTBACK,(mycol,myline,155,DEFAULTFONTSIZE),0)
    if bg==1:
        pygame.draw.rect(background,COLORDEFAULTVALUEBACK,(mycol,myline,155,DEFAULTFONTSIZE),0)
    mytext=font.render(text, 1,COLOR)
    textpos =mytext.get_rect()
    background.blit(mytext, mypos)
    drawscreen()


def main():
        ## OS Detection to check the video system
        thisplatform=platform.system()
        if thisplatform=="Linux":
            print "Linux Yay!"
            os.putenv('SDL_FBDEV', '/dev/fb0')
            os.putenv('SDL_VIDEODRIVER', 'fbcon')
            os.putenv('SDL_NOMOUSE', '1')
        else:
            print "Not Linux, BOO!"
            
        pygame.init()
        
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        print "Framebuffer size: %d x %d" % (size[0], size[1])

        pygame.display.set_caption('Space Pi-Rates')
    
        ##We're running this without a mouse, so disable mouse pointer
        pygame.mouse.set_visible(False)

        ## Fill background
        global background
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill(COLORDEFAULTBACK)
    
        ## Blit everything to the screen
        drawscreen()
        DRAWN=1
        

def setonline():
    ## Clear offline screen
    #rendertext("","CLEAR",5,1)    
    background.fill(COLORDEFAULTBACK)
    drawscreen()
    print "Online"

def setoffline():
    ## Clear Screen and put offline message on screen
    background.fill(COLORDEFAULTBACK)
    rendertext("CONSOLE OFFLINE","CLEAR",5,1)
    
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

def listenerloop(soc):  ##Threading this due to hangups between pygame listening for events and listening for incoming data from network
    ## Prints don't work here, need to do something to show that it's working.
    setonline() ## Clear offline message
    while 1:
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
                    rendertext(text, type, line,col)
            else:
                if debug: print "No reply"  ##Printing Doesn't work
        
def eventloop():
    setoffline() #Set console offline screen, incase we can't connect to server
    ## Event loop
    #startnet()
    #mythread=thread.start_new_thread(target=listenerloop, (s,))  ## doesn't work - keeping for prosperity
    print "Starting Thread..."
    threading.Thread(target=listenerloop, args=(s,)).start()   ##working (at the moment)
    print "Server Connection status =", SVRCONN
    print "Thread Started"
    KEYCOUNT=0
    while 1:    
        for event in pygame.event.get():
            ##Quit
            if event.type == QUIT:
                print "Exiting"
                sendtoserver("DISCONNECT-"+CONSOLE);
                os.exit("Exiting")
            ## Key Down
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sendtoserver("DISCONNECT-"+CONSOLE);
                    return
                else:
                    print "key pressed %s" % (event.key)
                    if debug: rendertext(str(event.key),"descript",0,3)
                    keypress=CONSOLE+"-KEY_"+str(event.key)
                    #sendtoserver(event.key)
                    KEYCOUNT=KEYCOUNT + 1
                    sendtoserver(keypress)
                drawscreen()
                print KEYCOUNT
        #if debug: print "end running event loop"
        print "."
        time.sleep(0.1)
screen = pygame.display.set_mode(SCREENRES)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print "Creating socket..."
    SVRCONN=1
    sendtoserver("CONNECT-"+CONSOLE)
except socket.error:
    rendertext("OFFLINE","CLEAR",5,1)
    print 'Failed to create socket'
    SVRCONN=2


if __name__ == '__main__': 
    main()
    eventloop()

