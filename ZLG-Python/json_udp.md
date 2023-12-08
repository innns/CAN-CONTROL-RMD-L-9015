# JSON 通信协议

[json 在线工具](https://c.runoob.com/front-end/53/)

## 设置当前角度 `angel`

|   key   |       value       |    注释     |
|:-------:|:-----------------:|:---------:|
|  "cmd"  |      "angel"      |  设置角度命令   |
|  "id"   |  (int) motor_id   |   电机的id   |
| "angel" | (float) des_angel | 期望的角度，角度制 |

```json
{
  "cmd": "angel",
  "id": 1,
  "angel": 34.56
}
```

## 获取当前角度 `read`

|  key  |     value      |   注释   |
|:-----:|:--------------:|:------:|
| "cmd" |     "read"     | 读取角度命令 |
| "id"  | (int) motor_id | 电机的id  |

```json
{
  "cmd": "read",
  "id": 1
}
```

## 切换工作模式 `switch`

|  key  |   value   |   注释   |
|:-----:|:---------:|:------:|
| "cmd" | "switch"  | 切换工作模式 |
| "mod" | (int) mod | 电机工作模式 |

- `mod == 0` 代表控制位置模式，电机内部参数设置为跟随设定的角度运动
- `mod == 1` 代表读取位置模式，电机回到零位，根据电机的位置反馈不同扭矩

```json
{
  "cmd": "read",
  "id": 1
}
```

## 清空UDP缓冲 `clear`

|  key  |  value  |   注释    |
|:-----:|:-------:|:-------:|
| "cmd" | "clear" | 清空UDP缓冲 |

```json
{
  "cmd": "clear"
}
```

## 设置pid `set_PID`

**一般不要改动pid**

|  key   |       value        |        注释         |
|:------:|:------------------:|:-----------------:|
| "cmd"  |     "set_PID"      |      设置pid参数      |
|  "id"  |   (int) motor_id   |       电机的id       |
|  "cp"  |     (uint8) cp     |       电流环kp       |
|  "ci"  |     (uint8) ci     |       电流环ki       |
|  "sp"  |     (uint8) sp     |       速度环kp       |
|  "si"  |     (uint8) si     |       速度环ki       |
|  "pp"  |     (uint8) pp     |       位置环kp       |
|  "pi"  |     (uint8) pi     |       位置环ki       |
| "save" | (bool) save_to_ROM | 是否保存到ROM（默认false） |

pid参数都是归一化到`0-255`的，`255`代表参数为设定的最大值

```json
{
  "cmd": "set_PID",
  "id": 1,
  "cp": 120,
  "ci": 80,
  "sp": 120,
  "si": 40,
  "pp": 60,
  "pi": 0,
  "save": false
}
```

## 复位并关闭电机 `close_motor`

|  key  |     value      |   注释    |
|:-----:|:--------------:|:-------:|
| "cmd" | "close_motor"  | 复位并关闭电机 |
| "id"  | (int) motor_id |  电机的id  |

```json
{
  "cmd": "close_motor",
  "id": 1
}
```

## 退出程序 `close_ALL`

|  key  |    value    |  注释  |
|:-----:|:-----------:|:----:|
| "cmd" | "close_ALL" | 退出程序 |

```json
{
  "cmd": "close_ALL"
}
```

