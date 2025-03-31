# Sifter
a Python script that reads AWS GuardDuty alerts stored as JSON files, extracts relevant fields, and inserts the data into a PostgreSQL database.

## Installation and Usage

Clone the repo and initialize:

 - `git clone https://github.com/ssolan5/Sifter.git`
 - `cd Sifter`
 - `make run`

In the ensueing nix shell:
 
 - `cd threat_feed_db`
 - `uv run gd_insert_guardduty.py`


