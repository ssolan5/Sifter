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
                

    ];
 
    GREETING = " Hello World!! ^--^ !! ! ";
    ALERTS_REPO="GuarddutyAlertsSampleData/";

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

      DB_DIR=".tmp/db"
      PGDATA="$DB_DIR"

      if test -d "$DB_DIR"; then 

          echo "Database is already initialized so not creating again" | cowsay -f hellokitty | lolcat

          cd $DB_DIR

          if [[ $(ls -al .s.PGSQL.5432) ]]; then

	      echo "Socket file exists, need to clean up; stop and start server " | cowsay -f hellokitty | lolcat 
              
              # TODO: Need to make a check here with pg_ctl status

              # If server has already started then stop it 
              pg_ctl -D . stop
              
              # Restart the server as socket may or may not 
              # be stuck anymore
              pg_ctl -D . -l logfile -o "--unix_socket_directories='$PWD'" start

              echo "Server should be started now?1?!?!?" | cowsay -f hellokitty | lolcat

           else

               pg_ctl -D . -l logfile -o "--unix_socket_directories='$PWD'" start

           fi
 
      else

          mkdir -p $DB_DIR
          cd $DB_DIR

          # Initializing database files
          initdb -D .
 
          # Check if that port is not already being used for PGSQL 
          # connections or a remnant from before -- test runs  

          echo "PostgreSQL Server starting ! !! was not on previously " | cowsay -f hellokitty | lolcat 

	   # Starts a PostGreSQL server 
	   pg_ctl -D . -l logfile -o "--unix_socket_directories='$PWD'" start
	   
           # Intialize my database "db" in database
	   createdb db -h "$(pwd)"

      fi

      # Once the database is initialized and status checked
      # move out of the directory to the python repo

      cd ../../threat_feed_db
    '';
}
    
     

	


        
        
