#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
"""quite a complicated demo showing many features of pi3d as well as
communication between players using httpRequest (see rpi_json.sql and
rpi_json.php) json serialisation and threading.
"""

"""
Space Pi-Rates mainscreen
originally Dogfight.py from pi3d_demos

"""


import sys
import time, math, glob, random, threading, json

import uuid
MYID=uuid.uuid4()
refid=MYID.hex  ##Unique ship ID (removes dashes) (send to comms for debugging/noise info?)

import demo
import pi3d

if sys.version_info[0] == 3:
  from urllib import request as urllib_request
  from urllib import parse as urllib_parse
else:
  import urllib
  urllib_request = urllib
  urllib_parse = urllib

instdisplay=False   #display instruments/icon on screen

audio=True   #turn on sound

screenoverride=True

if screenoverride==True:
	#screenwidth=640
	#screenheight=480
	screenwidth=800
	screenheight=600
else:
	screenwidth=0
	screenheight=0
	


if audio==True:
	import pygame
	pygame.init()
	bgnoise = pygame.mixer.Sound('assets/sounds/brownnoise.ogg')
	beamsound = pygame.mixer.Sound('assets/sounds/slimeball.wav')
	clock = pygame.time.Clock()
	bgnoise.play()
	#beamsound.play()


#display, camera, shader
#DISPLAY = pi3d.Display.create(x=100, y=100, frames_per_second=30)  ##Use for debugging (not fullscreen)
#DISPLAY = pi3d.Display.create(x=0, y=0, frames_per_second=30) #default screen for Pi
#DISPLAY = pi3d.Display.create(0, 0, 640,480,32, frames_per_second=30,window_title='Space Pi-rates',mouse=False) ## For testing on desktop (set to 640x480)
DISPLAY = pi3d.Display.create(0, 0, screenwidth,screenheight,32, frames_per_second=30,window_title='Space Pi-rates',mouse=False) ## For testing on desktop (set to 640x480)

#a default camera is created automatically but we might need a 2nd 2D camera
#for displaying the instruments etc. Also, because the landscape is large
#we need to set the far plane to 10,000
CAMERA = pi3d.Camera(lens=(1.0, 10000.0, 55.0, 1.33)) #4:3 res
#CAMERA = pi3d.Camera(lens=(1.0, 10000.0, 55.0, 1.77)) #16:9 res
#CAMERA = pi3d.Camera(lens=(1.0, 10000.0, 55.0, 2.0))
CAMERA2D = pi3d.Camera(is_3d=False)

print("""===================================
== W increase power, S reduce power
== V view mode, C control mode
== B brakes
== X jumps to location of 1st enemy in list
== P Fires beams
== Q to turn left, E to turn right
== I to climb, K to desend
================================""")

SHADER = pi3d.Shader("uv_bump") #for objects to look 3D
FLATSH = pi3d.Shader("uv_flat") #for 'unlit' objects like the background

GRAVITY = 0.00001 # 9.8 #m/s**2
LD = 10 #10 #lift/drag ratio
DAMPING = 0.95 #reduce roll and pitch rate each update_variables
BOOSTER = 1.5 #extra manoevreability boost to defy 1st Low of Thermodynamics.
#load bullet images
BULLET_TEX = [] #list to hold Texture refs
iFiles = glob.glob(sys.path[0] + "/assets/textures/starship/bullet??.png") ### Replace with beams/missles
iFiles.sort() # order is vital to animation!
for f in iFiles:
  BULLET_TEX.append(pi3d.Texture(f))
DAMAGE_FACTOR = 50 #dived by distance of shoot()
NR_TM = 1.0 #check much less frequently until something comes back
FA_TM = 5.0
NR_DIST = 250   ## Near Distance?
FA_DIST = 1900  ## Firing distance? - Far Distance?
P_FACTOR = 0.001
I_FACTOR = 0.00001

