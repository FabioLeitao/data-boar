# python\_lgpd\_crawler

Dashboard com capacidade de sondagem, apreciação e mapeamento dos dados pessoais e/ou sensíveis para busca de violações de compliance de acordo com as recomendações do LGPD (adaptável mediante dicionário de regras)

Web application that scans **databases** (for now) for compliance violations according to **LGPD** and other regulations. Implemented in Python3 with Flask for the backend and HTML/CSS/JavaScript for the frontend.


##### Implementation:

###### Solution Overview

1. **Dashboard** - Shows compliance status and scan results

2. **Scanner** - Connects to databases and identifies sensitive data

3. **Configuration** - Manages database connections and scan settings

###### Frontend 

The application includes three main pages:

1. **Dashboard** (index.html):

* Shows compliance requirements and current status
* Lists all configured databases
* Shows recent scan results

2. **Scanning** (scan.html):

* Interface to start scans
* Shows scan progress

3. **Configuration** (config.html):

* Form to add new database connections
* List of existing configurations


##### TODO:

###### Key goals!

1. Database Connection Management:

* Supports PostgreSQL and MySQL (mariaDB)
* Stores configuration securely

2. Compliance Checking:

* Checks for common compliance requirements
* Identifies sensitive data patterns (email, phone, CPF, gender, etc.) via some form of regex

3. Reporting:

* Generates local database indicating finds and possible vectors of violations of privacy
* Generates detailed PDF reports of quantities, locations...
* Summarizes findings and compliance status including some sort of risc score (TBD)

4. User-Friendly Interface:

* Clean dashboard showing scan history (including age of last data gathering)
* Progress tracking for ongoing scans (if so possible)
* Easy configuration management (credentials, DBE flavor (and connector), subsets, etc.)

###### How to Extend This Solution?

1. Add More Compliance Requirements:

* Add additional checks to the COMPLIANCE\_REQUIREMENTS dictionary (such as GDPR or CCPA) besides the current LGPD

2. Implement Actual Database Scanning:

* Connect to real databases using the get\_db\_connection function
* Scan tables for further sensitive data patterns (via some form of regex) eigther collumn name or actual record

3. Add More Data Types:

* Expand the PersonalDataPattern class to include more patterns (personal or sensitive data), not hardcoded if feasable
* Add support for different languages and name formats (mostly latin based, but not only, due to the international nature of the target company)
* Add support for different data base engines, such as MS SQL, Oracle, etc. (including their connectors, data sets, schemas, etc)
* Add support for different data inputs types besides BDE, such as DBF, CSV, XLS, XLSX, ODP, PMDX files, emails or forms that might also store personal and/or sensitive data
* Add support for some sort of API integration (SOAP or REST) to gather such data where available (many systems and/or solutions might already expose data bases for other intentions that might assist us)

4. Enhance Reporting:

* Add more detailed statistics to reports based on authoritative feedbacks
* Include database schema diagrams with forein keys connections, and cross reference of "possible same individual" as data gets unhidden (further indication of risc assestment)
