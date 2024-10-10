#!/bin/bash

# Define color codes
RESET="\033[0m"
GREEN="\033[32m"
RED="\033[31m"
YELLOW="\033[33m"

# virtual environment stuff
echo -e "${YELLOW}Setting up the environment...${RESET}"

# create the virtual environment
python3 -m venv venv
echo -e "${GREEN}Virtual environment created.${RESET}"

# activate virtual environment
source venv/bin/activate
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${RED}Failed to activate the virtual environment!${RESET}"
    exit 1
else
    echo -e "${GREEN}Virtual environment activated successfully.${RESET}"
fi

# install dependencies
pip3 install -r requirements.txt
echo -e "${GREEN}Required packages have been downloaded.${RESET}"

# oad environment variables from .env
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo -e "${GREEN}.env variables have been loaded.${RESET}"
else
    echo -e "${RED}.env file not found!${RESET}"
fi

# initialize the database
if [ -f "create_db.py" ]; then
    python create_db.py
    echo -e "${GREEN}Database initialized.${RESET}"
else
    echo -e "${RED}create_db.py not found!${RESET}"
fi

if [ -f "main.py" ]; then
    python main.py -i
    echo -e "${GREEN}main.py executed successfully.${RESET}"
else
    echo -e "${RED}main.py not found!${RESET}"
fi
