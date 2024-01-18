![TASCS LOGO](./assets/logo.png)

# Shared Bluehost Activity Log Parser
Using Python 3.10 with MySQL 5.7.20-log with country name list data provided by IPWhois utility get_countries
Depdendancies noted in requirements.txt

1. Securely download compressed log files from website hosting provider using Putty Pageant 0.80
2. Decompress and save server log files locally 
3. PARSE exported log files
4. LOAD unique sources from parsed logs into sources table
        - New entries into lookup table will have a NULL COUNTRY and DESCRIPTION value
5. LOAD parsed logs into database logs table
6. Convert ASN country Alpha-2 code to full country name using IPWhois 
7. SET full county names, ASN Descriptions, and ALPHA2 Codes in sources table
     a. If IPWhois error during source ip lookup, exception message is entered as country name
     b. If country ALPHA2 code not found, log source

src folder contains: 

        1. Python files needed to retrieve, process, and store web server logs to  database for analysis

assets folder contains:

        1. 'sample_unzipped_logfile'  with anonymized data
        2. 'logo' for README
        3, A sample_my_secrets.py secrets template
        4. File(s) for scheduled running
            

