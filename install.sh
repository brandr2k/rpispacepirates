sudo echo framebuffer_width=640 >> /boot/config.txt
sudo echo framebuffer_width=480 >> /boot/config.txt
sudo chown root:video /dev/fb*
sudo usermod -a -G video pi
cd /home/pi
git clone http://github.com/kwadroke/space_pi-rates.git
sudo apt-get update
sudo apt-get install python-pip python-imaging
sudo pip install pi3d
sudo reboot
