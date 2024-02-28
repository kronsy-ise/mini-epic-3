# ISE EPIC Block 3 Mini Project

Sports Club Administration System




### Running


To run this program, there are some prerequisites

Firstly, install all dependencies
```bash
pip install -r ./clubhub/requirements.txt
```

Then, spin up the database
```bash
docker-compose -f ./db-compose.yml up
```

After this, make all initializing migrations to the database 
Run this every time you make schema changes
```bash
DATABASE_URL="postgres://default_user:password1@localhost:5435/application" python ./clubhub/src/init_database.py
```

Finally, we can run the application
```bash 
DATABASE_URL="postgres://default_user:password1@localhost:5435/application" python ./clubhub/src/main.py
```
