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
docker-compose -f ./docker-compose.yml up
```

After this, make all initializing migrations to the database 
```bash
python ./clubhub/src/init_database.py
```


Finally, we can run the application
```bash 
python ./clubhub/src/main.py
```
