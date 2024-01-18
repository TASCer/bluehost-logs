![TASCS LOGO](./assets/logo.png)

# Shared Bluehost Activity Log Parser
Using Python 3.10 with MySQL 5.7.20-log with country name list data provided by IPWhois utility get_countries
Depdendancies noted in requirements.txt

1. Securely download compressed log files from website hosting provider
2. Decompress log files 
3. PARSE exported log files
4. LOAD unique sources from parsed logs into sources table
        - New entries into lookup table will have a NULL COUNTRY and DESCRIPTION value
5. LOAD parsed logs into database logs table
6. Convert ASN country Alpha-2 code to full country name using IPWhois 
7. SET full county names, ASN Descriptions, and ALPHA2 Codes in sources table
     a. If IPWhois error during source ip lookup, exception message is entered as country name
     b. If country ALPHA2 code not found, log source
8. Visuals of webserver activity saved in output directory

src folder contains: 

        1. Python files needed to run analysis

assets folder contains:

        1. sample_log with 1 day of my webserver anonymized logfile (testlog.csv)
        2. Logo for README
        3, A my_secrets file template
        4. Batch file for scheduled running
        

