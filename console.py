import pygame
from pygame.locals import *
import os
import math
import platform
import socket   #for sockets
import sys  #for exit


## networking - connect to this host
HOST="192.168.1.4"
PORT=1701
CONSOLE="HELM"

debug=0  #print to screen for debugging

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



clock=pygame.time.Clock()


def rendertext(text,type,line,col):
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

def sendtoserver(msg):
	msg=str(msg)
	try :
		#Set the whole string
		s.sendto(msg, (HOST, PORT))
        
		# receive data from client (data, addr)
		d = s.recvfrom(1024)
		reply = d[0]
		addr = d[1]
		if debug: print 'Server reply : ' + reply
	except socket.error, msg:
		print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	


def main():
	videocheck=2
	#OS Detection to check the video system
	thisplatform=platform.system()
	if thisplatform=="Linux":
		print "Linux Yay!"
		os.putenv('SDL_FBDEV', '/dev/fb0')
		os.putenv('SDL_VIDEODRIVER', 'fbcon')
		os.putenv('SDL_NOMOUSE', '1')
		videocheck=0  #temp
		#videocheck=1
		
	else:
		print "Not Linux, BOO!"
		videocheck=0
	
	
	
	if videocheck==1:
		##from https://learn.adafruit.com/pi-video-output-using-pygame/pointing-pygame-to-the-framebuffer
		disp_no = os.getenv("DISPLAY")
		if disp_no:
			print "I'm running under X display = {0}".format(disp_no)
        
		## Check which frame buffer drivers are available
		## Start with fbcon since directfb hangs with composite output
		drivers = ['fbcon', 'directfb', 'svgalib']
		found = False
		for driver in drivers:
			print "Trying Driver: %s" % (driver)
			## Make sure that SDL_VIDEODRIVER is set
			if not os.getenv('SDL_VIDEODRIVER'):
				os.putenv('SDL_VIDEODRIVER', driver)
			try:
				pygame.init()
			except pygame.error:
				print 'Driver: {0} failed.'.format(driver)
				continue
			found = True
			break
		
		if not found:
			raise Exception('No suitable video driver found!')
	##---
	else: 
		pygame.init()
		
	##---
	size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
	print "Framebuffer size: %d x %d" % (size[0], size[1])
	#screen = pygame.display.set_mode(size, pygame.FULLSCREEN)	
	#screen = pygame.display.set_mode(size, pygame.FULLSCREEN)	
	##End Adafruit
	
	#screen = pygame.display.set_mode(SCREENRES)
	pygame.display.set_caption('Space Pi-Rates')
	
	##We're running this without a mouse, so disabele mouse pointer
	pygame.mouse.set_visible(False)
	

	## Fill background
	global background
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill(COLORDEFAULTBACK)


	## Render Text
	##30 Chars Wide - MAX?
	rendertext("="+ CONSOLE +"=","title",0,0)
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
	rendertext("DOWN","",4,3)
	
	rendertext("TARGET DIR:","descript",9,0)
	rendertext("208","info",9,1)
	rendertext("TARGET DIST:","descript",9,2)
	rendertext("1201","info",9,3)
	rendertext("MAIN VIEWER:","descript",10,1)
	rendertext("FRONT","info",10,2)
	
	#rendertext("WWWWWWWWWMWWWWWWWWWMWWWWWWWWWMWWWWWWWWWMWWWWWWWWWM","descript",10)
        

	## Blit everything to the screen
	screen.blit(background, (0, 0))
	pygame.display.flip()

	## Event loop
	while 1:
					
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					sendtoserver("DISCONNECT|HELM");
					return
				elif event.key == K_1:
					#send key
					print "key pressed %s" % (event.key)
					#sendtoserver(event.key)
					if debug: rendertext("1","descript",0,3)
				elif event.key == K_2:
					#send key
					print "key pressed %s" % (event.key)
					#sendtoserver(event.key)
					if debug: rendertext("2","descript",0,3)
				elif event.key == K_3:
					#send key
					print "key pressed %s" % (event.key)
					#sendtoserver(event.key)
					if debug: rendertext("3","descript",0,3)
				elif event.key == K_4:
					#send key
					print "key pressed %s" % (event.key)
					#sendtoserver(event.key)
					if debug: rendertext("4","descript",0,3)
				elif event.key == K_5:
					#send key
					print "key pressed %s" % (event.key)
					#sendtoserver(event.key)
					if debug: rendertext("5","descript",0,3)
				elif event.key == K_UP:
					#send key
					print "key pressed %s" % (event.key)
					#sendtoserver(event.key)
					if debug: rendertext("UP","descript",0,3)
				elif event.key == K_DOWN:
					#send key
					print "key pressed %s" % (event.key)
					#sendtoserver(event.key)
					if debug: rendertext("DOWN","descript",0,3)
				elif event.key == K_LEFT:
					#send key
					print "key pressed %s" % (event.key)
					#sendtoserver(event.key)
					if debug: rendertext("LEFT","descript",0,3)
				elif event.key == K_RIGHT:
					#send key
					print "key pressed %s" % (event.key)
					#sendtoserver(event.key)
					if debug: rendertext("RIGHT","descript",0,3)
				else:
					print "other key pressed %s" % (event.key)
					#sendtoserver(event.key)
					if debug: rendertext("OTHER","descript",0,3)
					#do nothing
				sendtoserver(event.key)
		screen.blit(background, (0, 0))
		pygame.display.flip()
		
		
clock.tick(20)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print "Creating socket..."
    sendtoserver("CONNECT|HELM");
except socket.error:
    print 'Failed to create socket'
    
 
screen = pygame.display.set_mode(SCREENRES)
if __name__ == '__main__': main()
