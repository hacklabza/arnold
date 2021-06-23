VENV=./ve
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
	@echo "    $(CYAN)build-dev$(CLEAR): Initialises the virtualenv and installs the python deps."
	@echo "    $(CYAN)install$(CLEAR): Installs arnold on the raspberrypi."
	@echo "    $(CYAN)test$(CLEAR): Run unittest suite."

# Installs arnold on the raspberrypi.
build-dev: $(VENV)
	@echo "$(CYAN)Initialising virtualenv...$(CLEAR)"
	python3 -m venv $(VENV)
	@echo "$(GREEN)DONE$(CLEAR)"
	@echo "$(CYAN)Installing python deps...$(CLEAR)"
	$(PIP) install -r requirement.txt
	@echo "$(GREEN)DONE$(CLEAR)"

# Installs arnold on the raspberrypi.
install: build-virtualenv docker-build-image
	@echo "$(CYAN)Running docker-compose...$(CLEAR)"
	@sudo $(VENV)/bin/docker-compose up --build

# RRun unittest suite.
test:
	@echo "$(CYAN)Running unittests...$(CLEAR)"
	$(PIP) install -r requirement-test.txt
	$(PYTEST) arnold
