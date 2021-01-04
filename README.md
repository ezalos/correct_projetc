# Correct your Projects!

## Installation

```sh
git clone https://github.com/ezalos/correct_projetc.git          
cd correct_projetc
wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
tar -xvzf geckodriver*
chmod +x geckodriver
export PATH=$PATH:`pwd`
cp config.py.template config.py
vim config.py
```

## Usage

```sh
pyhton3 correct_me.py -h
```

## Suggestion of my preferred options

```sh
python3 correct_me.py -s -t 11h00-21h00 -r malloc
```
