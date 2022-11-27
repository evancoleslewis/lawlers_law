.PHONY: all setup clean

all: setup clean

setup: requirements.txt
	pip install -r requirements.txt

clean:
	rm -rf __pycache__
