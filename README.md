# Arnold
RPi 4 Based Robotic Platform

## Setup

 - Distro download: https://www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-32-bit
 - Remote Access: https://www.raspberrypi.org/documentation/remote-access/
 - Headless Wifi: https://www.raspberrypi.org/documentation/configuration/wireless/headless.md
 - Configure sound: https://www.raspberrypi.org/documentation/configuration/raspi-config.md

## System Requirements

 - Raspberry Pi OS Lite (Preferrable but not essential)
 - Git
 - Python 3.7+
 - Python Virtualenv

## Build Requirements

 - portaudio19-dev
 - python3-dev
 - flac

## Development

```bash
# Clone arnold locally
git clone git@github.com:hacklabza/arnold.git
cd arnold/

# Setup the virtualenv and install the python deps
make venv
make deps

# Run unittest
make test
```

## Installation

```bash
# Get the RPi's IP address
ping raspberrypi.local

# Access to the commandline over SSH
ssh pi@192.168.1.115

# Clone and install arnold
git clone git@github.com:hacklabza/arnold.git
cd arnold/
sudo make install

# Run the unittests to make sure arnold is installed correctly
make test
```

## Running arnold

```bash
# Initialise and run the internal API server
arnold run
```

Open your browser to http://192.168.1.115:8000 to control arnold.
