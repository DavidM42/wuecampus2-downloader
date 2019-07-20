# WueCampus2 Downloader

## How to use
1. You need to have python3 installed
2. Get project
    1. clone from git `git clone https://github.com/DavidM42/wuecampus2-downloader`
    2. move into folder e.g. via `cd wuecampus2-downloader`
    3. (Optional: create a virtual environment with `virtualenv venv`)
3. Set your login credentials 
    1. Rename `auth.ini.example` to `auth.ini`
    2. Change username and password in `auth.ini` to your wuecampus2 username and password
4. Install requirements via `pip install -r ./requirements.txt`
5. Run via `python ./cli.py <course name for folder> <link to wuecampus course>`
    * e.g. `python ./cli.py statistik https://wuecampus2.uni-wuerzburg.de/moodle/course/view.php?id=12345`