#!/usr/bin/env bash

set -e
set -x

start_enable() {
	for s in $@; do
		echo "Enabling and starting service $s"
		sudo systemctl enable $s
		sudo systemctl start $s
	done
}

# Install crap
crap=""
PHP_VER="php8.2"
if ! type mariadb; then crap="$crap mariadb-server ${PHP_VER}-mysql"; fi
if ! type pip3; then crap="$crap python3"; fi
if ! type php; then crap="$crap ${PHP_VER}-common ${PHP_VER}-fpm ${PHP_VER}-mysql"; fi
if ! type git; then crap="$crap git"; fi
if [ ! -d "/etc/nginx" ]; then crap="$crap nginx"; fi

if [ -n "$crap" ]; then
	sudo apt update --yes
	sudo apt upgrade --yes
	sudo apt install --yes $crap
fi

# Create LED user, home directory, etc.
if ! id leds; then
	echo "Creating leds user"
	sudo useradd leds
fi
sudo usermod -a -G leds leds
if [ ! -d /home/leds ]; then
	sudo mkdir /home/leds
	sudo chown leds:leds /home/leds
fi
REPO_DIR="/home/leds/led-ctrl-ws"
SETUP_DIR="$REPO_DIR/setup"
if [ ! -d "$REPO_DIR/.git" ]; then
	sudo -u leds sh -c "cd ~; git clone https://github.com/abc123me/led-ctrl-ws.git"
else
	sudo -u leds sh -c "cd \"$REPO_DIR\"; git pull"
fi

# Create Python3 virtual environment
if [ ! -f "$REPO_DIR/leds-venv/bin/pip" ]; then
	sudo -u leds python3 -m venv "$REPO_DIR/leds-venv"
	sudo -u leds "$REPO_DIR/leds-venv/bin/pip" install rpi-ws281x
fi

# Add LED service control to sudoers
if [ ! -f "/etc/sudoers.d/069_leds-service" ]; then
	sudo cp -i -v "$SETUP_DIR/069_leds-service" "/etc/sudoers.d/069_leds-service"
	sudo chown root:root "/etc/sudoers.d/069_leds-service"
	sudo chmod 600 "/etc/sudoers.d/069_leds-service"
fi

# Enabled LED webserver, delete default nginx server
if [ ! -h "/etc/nginx/sites-available/led_ctrl" ]; then
	sudo ln --symbolic "$SETUP_DIR/led_ctrl" /etc/nginx/sites-available/led_ctrl
	sudo ln --symbolic "$SETUP_DIR/led_ctrl" /etc/nginx/sites-enabled/led_ctrl
	sudo rm -f -v /etc/nginx/sites-enabled/default
fi

# Setup LED service
SERVICE_FILE="$REPO_DIR"/leds.service
LEDS_PY_FILE="$REPO_DIR"/leds.py
if [ ! -h "/etc/systemd/system/leds.service" ]; then
	sudo ln --symbolic "$SERVICE_FILE" /etc/systemd/system/leds.service
fi
sudo chown root:root "$SERVICE_FILE"
sudo chmod 744       "$SERVICE_FILE"
sudo chown root:root "$LEDS_PY_FILE"
sudo chmod 744       "$LEDS_PY_FILE"
sudo systemctl daemon-reload

#Setup MariaDB
echo "Setting up database"
start_enable mariadb
sudo mariadb < "$SETUP_DIR/LED_DB.dump"

# Enable and start the rest of the services
echo "Starting everything up!"
start_enable "${PHP_VER}-fpm" nginx leds

# TODO: Setup databse
