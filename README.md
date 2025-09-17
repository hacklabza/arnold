# Arnold
RPi 4 Based Robotic Platform

## Setup

 - Distro download: https://www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-64-bit
 - Remote Access: https://www.raspberrypi.org/documentation/remote-access/
 - Headless Wifi: https://www.raspberrypi.org/documentation/configuration/wireless/headless.md
 - Configure sound: https://www.raspberrypi.org/documentation/configuration/raspi-config.md

## System Requirements

 - Raspberry Pi OS Lite (Preferrable but not essential)
 - Git
 - Python 3.11+
 - Python Virtualenv

## Build Requirements

 - portaudio19-dev
 - python3-dev
 - flac
 - libespeak1
 - espeak-ng
 - ffmpeg
 - python3-opencv
 - ninja-build
 - poetry (https://python-poetry.org/docs/#installing-with-the-official-installer)

Run the following command to install system dependancies

```bash
make install
```

## Development

```bash
# Clone arnold locally
git clone git@github.com:hacklabza/arnold.git
cd arnold/

# Setup the virtualenv and install the python deps
make poetry
make deps

# Run unittest
make test
```

## Installation

```bash
# Get the RPi's IP address
ping raspberrypi.local

# Access to the commandline over SSH
ssh pi@raspberrypi.local

# Clone and install arnold
git clone git@github.com:hacklabza/arnold.git
cd arnold/
make install
make poetry

# Run the unittests to make sure arnold is installed correctly
make test
```

## Running arnold

### Manual mode

```bash
# Initialise and run the internal API server
arnold run
```

Open your browser to http://192.168.1.115:8000 to control arnold.

### Autonomous mode

```bash
# Initialise and run arnold in autonomous mode
arnold run -a
```

A rudimentary obstacle avoidance system is in place to stop arnold from running into things using lidar.

### Voice command mode

```bash
# Initialise and run arnold in voice command mode
arnold run -v
```

Arnold will listen for voice commands and execute them based on the command mapping in `arnold/constants.py`. It falls back to a conversation with ChatGPT if it doesn't understand the command.
