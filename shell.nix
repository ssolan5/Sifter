let
   # Tried to follow documentation on shell.nix of nix's own docs and the packages
   # in this tarball were outdated
   
   # nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-24.05";

   pkgs = import <nixpkgs> {}; 

   # { config = {}; overlays = []; };
in
pkgs.mkShell {

    packages = with pkgs; [
	
		# Adding the packages for the shell here
		
                postgresql
                python3
                uv
                libpq
                cowsay
        	lolcat
                git
                coreutils 

    ];
 
    GREETING = " Hello World!! ^--^ !! ! ";
    ALERTS_REPO = "GuarddutyAlertsSampleData/";
    DB_DIR=".tmp/db";
    PGDATA="";


    shellHook = ''

      COMMAND_OUTPUT=$(uv init threat_feed_db 2>&1)

      if [[ $? -eq 0 ]]; then
 
            cd threat_feed_db
            uv add psycopg2-binary
 
            # Exiting out of the uv repo after adding dependencies
	    cd ..
 

      # else 

            # echo "$COMMAND_OUTPUT" | cowsay -f hellokitty | lolcat 

      fi

      echo $GREETING | cowsay -f hellokitty | lolcat
 
      # Cloning the Guard Duty sample alerts json repo
 
      if test -d "$ALERTS_REPO"; then 

          echo "GuarddutyAlertsSampleData exists!" | cowsay -f hellokitty | lolcat

      else 

          git clone https://github.com/vkatariaairisec/GuarddutyAlertsSampleData.git

      fi

      # Initializing the database
      
      # Adapting https://mgdm.net/weblog/postgresql-in-a-nix-shell/
      # for shell hook
 
      if test -d "$DB_DIR"; then 

          echo "Database is already initialized so not creating again" | cowsay -f hellokitty | lolcat
	  # checkCommand=$(pg_ctl -D . stop)
          # if [[ $checkCommand == "*Is server running?*" ]]
 


      else

          cd $DB_DIR

          mkdir -p $DB_DIR
          cd $DB_DIR

          # Initializing database files
          initdb -D .
          
          # TODO : debug unix socket directories issue
          # awk -i inplace '{ sub(/\/tmp/,ENVIRON["PGDATA"],$3) }1' postgresql.conf 

 
          # Check if that port is not already being used for PGSQL 
          # connections or a remnant from before -- test runs  

          echo "Checking if someone is already using the socket for the server" | cowsay -f hellokitty | lolcat

          # checkCommand=$(pg_ctl -D . stop)
          # if [[ $checkCommand == "*Is server running?* || $checkCommand == "*server stopped*" ]]


          echo "PostgreSQL Server starting ! !! " | cowsay -f hellokitty | lolcat 

	  # Starts a PostGreSQL server 
	  pg_ctl -D . -l logfile start   
          
          # Intialize my database "db" in database
	  # TODO: debug socket files, setting up PGDATA
          # createdb db -h "$(pwd)"

          createdb gd_security_alerts
          psql -d gd_security_alerts -c "CREATE USER postgres WITH SUPERUSER PASSWORD 'password';" 

      fi

      # Once the database is initialized and status checked
      # move out of the directory to the python repo

      cd ../../threat_feed_db
    '';
}
    
     

	


        
        