#define Aeroplane class
class Aeroplane(object):
  def __init__(self, model, recalc_time, refid):
    self.refid = refid
    self.recalc_time = recalc_time #in theory use different values for enemy
    self.x, self.y, self. z = 0.0, 0.0, 0.0
    self.x_perr, self.y_perr, self.z_perr = 0.0, 0.0, 0.0
    self.x_ierr, self.y_ierr, self.z_ierr = 0.0, 0.0, 0.0
    self.d_err = 0.0
    self.v_speed, self.h_speed = 0.0, 0.0
    self.rollrate, self.pitchrate, self.yaw = 0.0, 0.0, 0.0
    self.direction, self.roll, self.pitch = 0.0, 0.0, 0.0
    self.max_roll, self.max_pitch = 65, 30 #limit rotations
    self.ailerons, self.elevator = 0.0, 0.0
    self.max_ailerons, self.max_elevator = 10.0, 10.0 #limit conrol surface movement
    self.VNE = 120 #max speed (Velocity Not to be Exceeded)
    self.mass = 300
    self.a_factor, self.e_factor = 10, 10
    self.roll_inrta, self.pitch_inrta = 100, 100
    self.max_power = 2000 #force units of thrust really
    self.lift_factor = 20.0 #randomly adjusted to give required performance!
    self.power_setting = 0.0
    self.throttle_step = 20
    self.last_time = time.time()
    self.last_pos_time = self.last_time
    self.del_time = None #difference in pi time for other aero c.f. main one
    self.rtime = 60
    self.nearest = None
    self.other_damage = 0.0 #done to nearest others since last json_load
    self.damage = 0.0 #done to this aeroplane by others
    #create the actual model
    self.model = pi3d.Model(file_string=model, camera=CAMERA)
    self.model.set_shader(SHADER)
    #create the bullets
    plane = pi3d.Plane(h=25, w=1)
    self.bullets = pi3d.MergeShape(camera=CAMERA)
    #the merge method does rotations 1st Z, 2nd X, 3rd Y for some reason
    #for multi axis rotations you need to figure it out by rotating a
    #sheet of paper in the air in front of you (angles counter clockwise)!
    

    """  ##Old beams/bullets
    self.bullets.merge([[plane, -2.0, 0.5, 8.0, 90,0,0, 1,1,1],
                        [plane, -2.0, 0.5, 8.0, 0,90,90, 1,1,1],
                        [plane, 2.0, 0.5, 8.0, 90,0,0, 1,1,1],
                        [plane, 2.0, 0.5, 8.0, 0,90,90, 1,1,1]])
    """
    self.bullets.merge([[plane, 0.0, 0.5, 8.0, 90,0,0, 1,1,1]]) ## fixed single beam
    self.num_b = len(BULLET_TEX)
    self.seq_b = self.num_b
    self.bullets.set_draw_details(FLATSH, [BULLET_TEX[0]])

  def set_ailerons(self, dx):
    self.ailerons = dx
    if abs(self.ailerons) > self.max_ailerons:
      self.ailerons = math.copysign(self.max_ailerons, self.ailerons)

  def set_elevator(self, dy):
    self.elevator = dy
    if abs(self.elevator) > self.max_elevator:
      self.elevator = math.copysign(self.max_elevator, self.elevator)

  def set_power(self, incr):
    self.power_setting += incr * self.throttle_step
    if self.power_setting < 0:
      self.power_setting = 0
    elif self.power_setting > self.max_power:
      self.power_setting = self.max_power
    print("power at " + str(self.power_setting))

  def shoot(self, target):
    #only shoot if animation seq. ended
    beamsound.play()
    if self.seq_b < self.num_b:
      return 0.0
    #animate bullets
    self.seq_b = 0
    #check for hit
    #components of direction vector
    diag_xz = math.cos(math.radians(self.pitch))
    drn_x = diag_xz * math.sin(math.radians(self.direction))
    drn_y = math.sin(math.radians(self.pitch))
    drn_z = diag_xz * math.cos(math.radians(self.direction))
    #this will already be a unit vector
    #vector from target to aeroplane
    a_x = target[0] - self.x
    a_y = target[1] - self.y
    a_z = target[2] - self.z
    #dot product
    dot_p = drn_x * a_x + drn_y * a_y + drn_z * a_z
    dx = a_x - dot_p * drn_x
    dy = a_y - dot_p * drn_y
    dz = a_z - dot_p * drn_z
    distance = math.sqrt(dx**2 + dy**2 + dz**2)
    print("distance={0:.2f}".format(distance))
    print("Damage: %s" % (DAMAGE_FACTOR))
    return DAMAGE_FACTOR / distance if distance > 0.0 else 2.0 * DAMAGE_FACTOR

  def home(self, target):
    #turn towards target location, mainly for AI control of enemy aircraft
    dir_t = math.degrees(math.atan2((target[0] - self.x), (target[2] - self.z)))
    #make sure the direction is alway a value between +/- 180 degrees
    #roll so bank is half direction, 
    self.roll = -((dir_t - self.direction + 180) % 360 - 180) / 2
    #find angle between self and target
    pch_t = math.degrees(math.atan2((target[1] - self.y),
            math.sqrt((target[2] - self.z)**2 + (target[0] - self.x)**2)))
    self.pitch = pch_t
    return True

  def update_variables(self):
    #time
    tm = time.time()
    dt = tm - self.last_time
    if dt < self.recalc_time: # don't need to do all this physics every loop
      return
    self.last_time = tm
    #force from ailerons and elevators to get rotational accelerations
    spsq = self.v_speed**2 + self.h_speed**2 #speed squared
    a_force = self.a_factor * self.ailerons * spsq #ailerons force (moment really)
    roll_acc = a_force / self.roll_inrta #good old Newton
    e_force = self.e_factor * self.elevator * spsq #elevator
    pitch_acc = e_force / self.pitch_inrta
    #velocities and positions
    if abs(self.roll) > self.max_roll: #make it easier to do flight control
      self.roll = math.copysign(self.max_roll, self.roll)
      self.rollrate = 0.0
    if abs(self.pitch) > self.max_pitch:
      self.pitch = math.copysign(self.max_pitch, self.pitch)
      self.pitchrate = 0.0
    self.roll += self.rollrate * dt #update roll position
    self.pitch += self.pitchrate * dt #update roll rate
    self.rollrate += roll_acc * dt
    self.rollrate *= DAMPING # to stop going out of contol while looking around!
    self.pitchrate += pitch_acc * dt
    self.pitchrate *= DAMPING
    #angle of attack
    aofa = math.atan2(self.v_speed, self.h_speed)
    aofa = math.radians(self.pitch) - aofa # approximation to sin difference
    lift = self.lift_factor * spsq * aofa
    drag = lift / LD 
    #if spsq < 100: #stall!  ####DONT STALL!!
     # lift *= 0.9
     # drag *= 1.3

    cos_pitch = math.cos(math.radians(self.pitch))
    sin_pitch = math.sin(math.radians(self.pitch))
    cos_roll = math.cos(math.radians(self.roll))
    sin_roll = math.sin(math.radians(self.roll))  
    ### start looking here for turning....
    h_force = (self.power_setting - drag) * cos_pitch - lift * sin_pitch
    v_force = lift * cos_pitch * cos_roll - self.mass #* GRAVITY
    h_acc = h_force / self.mass
    v_acc = v_force / self.mass
    self.h_speed += h_acc * dt
    if self.h_speed > self.VNE:
      self.h_speed = self.VNE
    elif self.h_speed < 0:  
      self.h_speed = 0
    self.v_speed += v_acc * dt
    if abs(self.v_speed) > self.VNE:
      self.v_speed = math.copysign(self.VNE, self.v_speed)
    turn_force = -lift * sin_roll * 1.5
    radius = self.mass * spsq / turn_force if turn_force != 0.0 else 0.0
    self.yaw = math.sqrt(spsq) / radius if radius != 0.0 else 0.0

  def update_position(self, height):
    #time
    tm = time.time()
    dt = tm - self.last_pos_time
    self.last_pos_time = tm
    self.x += (self.h_speed * math.sin(math.radians(self.direction)) * dt -
              self.x_perr * P_FACTOR - self.x_ierr * I_FACTOR)
    self.y += self.v_speed * dt - self.y_perr * P_FACTOR - self.y_ierr * I_FACTOR
    if self.y < (height + 3):
      self.y = height + 3
      self.v_speed = 0
      self.pitch = 2.5
      #self.roll = 0
    self.z += (self.h_speed * math.cos(math.radians(self.direction)) * dt -
              self.z_perr * P_FACTOR - self.z_ierr * I_FACTOR)

    self.direction += math.degrees(self.yaw) * dt - self.d_err * P_FACTOR

    ## debug/details
    #print("X: %s |Y: %s |dir: %s|v speed: %s|h speed: %s" % (str(self.x), str(self.y), str(self.direction), str(self.v_speed), str(self.h_speed) ))
    ## report to server str(self.direction) to send to helm

    #set values of model
    sin_d = math.sin(math.radians(self.direction))
    cos_d = math.cos(math.radians(self.direction))
    sin_r = math.sin(math.radians(self.roll))
    cos_r = math.cos(math.radians(self.roll))
    sin_p = math.sin(math.radians(self.pitch))
    cos_p = math.cos(math.radians(self.pitch))
    absroll = math.degrees(math.asin(sin_r * cos_d + cos_r * sin_p * sin_d))
    abspitch = math.degrees(math.asin(sin_r * sin_d - cos_r * sin_p * cos_d))
    self.model.position(self.x, self.y, self.z)
    self.model.rotateToX(abspitch)
    self.model.rotateToY(self.direction)
    self.model.rotateToZ(absroll)
    #set values for bullets
    if self.seq_b < self.num_b:
      self.bullets.position(self.x, self.y, self.z)
      self.bullets.rotateToX(abspitch)
      self.bullets.rotateToY(self.direction)
      self.bullets.rotateToZ(absroll)
    #set values for camera
    
    return (self.x - 10.0 * sin_d, self.y + 4, self.z - 10.0 * cos_d, self.direction)

  def draw(self):
    self.model.draw() ###make this toggled for inside/outside view?
    #draw the bullet sequence if not finished
    if self.seq_b < self.num_b:
      self.bullets.buf[0].textures[0] = BULLET_TEX[self.seq_b]
      self.bullets.draw()
      self.seq_b += 1

