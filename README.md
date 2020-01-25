# autosync
Automatically transfer reports to central server

# Installation instructions

## Get a copy of the application

1. Clone the application from github and `cd` into it

    ```bash
    $ git clone https://github.com/EGPAFMalawiHIS/autosync
    $ cd autosync
    ```

2. Copy the configuration file as follows:

    ```bash
    $ cp .env.example .env
    ```

3. Edit the new `.env` configuration file, setting the values accordingly:

    - Edit the SERVER and PORT options to point to a running instance of the [autosync receiver](https://github.com/EGPAFMalawiHIS/autosync_receiver)
    - Set the ENCRYPTION KEY
    - Set the REPORTING_API_TYPE to either `emr` or `emastercard`. This depends on what application you want to pull reports from.
    - Then set REPORTING_API_PROTOCOL to either `http` or `https`; REPORTING_API_HOST and REPORTING_API_PORT to the address of a running application server instance respectively.
    - Depending on your target application server you may need to set up a login username and password. For the [BHT-EMR-API](https://github.com/HISMalawi/BHT-EMR-API) you definitely have to set up one but take note that the
    username can not be used for other login as the API does not allow multiple logins at once.

4. Edit site.txt to set the facility the application will be reporting from (details will be provided from where ever the autosync receiver is running)

    - Set the SITECODE, SITENAME, and DISTRICT (don't mess these up) 

5. Run the installation script

    ```bash
    $ chmod +x install.sh
    $ sudo ./install.sh
    ```

   This creates an `autotransfer` directory in your home directory where the application will run from.

6. Check that the application is running with systemctl

    ```bash
    $ sudo systemctl status autotransfer.service
    ```

7. Check that the are no errors in the log file

    ```bash
    $ sudo view ~/autotranfer/sms_send.log
    ```

 


