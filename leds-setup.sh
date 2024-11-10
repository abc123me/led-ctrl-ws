#!/bin/sh

set -e
set -x

# Install crap
sudo apt update --yes
sudo apt upgrade --yes
sudo apt install --yes nginx mariadb-server php-common php-fpm php-mysql mycli python3 python3-pip

# Create LED user, home directory, etc.
sudo useradd leds
sudo usermod -a -G leds leds
if [ ! -d /home/leds ]; then
	sudo mkdir /home/leds
	sudo chown leds:leds /home/leds
fi
sudo -u leds sh -c "cd ~; git clone https://github.com/abc123me/led-ctrl-ws.git"
REPO_DIR="/home/leds/led-ctrl-ws"
SETUP_DIR="$REPO_DIR/setup"

# Create Python3 virtual environment
sudo -u leds python3 -m "$REPO_DIR/leds-venv"
sudo -u leds "$REPO_DIR/leds-venv/bin/pip install rpi-ws281x"

# Add LED service control to sudoers
sudo cp -i -v "$SETUP_DIR/069_leds-service" "/etc/sudoers.d/069_leds-service"
sudo chown root:root "/etc/sudoers.d/069_leds-service"
sudo chmod 600 "/etc/sudoers.d/069_leds-service"

# Enabled LED webserver, delete default nginx server
sudo cp -i -v "$SETUP_DIR/led_ctrl" "/etc/nginx/sites-available"
sudo ln --symbolic /etc/nginx/sites-available/led_ctrl /etc/nginx/sites-enabled/led_ctrl
sudo rm -f -v /etc/nginx/sites-enabled/default

# Setup LED service
sudo ln --symbolic "$SETUP_DIR"/leds.service /etc/systemd/system/leds.service
sudo chown root:root /home/leds/leds.service
sudo chown root:root /home/leds/leds.py
sudo chmod 744 /home/leds/leds.py
sudo chmod 744 /home/leds/leds.service

#Setup MariaDB
sudo mariadb </home/leds/setup/LED_DB.dump

# Enable and start all services
start_enable() {
	for s in $@; do
		set +x
		echo "Enabling and starting service $s"
		set -x
		sudo systemctl enable "$s"
		sudo systemctl start "$s"
`	done
}
sudo systemctl daemon-reload
start_enable mariadb nginx leds

# TODO: Setup databse