#define Instruments class
class Instruments(object):
  def __init__(self):
    wd = DISPLAY.width
    print(str(wd))
    ht = DISPLAY.height
    print(str(ht))
    
    asi_tex = pi3d.Texture("assets/textures/airspeed_indicator.png")  ### Update these with more sci-fi looking images
    alt_tex = pi3d.Texture("assets/textures/altimeter.png")
    rad_tex = pi3d.Texture("assets/textures/radar.png")  ## Use for Sensors
    dot_tex = pi3d.Texture("assets/textures/radar_dot.png")  ##Use for sensors
    ndl_tex = pi3d.Texture("assets/textures/instrument_needle.png")
    sprlogo_tex = pi3d.Texture("assets/textures/spr_logo.png") ##Logo

    self.asi = pi3d.ImageSprite(asi_tex, FLATSH, camera=CAMERA2D,
          w=128, h=128, x=-128, y=-ht/2+64, z=2)
    self.alt = pi3d.ImageSprite(alt_tex, FLATSH, camera=CAMERA2D,
          w=128, h=128, x=0, y=-ht/2+64, z=2)

    self.rad = pi3d.ImageSprite(rad_tex, FLATSH, camera=CAMERA2D,
          w=128, h=128, x=128, y=-ht/2+64, z=2)
    self.dot = pi3d.ImageSprite(dot_tex, FLATSH, camera=CAMERA2D,
          w=16, h=16, z=1)

    self.ndl1 = pi3d.ImageSprite(ndl_tex, FLATSH, camera=CAMERA2D,
          w=128, h=128, x=-128, y=-ht/2+64, z=1)
    self.ndl2 = pi3d.ImageSprite(ndl_tex, FLATSH, camera=CAMERA2D,
          w=128, h=128, x=0, y=-ht/2+64, z=1)
    self.ndl3 = pi3d.ImageSprite(ndl_tex, FLATSH, camera=CAMERA2D,
          w=128, h=128, x=128, y=-ht/2+64, z=1)
    
 
    self.spr = pi3d.ImageSprite(sprlogo_tex, FLATSH, camera=CAMERA2D,
          w=49, h=64, x=-wd/2+25, y=-ht/2+32, z=2)  ##Logo
    print(wd)
    self.dot_list = []
    self.update_time = 0.0
  def draw(self):
    
    #self.asi.draw()
    #self.alt.draw()
    self.rad.draw()
    self.spr.draw()  ## Logo
    """
    for i in self.dot_list:
      self.dot.position(i[1] + 128, i[2] + self.rad.y(), 1)
      self.dot.draw()
    self.ndl1.draw()
    self.ndl2.draw()
    self.ndl3.draw()
    """

  def update(self, ae, others):
    
    self.ndl1.rotateToZ(-360*ae.h_speed/140)
    self.ndl2.rotateToZ(-360*ae.y/3000)
    self.ndl3.rotateToZ(-ae.direction)
    
    self.dot_list = []
    for i in others:
      if i == "start":
        continue
      o = others[i]
      dx = (o.x - ae.x) / 50
      dy = (o.z - ae.z) / 50
      d = math.hypot(dx, dy)
      if d > 40:
        dx *= 40 / d
        dy *= 40 / d
      self.dot_list.append([o.refid, dx, dy])
    self.update_time = ae.last_pos_time

