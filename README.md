space pi-rates
==============
website: http://kwadroke.github.io/rpispacepirates/

Space Pi-rates is a Starship Bridge Simulator created for the Raspberry Pi. Space Pi-rates is inspired by Artemis Spaceship Bridge Simulator. The game is not yet functional and is a Work in Progress.


Raspberry Pi Instructions:

run these commands at the terminal to setup (only needs to be done once):

    sudo echo framebuffer_width=640 >> /boot/config.txt
    sudo echo framebuffer_width=480 >> /boot/config.txt
    sudo chown root:video /dev/fb*
    sudo usermod -a -G video pi
    cd /home/pi
    git clone http://github.com/kwadroke/space_pi-rates.git
    sudo apt-get update
    sudo apt-get install python-pip 
    sudo pip install pi3d
    sudo pip install Pillow
    sudo reboot

To run game (console):

    cd space_pi-rates
    python console.py

To run game (mainscreen):

    cd space_pi-rates
    sudo python mainscreen.py

