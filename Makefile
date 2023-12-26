VENV=ve
PYTHON=$(VENV)/bin/python3
PIP=$(VENV)/bin/pip3
PYTEST=$(VENV)/bin/pytest

# Colours.
CLEAR=\033[0m
RED=\033[0;31m
GREEN=\033[0;32m
CYAN=\033[0;36m

# Define the params of the help command.
help:
	@echo "usage: make <target>"
	@echo "    $(CYAN)venv$(CLEAR): Initialises the virtualenv and activates it."
	@echo "    $(CYAN)build-dev$(CLEAR): Installs the python deps."
	@echo "    $(CYAN)install$(CLEAR): Installs arnold on the raspberrypi."
	@echo "    $(CYAN)test$(CLEAR): Run unittest suite."

# Initialises the virtualenv and activates it.
venv:
	@echo "$(CYAN)Initialising virtualenv...$(CLEAR)"
	python3 -m venv $(VENV)
	@echo "$(CYAN)Activating virtualenv...$(CLEAR)"
	. $(VENV)/bin/activate
	cd .
	@echo "$(GREEN)DONE$(CLEAR)"

# Installs the python deps.
deps:
	@echo "$(CYAN)Installing python deps...$(CLEAR)"

	$(PIP) install .
	@echo "$(GREEN)DONE$(CLEAR)"

# Installs arnold on the raspberrypi.
install:
	@echo "$(CYAN)Installing Arnold...$(CLEAR)"
	@sudo apt update -y
	@sudo apt ugrade -y
	@sudo apt install -y portaudio19-dev python3-dev flac libespeak1 espeak ffmpeg
	@sudo apt install -y python3-opencv

# Run unittest suite.
test: $(VENV)
	@echo "$(CYAN)Running unittests...$(CLEAR)"
	pip install -r requirements-test.txt
	GPIOZERO_PIN_FACTORY=mock $(PYTEST) arnold
