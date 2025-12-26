# python\_lgpd\_crowler

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

* Supports PostgreSQL and MySQL
* Stores configuration securely

2. Compliance Checking:

* Checks for common compliance requirements
* Identifies sensitive data patterns (email, phone, CPF, etc.)

3. Reporting:

* Generates detailed PDF reports
* Summarizes findings and compliance status

4. User-Friendly Interface:

* Clean dashboard showing scan history
* Progress tracking for ongoing scans
* Easy configuration management

###### How to Extend This Solution?

1. Add More Compliance Requirements:

* Add additional checks to the COMPLIANCE\_REQUIREMENTS dictionary (such as GDPR or CCPA) besides the current LGPD

2. Implement Actual Database Scanning:

* Connect to real databases using the get\_db\_connection function
* Scan tables for sensitive data patterns

3. Add More Data Types:

* Expand the PersonalDataPattern class to include more patterns (personal or sensitive data)
* Add support for different languages and name formats
* Add support for different data base engines, such as MS SQL, Oracle, etc
* Add support for different data inputs types, such as DBF, CSV, XLS, XLSX, ODP, PMDX files

4. Enhance Reporting:

* Add more detailed statistics to reports
* Include database schema diagrams
