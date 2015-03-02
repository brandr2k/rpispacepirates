import pygame
from pygame.locals import *
import os
import math
import platform
import socket   #for sockets
import sys  #for exit
import time
from thread import *
from queue import Queue

## networking - connect to this host
HOST="192.168.137.1"
PORT=1701
CONSOLE="HELM"

debug=1  #print to screen for debugging

## screen setup
SCREENRES=(640, 480)

DEFAULTFONT='assets/leaguegothic-regular-webfont.ttf'
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
DRAWN="0"
s=0
count=0
#clock=pygame.time.Clock()

class serverdata():
	def startnet(bogus):
		#enable networking
		try:
			global s
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			print "Creating socket..."
		except socket.error:
			rendertext("OFFLINE","CLEAR",5,1)
			print 'Failed to create socket'
		# receive data from client (data, addr)
		

		while 1:		
			#print "got data"
			d = s.recvfrom(1024)
			reply = d[0]
			addr = d[1]
			if debug: print 'Server reply : ' + reply
			if reply=="OK" or reply=="HELLO":
				if debug: print reply
			else:
				#split out list of strings for building GUI
				text, type, line,col=reply.split(',')
				main.rendertext(text, type, line,col)
			
			
	def sendtoserver(msg):
		msg=str(msg)
		try :
			#Set the whole string
			
			s.sendto(msg, (HOST, PORT))
		except socket.error, msg:
			if debug: print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			if DRAWN=="1":
				rendertext("CONSOLE OFFLINE","CLEAR",5,1)
				#drawscreen()
			else:
				print "CONSOLE OFFLINE"
				print "retrying in 5 seconds"
				time.sleep(5)
				serverconnect()    



def drawscreen():
	## render to screen
	global count
	screen.blit(background, (0, 0))
	pygame.display.flip()
	#count=count+1
	#print count

def rendertext(text,type,line,col):
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
		#OS Detection to check the video system
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
	
		##We're running this without a mouse, so disabele mouse pointer
		pygame.mouse.set_visible(False)

		## Fill background
		global background
		background = pygame.Surface(screen.get_size())
		background = background.convert()
		background.fill(COLORDEFAULTBACK)
	
		## Blit everything to the screen
		drawscreen()
		DRAWN=1
		
		q=Queue()
		#Start Treads
		t1 = Thread(target=serverdata.startnet,args=(s,))
		t1.start()
		## Tell server who we are
		serverdata.sendtoserver("CONNECT-"+CONSOLE)
		
def eventloop():
	## Event loop
	
	while 1:	
			
		for event in pygame.event.get():
			#print "received event"
			if event.type == QUIT:
				sendtoserver("DISCONNECT-"+CONSOLE);
				return
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					sendtoserver("DISCONNECT-"+CONSOLE);
					return
				else:
					print "key pressed %s" % (event.key)
					if debug: rendertext(str(event.key),"descript",0,3)
					sendtoserver(event.key)
		drawscreen()
	
	
screen = pygame.display.set_mode(SCREENRES)	


 

if __name__ == '__main__': 
	main()
	eventloop()

