## for developers

```
python3 -m venv ./venv
```

```
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:[absolute path to catapult folder]
```

```
pip install -r requirements.txt
pip freeze > requirements.txt
```

# upgrade packages

```bash
pipupgrade --all
```