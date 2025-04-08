# Sifter
a Python script that reads AWS GuardDuty alerts stored as JSON files, extracts relevant fields, and inserts the data into a PostgreSQL database.

Please note: No LLMs were used to generate this code, have coded this project entirely by myself in vim.

## Installation and Usage

Dependencies:


Clone the repo and initialize:

 - `git clone https://github.com/ssolan5/Sifter.git`
 - `cd Sifter`
 
 - Install nix, this will install nix and start the setup process:
    -  `sh <(curl -L https://nixos.org/nix/install)`
    -  Verify installation
       - `nix --version`
    - nix provides a shell environment that allows one to setup and use specified packages, that ends up not messing up the user's existing installs
     
 -  `make run`

In the ensuing nix shell:

The nix shell will open up in the threat feed db directory:

 - `uv run gd_insert_guardduty.py`

If you want to run the script again:

 - `uv run gd_insert_guardduty.py`
 - choose option 7 from the ensuing interactive textual interface



## Closing and clean up

 - After calling exit on the textual interface in python,
this will automatically close the postgreSQL socket and drop the postgreSQL db to clean up the environment.
Now you can exit the nix shell:
 
 - `exit`

In the repository directory:

 - `make clean`

## Future Work


Functionality of most of the additions to nix shell already exists in the `main` branch, 
but has to be made cleaner 

- [ ] Additions to `shell.nix`
	
	- [ ] Check database file status 
		- [ ] if the database already initialized thus would have the user already setup
			- [ ]  check database server status  in the shellHook
				- [ ] if the database server is not running 
					- [ ] start it 
				- [ ] if the database server is running then
					- [ ] do nothing 

	- [x] If database file does not exist
		- [x] Initialize the database 
		- [x] Start the database server
			- [x] create the user 
			- [x] Call `uv run gd_guardduty_alerts.py` 
				- such that the textual interface is initialized after the user calls `make run`
			- [x] handle exiting out of the shell nix in the python file directly 


Functionality of the selected additions for `gd_guardduty_alerts.py` exists in the dev branch.

- [ ] Additions to `gd_guardduty_alerts.py`

	- [x]  Handle different alerts file to pass to the `JSONparser` and place in the database
		- [ ] user input handling and file validation
		- [x] Either create multiple databases or create a new table each time
	- [x] Start and Stop database
		- [x] Textual interface option 
		- [x] commands to `pg_ctl` through `os.system`
	- [x] Parse SQL query results in a nicer format for human readability. 
	- [ ] Make multiple tables for each of the different JSON depths 
		- [ ] show off `SQL JOINs`
		- [ ] have each of the table's primary key be the `id` 

