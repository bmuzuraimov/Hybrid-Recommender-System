# Lab3

## Create an environment (only for Mac and Linux)

```
python3 -m venv .venv
```

## Activate the environment (only for Mac and Linux)

```
. .venv/bin/activate
```

## Install Python packages 

```
pip install --upgrade pip setuptools wheel pyquery
pip install -r requirements.txt
```

## Run the project
```
flask --app flaskr run --debug
```

## Add the recommendation algorithm
You only need to modify the `main.py` file. Its path is as follows:
```
path: /flaskr/main.py
```