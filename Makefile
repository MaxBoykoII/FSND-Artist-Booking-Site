## The Makefile includes instructions on development setup and linting

setup:
	# Create python virtualenv
	conda create --name fyyur

install:
	# This should be run inside the virtual environment
	pip install Flask
	pip install -r requirements.txt

launch:
	# This should be run inside the virtual environment
	# Launches the application
	export FLASK_APP=myapp
	export FLASK_ENV=development
	python app.py