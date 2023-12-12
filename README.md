
Install and update node to the latest version:
```
sudo apt install npm
sudo npm cache clean -f
sudo npm install -g n
sudo n stable
```
Then `cd` into this directory and run:
```
python -m venv .venv
pip install -r requirements.txt
npm i
```
This should set up your development environment. Finally, run:
```
npm run compile
npm run serve
```
and the server should start. If you get an error with pip, be sure to use Python version >= 3.10. However, < 3.13a as I see errors with that version.
