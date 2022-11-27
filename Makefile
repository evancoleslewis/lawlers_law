.PHONY: all setup clean

all: setup clean

setup: requirements.txt
	@echo "Installing required packages..."
	pip install -r requirements.txt

clean:
	@echo "Clearing out pycache..."
	rm -rf __pycache__