def json_load(ae, others): ### Replace this with UDP networking
  """httprequest other players. Sends own data and gets back array of all
  other players within sight. This function runs in a background thread
  """
  #TODO pass nearest, nearest.hp and own hp merge in some way
  tm_now = time.time()
  jstring = json.dumps([ae.refid, ae.last_time, ae.x, ae.y, ae.z,
      ae.h_speed, ae.v_speed, ae.pitch, ae.direction, ae.roll,
      ae.pitchrate, ae.yaw, ae.rollrate, ae.power_setting, ae.damage], separators=(',',':'))
  if ae.nearest:
    n_id = ae.nearest.refid
    n_damage = ae.nearest.other_damage
    ae.nearest.other_damage = 0.0
  else:
    n_id = ""
    n_damage = 0.0
  params = urllib_parse.urlencode({"id":ae.refid, "tm":tm_now, "x":ae.x, "z":ae.z,
          "json":jstring, "nearest":n_id, "damage":n_damage})
  others["start"] = tm_now #used for polling freqency
  urlstring = "http://www.eldwick.org.uk/sharecalc/rpi_json.php?{0}".format(params)
  #urlstring = "http://localhost/rpi_json.php?{0}".format(params)
  try:
    r = urllib_request.urlopen(urlstring)
    if r.getcode() == 200: #good response
      jstring = r.read().decode("utf-8")
      #print "jstring: %s" % (jstring)
      if len(jstring) > 50: #error messages are shorter than this
        olist = json.loads(jstring)
        #smooth time offset value
        ae.del_time = ae.del_time * 0.9 + olist[0] * 0.1 if ae.del_time else olist[0]
        #own damage is cumulative and not reset on server until dead!
        ae.damage = olist[1]
        #if ae.damage > 2.0 * DAMAGE_FACTOR: #explode return to GO etc
        #print(ae.damage)
        olist = olist[2:]
        """
        synchronisation system: sends time.time() which is used to calculate
        an offset on the server and which is inserted as the second term 
        in the json string. When the list of other players comes back from
        the server it is preceded by the same offset time inserted in this json.
        This is used to adjust the last_time for all
        the other avatars.
        """
        nearest = None
        ae.rtime = 60
        for o in olist:  ## AI should go somewhere in here on the server....
          if not(o[0] in others):
            others[o[0]] = Aeroplane("assets/models/cigar1.obj", 0.9, o[0])
          oa = others[o[0]] #oa is other aeroplane, ae is this one!
          oa.refif = o[0]
          #exponential smooth time offset values
          oa.del_time = oa.del_time * 0.9 + o[1] * 0.1 if oa.del_time else o[1]
          oa.last_time = o[2] + oa.del_time - ae.del_time # o[1] inserted by server code
          dt = tm_now - oa.last_time
          if oa.x == 0.0:
            oa.x, oa.y, oa.z = o[3], o[4], o[5]
          nx = o[3] + o[6] * math.sin(math.radians(o[9])) * dt
          ny = o[4] + o[7] * dt
          nz = o[5] + o[6] * math.cos(math.radians(o[9])) * dt
          distance = math.hypot(nx - ae.x, nz - ae.z)
          if not nearest or distance < nearest:
            nearest = distance
            ae.nearest = oa
          oa.x_perr, oa.y_perr, oa.z_perr = oa.x - nx, oa.y - ny, oa.z - nz
          oa.x_ierr += oa.x_perr
          oa.y_ierr += oa.y_perr
          oa.z_ierr += oa.z_perr
          oa.d_err = ((oa.direction - (o[9] + o[12] * dt) + 180) % 360 - 180) / 2
          oa.h_speed = o[6]
          oa.v_speed = o[7]
          oa.pitch = o[8]
          oa.roll = o[10]
          oa.pitchrate = o[11]
          oa.yaw = o[12]
          oa.rollrate = o[13]
          oa.power_setting = o[14]
          oa.damage = o[15]

        if nearest:
          ae.rtime = NR_TM + (max(min(nearest, FA_DIST), NR_DIST) - NR_DIST) / \
                  (FA_DIST - NR_DIST) * (FA_TM - NR_TM)
        #TODO tidy up inactive others; flag not to draw, delete if inactive for long enough
        return True
      else:
        print(jstring)
        return False
    else:
      print(r.getcode())
      return False
  except Exception as e:
    print("exception:", e)


