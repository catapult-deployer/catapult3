# Command Line Interface


| short flag |  full flag  |                                       description |
|:----------:|:------------|:--------------------------------------------------|
|            | --project   | full path for folder with catapult deploy project |
| -s         | --service   | name of service                                   |
| -b         | --branch    | name of branch or tag                             |
| -p         | --place     | name of place                                     |
|            | --force     | is force deploy?                                  |
|            | --command   | command will be executed on maintain server       |
|            | --parameter | environment parameter ("key:value")               |

```
catapult deploy -s analytics -p production -b master --project ../deploy --force --command "./artisan clear:cache" --command "./artisan config:clear" --parameter "param1:value" --parameter "param2:value"
```

# Rest Api


## Make release

End-point

```
POST /releases
```

Accepts json-structure with params

| name       | is required? | type    | description                       |
|:----------:|:------------:|:-------:|:----------------------------------|
| service    | true         | string  | Name of service                   |
| branch     | true         | string  | Name of branch or tag             |
| place      | true         | string  | Name of place                     |
| force      | false        | boolean | Is force deploy?                  |
| commands   | false        | list    | List of strings of commands       |
| parameters | false        | object  | Object with key-value parameters  |

Example

```
curl -H "X-Token: oShEb1mMmvdeLHVMfDvgQgFWKuprWrsdXke" -d '{"service": "core", "branch": "master", "place": "prod"}' -X POST http://localhost:5000/releases
```

Result returns

```json
{
  "isSuccess": true,
  "data": {
    "release_name": "1544134318_core_master"
  }
}
```

## Get information about release

End-point

```
GET /releases/{release-name}
```

Example

```
curl -H "X-Token: oShEb1mMmvdeLHVMfDvgQgFWKuprWrsdXke" -X GET http://localhost:5000/releases/1544134318_core_master
```

Result returns

```json
{
  "isSuccess": true,
  "data": {
    "name": "1544134318_core_master",
    "request": {
      "branch": "master",
      "commands": [],
      "force": true,
      "parameters": {},
      "place": "prod",
      "service": "core",
      "name": "1544134318_core_master",
      "time_start": 1544134442
    },
    "status": "pending",
    "logger": [],
    "time_end": null
  }
}
```


#### for developers


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