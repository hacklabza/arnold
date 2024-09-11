PYTEST=pytest

# Colours.
CLEAR=\033[0m
RED=\033[0;31m
GREEN=\033[0;32m
CYAN=\033[0;36m

# Define the params of the help command.
help:
	@echo "usage: make <target>"
	@echo "    $(CYAN)poetry$(CLEAR): Initialises the poetry environment and install dependancies"
	@echo "    $(CYAN)install$(CLEAR): Installs arnold on the raspberrypi."
	@echo "    $(CYAN)test$(CLEAR): Run unittest suite."

# Initialises the virtualenv and activates it.
poetry:
	@echo "$(CYAN)Activating virtualenv...$(CLEAR)"
	poetry shell
	@echo "$(CYAN)Installing python deps...$(CLEAR)"
	poetry install
	@echo "$(GREEN)DONE$(CLEAR)"

# Installs arnold on the raspberrypi.
install:
	@echo "$(CYAN)Installing Arnold...$(CLEAR)"
	@sudo apt update -y
	@sudo apt upgrade -y
	@sudo apt install -y portaudio19-dev python3-dev flac libespeak1 espeak ffmpeg
	@sudo apt install -y python3-opencv

# Run unittest suite.
test: poetry
	@echo "$(CYAN)Running unittests...$(CLEAR)"
	GPIOZERO_PIN_FACTORY=mock $(PYTEST) arnold
