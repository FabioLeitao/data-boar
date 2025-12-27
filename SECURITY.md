# Security Policy

## Supported Versions

Any Python3 version after 3.6 (tested on 3.13),... 

* uv 
* pip 
* Flask
* Flask-SQLAlchemy
* ReportLab
* Psycopg2 or MySQL Connector (depending on your database)
* SQLite3

#### Prereqs

1. sudo apt -y install libsqlcipher-dev libsqlclient-dev libsqlite3-dev sqlite3 sqlite3-tools mariadb-plugin-connect python3-mariadb-connector dbconfig-mysql
2. sudo apt -y install libmariadbd-dev libmariadb-dev
3. uv venv
4. source .venv/bin/activate
5. uv self update
6. uv add -r requirements.txt
7. uv sync
8. uv run ./lgpdc.py


## Reporting a Vulnerability

You can submit a vunerability issue by creating in Issues tab.
