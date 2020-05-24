# Install

```
pip3 install catapult3
```

После этого вам будет доступна утилита `catapult`

Деплой можно запустить как в CLI режиме, так и поднять web-server, который будет выполнять запросы на деплой.

# Services

Для работы Catapult, вам необходимо создать директорию и поместить в нее файл `config.yml`, в котором будет находиться конфигурация деплой сервера в формате YAML.

В этой же директории создайте директорию с именем `services`. Каждая директория в `services` - это сервис, который можно будет деплоить. Имя директории - это имя сервиса для деплоя.

Директория-сервис содержит файл `config.yml`, описывающий настройки деплоя сервиса. Так, например, вам необходимо будет указать список мест, куда может деплоиться ваш сервис - `place` (это могут быть стейдж и продакшн сервера). И, по необходимости, директорию `shared` с произвольным содержимым.

Директория `recipes` может содержать дополнительные рецепты (набор инструкций) для деплоя сервисов. Рецепты пишутся на языке Python.


# Command Line Interface

| short flag |  full flag  | required | description                                       |
|:----------:|:------------|:--------:|:--------------------------------------------------|
|            | --project   | no       | full path for folder with catapult deploy project |
| -s         | --service   | yes      | name of service                                   |
| -b         | --branch    | yes      | name of branch or tag                             |
| -p         | --place     | yes      | name of place                                     |
|            | --force     | yes      | is force deploy?                                  |
|            | --command   | yes      | command will be executed on maintain server       |
|            | --parameter | yes      | environment parameter ("key:value")               |

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