Created by [@IlyaShirko](https://github.com/ilyashirko)  

# Vacancies parser  
This app is made for parsing [HeadHunter](https://hh.ru/) and [SuperJob](https://superjob.ru/).  
It take salary statistic for 10 most popular programm languages.  
Location - Moscow.  
Currency - RUB.  

## How to install
for installing app clone it from git, go to the root folder, make and activate env and install dependencies:
```
$ git clone https://github.com/ilyashirko/devman_edu_api_5
$ cd devman_edu_api_5
$ python3 -m venv env
$ source env/bin/activate
$ pip3 install -r requirements.txt
```
You should get SuperJob secret key [from here](https://api.superjob.ru/)
You also needs user_agent for HeadHunter. You can take it [here](https://www.whatsmyua.info/)
Create `.env' file and put data there:
```
SJ_SECRET_KEY=v3.r.2lkjl2k3j4l2kj34lkjlkjl2kjl23423423423.a2342342kj4h2kj3h4k2j346cc67626a13fd
USER_AGENT={your_user_agent}
```

## how to launch
from root folder write in terminal
```
$ python3 main.py
```
You will see 2 progress bar and then you will get a table with all available statistic.