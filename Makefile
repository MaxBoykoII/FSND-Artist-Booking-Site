## The Makefile includes instructions on development setup and linting

setup:
	# Create python virtualenv
	conda create --name fyyur python=3.7.4

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

lint:
	# Lint the python code
	# This should be run inside the virtual environment
	pylint --ignored-classes=SQLAlchemy --disable=E1133,R,C,W0511,W0401,W0622,W0143,E1101,W0613,E1101,W0614,W0611,W0105  app.py

all: install lint