### remove this part of the networking (it's for ID) defined at the top of page (better unique id)
#MAC address
"""
try:
  refid = (open("/sys/class/net/eth0/address").read()).strip()
except:
  try:
    refid = (open("/sys/class/net/wlan0/address").read()).strip()
  except:
    refid = "00:00:00:00:00:00"
"""
    
    
    
#create the instances of Aeroplane
a = Aeroplane("assets/models/starship.obj", 0.00, refid)  ### Our ship
a.z, a.direction = 905, 180
#a.z, a.direction = 1200, 180
#create instance of instruments
inst = Instruments()
others = {"start": 0.0} #contains a dictionary of other players keyed by refid
thr = threading.Thread(target=json_load, args=(a, others))
thr.daemon = True #allows the program to exit even if a Thread is still running
thr.start()
# Load textures for the environment cube
ectex = pi3d.loadECfiles("assets/textures/ecubes", "bkg1")
myecube = pi3d.EnvironmentCube(size=7000.0, maptype="FACES", camera=CAMERA)
myecube.set_draw_details(FLATSH, ectex)
myecube.set_fog((0.0,0.0,0.0,1.0), 4000)
# Create elevation map
mapwidth = 50000.0 #probably need to increase these
mapdepth = 50000.0
mapheight = 3000.0
#mountimg1 = pi3d.Texture("assets/textures/mountains3_512.jpg")   ### get rid of this (we're in space)
mountimg1 = pi3d.Texture("assets/textures/grid.png")   ### get rid of this (we're in space)
bumpimg = pi3d.Texture("assets/textures/grasstile_n.jpg")   ### get rid of this (we're in space)
reflimg = pi3d.Texture("assets/textures/stars.jpg")  ### update with space skybox
#mymap = pi3d.ElevationMap("assets/textures/mountainsHgt.jpg", name="map",
#                     width=mapwidth, depth=mapdepth, height=mapheight,
#                     divx=64, divy=64, camera=CAMERA)  ###we don't need this
mymap = pi3d.ElevationMap("assets/textures/mountainsHgt.jpg", name="map",
                     width=mapwidth, depth=mapdepth, height=mapheight,
                     divx=64, divy=64, camera=CAMERA)  ###we don't need this
