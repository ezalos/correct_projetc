import os
from getpass import getpass

ENV_42_USER = "USERNAME_42"
ENV_42_PASS = "PASSWORD_42"

login = {
    "user" : "user",
    "password" : "pass"
}

if ENV_42_USER in os.environ:
	login["user"] = os.environ[ENV_42_USER]
else:
	login["user"] = input(f"Please input your 42 username: ")

if ENV_42_PASS in os.environ:
	login["password"] = os.environ[ENV_42_PASS]
else:
	login["password"] = getpass(f"Please input your 42 password: ")

