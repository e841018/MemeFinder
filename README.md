# MemeFinder

## Requirements

* Backend: Python 3
  * numpy, scipy, flask, python-socketio, eventlet
* Frontend: Google Chrome

## Usage

1. Download `memes_tw.zip` and `memes_tw.pkl` from [here](https://drive.google.com/drive/folders/1u5gxiflz80oIZgIBa9Y0Ir3IPZteWevO).

2. Organize the files as follows:

   ```
   MemeFinder
   +- frontend
   |  +- ...
   +- features
   |  +- memes_tw.pkl (downloaded)
   +- images
   |  +- memes_tw (extracted from memes_tw.zip)
   |     +- class0
   |     |  +-...
   |     +- tag.csv	
   |     +- example.py
   |- ...
   ```

3. Install all the dependencies and run `python server.py`.
4. Connect to `127.0.0.1:8080` in a browser.
5. To terminate the server, `Ctrl+C`.