#mymap.set_draw_details(SHADER, [mountimg1, bumpimg, reflimg], 1024.0, 0.0)
mymap.set_draw_details(SHADER, [mountimg1, bumpimg, reflimg], 0.0, 0.0)
#mymap.set_fog((0.5, 0.5, 0.5, 1.0), 4000)  ### make fog dark to hide?
#mymap.set_fog((0.0, 0.0, 0.0, 1,0), 4000)  ### make fog dark to hide?
# init events
inputs = pi3d.InputEvents()
#inputs.get_mouse_movement()
CAMERA.position((0.0, 0.0, -10.0)) #org


cam_rot, cam_pitch = 0, 0
cam_toggle = True #control mode
mx=0
my=0
while DISPLAY.loop_running() and not inputs.key_state("KEY_ESC"):
  inputs.do_input_events() 

  if inputs.key_state("KEY_Q") or inputs.key_state("BTN_BASE3"): #control mode
    print("X - 1 %s" % (mx))
    mx=mx-1
    #mx=-1
  if inputs.key_state("KEY_E") or inputs.key_state("BTN_BASE4"): #control mode
    print("X + 1 %s" % (mx))
    mx=mx+1
    #mx=1
  if inputs.key_state("KEY_SPACE") or inputs.key_state("BTN_BASE4"): #control mode
    print("Centering. X=%s Y=%s" % (mx,my))
    mx=0
    my=0
  if inputs.key_state("KEY_I") or inputs.key_state("BTN_BASE5"): #control mode
    print("Y - 1 %s" % (my))
    my=my-1
    #my=-1
  if inputs.key_state("KEY_K") or inputs.key_state("BTN_BASE6"): #control mode
    print("Y + 1 %s " % (my))
    my=my+1
    #my=1

  #mx, my, mv, mh, md = inputs.get_mouse_movement()
  print("--%s--"%(mx))
  #_, _, mv, mh, md = inputs.get_mouse_movement()
  if cam_toggle:
    a.set_ailerons(-mx * 0.001)
    a.set_elevator(my * 0.001)
  else:
    cam_rot -= mx * 0.1
    cam_pitch -= my * 0.1
  #"""
  """ joystick input
  mx, my = inputs.get_joystickR()
  if cam_toggle:
    a.set_ailerons(-mx * 0.06)
    a.set_elevator(my * 0.02)
  else:
    cam_rot -= mx * 2.0
    cam_pitch -= my * 2.0
  """
  
  ### Control this over network
  if inputs.key_state("KEY_W") or inputs.get_hat()[1] == -1: #increase throttle
    a.set_power(1)
    print("+ speed")
  if inputs.key_state("KEY_S") or inputs.get_hat()[1] == 1: #throttle back
    a.set_power(-1)
    print("- speed")
  if inputs.key_state("KEY_X"): #jump to first enemy!
    print("Jump")
    for i in others:
      if i != "start":
        b = others[i]
        a.x, a.y, a.z = b.x, b.y + 5, b.z
        break
  if inputs.key_state("KEY_B") or inputs.key_state("BTN_BASE2"): #brakes
    print("brakes")
    a.h_speed *= 0.99
  if inputs.key_state("KEY_V") or inputs.key_state("BTN_TOP2"): #view mode
    print("viewmode")
    cam_toggle = False
    a.set_ailerons(0)
    a.set_elevator(0)
  if inputs.key_state("KEY_C") or inputs.key_state("BTN_BASE"): #control mode
    print("control mode")
    cam_toggle = True
    cam_rot, cam_pitch = 0, 0

  if inputs.key_state("KEY_1"): 
    print("Toggle Instuments")
    if instdisplay==True:
        instdisplay=False
    else:
	instdisplay=True
	
  if inputs.key_state("KEY_0"): 
    print("Screenshot")
    pi3d.screenshot("screenshots/screenshot.jpg")

  #if inputs.key_state("BTN_LEFT") or inputs.key_state("BTN_PINKIE") or inputs.key_state("KEY_P"): #shoot
  if inputs.key_state("KEY_P"): #shoot
    print("shoot")
    #target is always nearest others set during last json_load()
    #tx, ty, tz = 0., 0.0, 0.0
    if a.nearest:
      tx, ty, tz = a.nearest.x, a.nearest.y, a.nearest.z
      a.nearest.other_damage += a.shoot([tx, ty, tz])

  a.update_variables()
  loc = a.update_position(mymap.calcHeight(a.x, a.z))
  CAMERA.reset()
  #CAMERA.rotate(-20 + cam_pitch, -loc[3] + cam_rot, 0) #unreal view
  CAMERA.rotate(-20 + cam_pitch, -loc[3] + cam_rot, -a.roll) #air-sick view
  CAMERA.position((loc[0], loc[1], loc[2]))
  if instdisplay==True:
    inst.draw()  ### comment this out to disable instruments
  a.draw()  ### Draw your ship

  for i in others:
    if i == "start":
      continue
    b = others[i]
    b.update_variables()
    b.update_position(mymap.calcHeight(b.x, b.z))
    b.draw()
  #do httprequest if thread not already started and enough time has elapsed
  if not (thr.isAlive()) and (a.last_pos_time > (others["start"] + a.rtime)):
    thr = threading.Thread(target=json_load, args=(a, others))
    thr.daemon = True #allows the program to exit even if a Thread is still running
    thr.start()
    
  if a.last_pos_time > (inst.update_time + NR_TM):
    inst.update(a, others)

  #mymap.draw() ### Draw "ground"
  myecube.position(loc[0], loc[1], loc[2])
  myecube.draw()

inputs.release()
DISPLAY.destroy()
