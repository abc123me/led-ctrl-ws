# led-ctrl-ws

LED control webserver and LED control daemon for pi, this really should be too repos, but I'm lazy!

# Installation

Installation requires sudo access, and WILL create a giant security hole in your system at the leds python daemon unfortunately must run as root

```sh
wget "https://raw.githubusercontent.com/abc123me/led-ctrl-ws/refs/heads/master/leds-setup.sh" -O /tmp/leds-setup.sh
chmod +x /tmp/leds-setup.sh
/tmp/leds-setup.sh
```

Or as a one-liner
```sh
wget "https://raw.githubusercontent.com/abc123me/led-ctrl-ws/refs/heads/master/leds-setup.sh" -O /tmp/leds-setup.sh && chmod +x /tmp/leds-setup.sh && /tmp/leds-setup.sh
```

## Installation warning
Please use the script, just cloning this repo *is not enough* as packages need to be installed, databases need created, and python virtual environments need configured. See the script for how to do so, documentation does not currently exist.