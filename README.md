

## Instruction to use Ayurvedic-Intelligence

- git clone `https://github.com/vk07kiran/Ayurvedic-Intelligence.git`
- Start apache and mysql server through xampp
- Create a database name userdb
- In order to use chatbot, Install ollama and the model llama3.2 & mxbai-embed-large
  - Download and install ollama from `https://ollama.com/download` file size is about 1GB
  - Install models. Go to your command prompt type `ollama pull llama3.2` and `ollama pull mxbai-embed-large`
- Open the folder Ayurvedic-Intelligence and install requirements.txt (pip install -r requirements.txt)
- Run app.py

## HerbScanner (This doesn't work)
In order to run HerbScanner, it requires tensorflow but it is not supported by python 3.13, so you need to create a virtual environment and install python 3.11 or lower than 3.12
1. To create a python virtual environment:
  - `python -m venv myenv`
  - Run poweshell as administrator and `Set-ExecutionPolicy RemoteSigned` Y
  - `.\myenv\Scripts\Activate.ps1`
  - `pip install --upgrade pip`
  - `pip install tensorflow`
  - `deactivate`
  - `rmdir /s /q myenv`

2. edited by unknown guy
