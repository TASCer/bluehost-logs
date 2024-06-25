![TASCS LOGO](./assets/logo.png)

# Bluehost Apache Weblog Parser version: 1.0.1
### Using Python 3.10.2 with MySQL 5.7.20-log
###### Source IP to Country Name provided by IPWhois utility get_countries
###### Depdendancies noted in requirements.txt

1. Securely (passphrased private cert) download compressed Apache weblogs from hosting provider
    * Windows uses: Putty Pageant 0.80
    * Linux uses: ssh-agent 
1. Decompress and save server log files locally 
1. PARSE log files
1. LOAD unique sources from parsed logs into sources table
    * New entries into lookup table will have a NULL COUNTRY and DESCRIPTION value
1. LOAD parsed logs into database logs table
1. Convert ASN country Alpha-2 code to full country name using IPWhois 
1. SET full county names, ASN Descriptions, and ALPHA2 Codes in sources table
     * If IPWhois error during source ip lookup, exception message is entered as country name
     * If country ALPHA2 code not found, log source

---

#### src folder contains: 

* Python files needed to retrieve, process, and store web server logs to a database for analysis

#### assets folder contains:

* 'sample_unzipped_logfile'  with anonymized data
* 'logo.png' for README logo
* A template of mt 'my_secrets.py' secrets file

#### misc folder contains:

* Batch file for running a Scheduled Task in Windows 
            
---

[TASC Solutions LLC](https://www.tascs.net)

#### PRE_LAUNCH TODO's

* [ ] TASC 1 - CREATE 'input' dir and 'zipped_logfiles' subdir in root dir
* [ ] TASC 2 - CREATE 'output' dir and 'unzipped_logfiles' subdir in root dir


