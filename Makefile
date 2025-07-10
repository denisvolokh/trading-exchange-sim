.PHONY: run install clean

install:
	pip install -r requirements.txt

run:
	python run.py

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
