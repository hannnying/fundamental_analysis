


## Ensure You're in the Correct Directory  
Make sure you're in the `fastAPI` directory before running any scripts. 

## Preloading Data into the Database
Currently, there are issues with running this script from /fastAPI as can't find the modules to be imported

```bash
python /internal/preload.py
```

## Starting the Application
To start the application, run

```bash
python -m uvicorn app.main:app --reload
```


