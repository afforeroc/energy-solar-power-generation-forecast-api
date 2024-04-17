# Energy Solar Generation API
Energy Computer Systems - Solar Power Forecasting API

## Install Python and Update PIP
> PowerShell
* Install [Python 3.9.0](https://www.python.org/downloads/release/python-390/)
* Check Python version: `python --version`
* Install and upgrade PIP: `python -m pip install --upgrade pip`

## Configure the Virtual Environment
> PowerShell
* Navigate to the repository folder: `cd .\solar-power-forecasting\`
* Allow the execution of scripts to activate a virtual environment: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
* Install the virtual environment package: `pip install virtualenv`
* Create a virtual environment: `python -m virtualenv venv`
* Activate the virtual environment: `.\venv\Scripts\activate`
* Install the required libraries: `pip install -r requirements.txt`

## Use the App within the Virtual Environment
> PowerShell
* Navigate to the repository folder: `cd .\solar-power-forecasting-api\`
* Activate the virtual environment: `.\venv\Scripts\activate`
* Run the Python file: `streamlit run app.py`
* Deactivate the virtual environment: `deactivate`

## Generate Executable App
> PowerShell
* Navigate to the repository folder: `cd .\solar-power-forecasting-api\`
* Generate an executable file: `pyinstaller --onefile .\app.py`
* Run the executable file: `.\app.exe`
