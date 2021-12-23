# Correct your Projects!

Did you already dreamed of getting correction slots for your project without the tedious task of continuously refreshing the agenda ?

Your needs have been heard and this repository is here for you !

## Installation

Install depedencies for the project:

```sh
pip3 install -r requirements.txt
```

This project makes use of a browser entirely controllable by code.
As such you need to download the `geckodriver` in the project directory.

The latest version can be found here: [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases)


For example for Linux the latest version (as of december 2021) can be downloaded and extracted this way:

```sh
wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz
tar -xvzf geckodriver*
chmod +x geckodriver
```

## Usage

`geckodriver` needs to be in the `PATH`

```sh
export PATH=$PATH:`pwd`
```

Then, to launch the script:

```sh
python3 correct_me.py -s -t 11h00-21h00
```

It will look for one slot this week between 11AM and 9PM for any locked project.


A precise usage of the program can be accessed this way:

```sh
pyhton3 correct_me.py --help
```