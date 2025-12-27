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

1. sudo apt install libsqlcipher-dev libsqlclient-dev libsqlite3-dev sqlite3 sqlite3-tools mariadb-plugin-connect python3-mariadb-connector dbconfig-mysql
2. uv venv
3. source .venv/bin/activate
4. uv self update
6. uv sync
7. uv run ./lgpdc.py


## Reporting a Vulnerability

You can submit a vunerability issue by creating in Issues tab.
