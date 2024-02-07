![TASCS LOGO](./assets/logo.png)

# Shared Bluehost Activity Log Parser
Using Python 3.10 with MySQL 5.7.20-log with country name list data provided by IPWhois utility get_countries
Depdendancies noted in requirements.txt

1. Securely download compressed log files from website hosting provider using Putty Pageant 0.80
1. Decompress and save server log files locally 
1. PARSE exported log files
1. LOAD unique sources from parsed logs into sources table
        - New entries into lookup table will have a NULL COUNTRY and DESCRIPTION value
1. LOAD parsed logs into database logs table
1. Convert ASN country Alpha-2 code to full country name using IPWhois 
1. SET full county names, ASN Descriptions, and ALPHA2 Codes in sources table
     * If IPWhois error during source ip lookup, exception message is entered as country name
     * If country ALPHA2 code not found, log source

#### src folder contains 

        Python files needed to retrieve, process, and store web server logs to a database for analysis

#### assets folder contains:

        * 'sample_unzipped_logfile'  with anonymized data
        * 'logo.png' for README logo
        * A sample_my_secrets.py secrets template
        * File(s) for scheduled running
            
[TASC Solutions LLC](https://www.tascs.net)

* [x] TASC 1 - CREATE README
* [ ] TASC 2 - Update README w/ code blocks
