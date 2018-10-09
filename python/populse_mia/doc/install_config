# Install/config 
# Ubuntu 16.04 - Python3 - Git/GitLab - Pycharm

# INSTALLING AND CONFIGURATE GIT/GITLAB

sudo apt-get install git
cat ~/.ssh/id_rsa.pub 

#If no result: create a ssh key
ssh-keygen -t rsa -C your_adress@example.com -b 4096

# COPY THE KEY WITH XCLIP
sudo apt-get install xclip
xclip -sel clip < ~/.ssh/id_rsa.pub

# Add your key to Gitlab (Profile -> Settings -> SSH Keys and paste)
ssh -T git@gricad-gitlab.univ-grenoble-alpes.fr #Just a test to see if the SSH Key works

# INSTALL THE LIBRARY FOR MIA2
sudo apt-get install python3-pyqt5
sudo apt-get install python-nibabel
sudo apt-get install python3-nibabel
sudo apt-get install python3-tk
sudo apt-get install python3-matplotlib

# INSTALL AN IDE (HERE PYCHARM-COMMUNITY)
sudo add-apt-repository ppa:ubuntu-desktop/ubuntu-make
sudo apt-get update
sudo apt-get install ubuntu-make
umake ide pycharm


