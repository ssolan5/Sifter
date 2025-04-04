# Sifter
a Python script that reads AWS GuardDuty alerts stored as JSON files, extracts relevant fields, and inserts the data into a PostgreSQL database.

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

In the ensueing nix shell:

The nix shell will open up in the threat feed db directory:

 - `uv run gd_insert_guardduty.py`



## Closing and clean up

 - After calling exit on the textual interface in python,
this will automatically close the postgreSQL socket and drop the postgreSQL db to clean up the environment.
Now you can exit the nix shell:
 
 - `exit`

In the repository directory:

 - `make clean`



