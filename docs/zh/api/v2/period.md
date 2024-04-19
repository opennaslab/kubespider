# period

## 简介

kubespider支持通过指定binding配置来创建周期性运行的任务

## api

headers: {"Authorization":"bearer {your token}"}

### 查询周期任务列表 /api/v2/period [GET]

```json
{
    "code": 200,
    "data": [
        {
            "arguments": {
                "keyword": "寄生兽"
            },
            "bindings": [
                {
                    "id": 1,
                    "name": "mt"
                }
            ],
            "enable": false,
            "id": 1,
            "name": "search test",
            "task_type": "search",
            "tigger_config": {
                "hours": 0,
                "minutes": 0,
                "seconds": 10
            },
            "tigger_type": "interval"
        }
    ],
    "msg": "Ok"
}
```

### 创建/更新周期任务 /api/v2/period [POST]

入参示例: interval类型的周期任务,带id为更新,不带id为新增
todo: 支持date,cron类型的周期任务

```json
{
    "name": "search test",
    "task_type": "search",
    "arguments": {
        "keyword": "寄生兽"
    },
    "tigger_type": "interval",
    "tigger_config": {
        "hours": 0,
        "minutes": 0,
        "seconds": 60
    },
    "bindings": [1,2],
    "id":1
}
```

```json
{
    "code": 200,
    "data": null,
    "msg": "Ok"
}
```

### 删除周期任务 /api/v2/period/<int:task_id> [DELETE]
```json
{
    "code": 200,
    "data": null,
    "msg": "Ok"
}
```
### 启用/禁用周期任务 /api/v2/period/operate [PUT]

```json
{
    "id":1,
    "enable":true
}
```

```json
{
  "code": 200,
  "data": null,
  "msg": "Ok"
}
```