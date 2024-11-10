#!/bin/sh

set -e
set -x

sudo apt update --yes
sudo apt upgrade --yes
sudo apt install --yes nginx mariadb-server php-common php-fpm php-mysql mycli

sudo useradd leds
sudo usermod -a -G leds leds
sudo -u leds git clone /home/leds/
sudo cp -i -v /home/leds/setup/069_leds-service /etc/sudoers.d/
sudo cp -i -v /home/leds/setup/led_ctrl /etc/nginx/sites-available
sudo ln --symbolic /etc/nginx/sites-available/led_ctrl /etc/nginx/sites-enabled/led_ctrl
sudo rm -v /etc/nginx/sites-enabled/default

sudo ln --symbolic /home/leds/leds.service /etc/systemd/system/leds.service
sudo chown root:root /home/leds/leds.service
sudo chown root:root /home/leds/leds.py
sudo chmod 744 /home/leds/leds.py
sudo chmod 744 /home/leds/leds.service

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

sudo mariadb </home/leds/setup/LED_DB.dump

# TODO: Setup databse
