space pi-rates
==============
website: http://kwadroke.github.io/rpispacepirates/

Space Pi-rates is a Starship Bridge Simulator created for the Raspberry Pi. Space Pi-rates is inspired by Artemis Spaceship Bridge Simulator. The game is not yet functional and is a Work in Progress.


Raspberry Pi Instructions:

run these commands at the terminal to setup (only needs to be done once):

    sudo echo framebuffer_width=640 >> /boot/config.txt
    sudo echo framebuffer_height=480 >> /boot/config.txt
    sudo chown root:video /dev/fb*
    sudo usermod -a -G video pi
    cd /home/pi
    git clone http://github.com/kwadroke/space_pi-rates.git
    sudo apt-get update
    sudo apt-get install python-pip python-imaging
    sudo pip install pi3d
    sudo reboot

Linux Desktop Instructions (Debian/Ubuntu):

    cd ~
    git clone http://github.com/kwadroke/space_pi-rates.git
    sudo apt-get update
    sudo apt-get install python-pip python-imaging libgles2-mesa-dev
    sudo pip install pi3d


Windows Desktop Instructions (for Console & Server):

    Clone source code from: http://github.com/kwadroke/space_pi-rates.git
    Download & Install Python 2.7.x from https://www.python.org/downloads/windows/.
        Select the last option in the list of components to install  __..add python.exe to Path__ by selecting the option to install on hard drive.
    Download & install Pygame from http://pygame.org/download.shtml for Python 2.7.x


Windows Desktop Instructions For Pi3D (Mainscreen & Science) (Work in progress)

    Download & Install NumPy for Python 2.7 from SourceForge
        http://sourceforge.net/projects/numpy/files/NumPy/1.9.2/numpy-1.9.2-win32-superpack-python2.7.exe/download
    open command prompt window then
      pip install Pillow
      pip install pi3d
    Download Pi3D Dlls from https://github.com/paddywwoof/pi3d_windll/archive/master.zip
    and extract the dlls to the rpispacepirates folder for your system


To start server:

    cd rpispacepirates
    python server.py


To run game (console):

    cd rpispacepirates
    python console.py


To run game (mainscreen):

    cd rpispacepirates
    sudo python mainscreen.py


To run game (mainscreen on Windows - not yet working):

    cd rpispacepirates
    python mainscreen.py
