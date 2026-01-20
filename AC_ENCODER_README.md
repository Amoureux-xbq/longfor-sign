# AC 参数生成器说明文档

## 📋 概述

AC 参数是顶象滑块验证码的核心加密参数，用于验证滑动轨迹的真实性。

**格式：** `s_v3#<Base64编码的数据>`

## 🔍 逆向分析过程

### 1. 反混淆 greenseer.js

使用 `greenseerAST.js` 工具反混淆：

```bash
# 安装依赖
npm install @babel/parser @babel/traverse @babel/types @babel/generator

# 运行反混淆
./deobfuscate_greenseer.sh
```

### 2. 核心方法分析

#### `reload()` - 初始化
```javascript
this._ua = "";      // 存储所有事件数据
this._sa = [];      // 存储轨迹点
this.tm = now();    // 起始时间戳
```

#### `start()` - 收集环境信息
```javascript
getTM()    // 时间戳加密
getBR()    // 浏览器信息加密
getLO()    // URL 加密
getCF()    // 随机数加密
getDI()    // 窗口信息加密
getEM()    // 自动化检测加密
getJSV()   // 版本号加密
getTK()    // sid 加密
getSC()    // 屏幕信息加密
```

#### `app(eventType, data)` - 核心方法
```javascript
// 所有加密数据最终都通过这个方法追加到 _ua
// 格式：[事件类型][数据长度(2字节)][加密数据]
this._ua += [eventType, length, data].join("")
this.ua = "s_v3#" + btoa(this._ua)
```

#### 轨迹加密（关键）

**recordSA(event)** - 记录轨迹点
```javascript
var time = now() - this.tm;        // 相对时间
var x = getPageX(event);           // x 坐标
var y = getPageY(event);           // y 坐标
var data = bs4(time) + bs2(x) + bs2(y);  // 编码
this._sa.push(encryptSA(data));    // 加密并存储
```

**sendSA()** - 发送轨迹数据
```javascript
// 遍历 _sa 数组，调用 app(17, data) 更新 ua
this._sa.forEach(data => this.app(17, data));
```

**sendTemp(str)** - 发送最终坐标
```javascript
// str 格式: "x=187&y=67"
var data = bs2(str.length) + bss(str);
this.app(10, encryptTEMP(data));
```

#### 加密算法

**encryptSA** - 轨迹加密
```javascript
var key = 33265;
for (var i = 0; i < data.length; i++) {
    var encrypted = (data[i] ^ key) & 255;
    result.push(encrypted);
    key = encrypted;  // 使用上一个加密值作为下一个密钥
}
```

**encryptTEMP** - TEMP 加密
```javascript
var keyStr = "C6Br4b6f7NgK";
var keyIdx = 44;
for (var i = 0; i < data.length; i++) {
    keyIdx = (keyIdx + 4) % keyStr.length;
    var encrypted = (data[i] ^ keyStr.charCodeAt(keyIdx)) & 255;
    result.push(encrypted);
}
```

**btoa** - 自定义 Base64 编码
```javascript
// 使用顶象自定义字符表
var chars = "XmYj3u1PnvisIZUF8ThR/a6DfO+kW4JHrCELycAzSxleoQp02MtwV9Nd57qGgbKB=";
// 编码逻辑与标准 Base64 相同，只是字符表不同
```

## 💻 Python 实现

### 完整流程

```python
from ac_encoder_v2 import generate_ac

# 轨迹数据（带时间戳）
trajectory = [
    (0, 0, 1737370000000),      # (x, y, timestamp_ms)
    (5, 1, 1737370000020),
    (12, -1, 1737370000040),
    (20, 0, 1737370000060),
    (187, 0, 1737370001000)
]

# 生成 AC 参数
ac = generate_ac(
    trajectory=trajectory,
    x=187,           # 最终 x 坐标
    y=67,            # 最终 y 坐标
    sid="test_sid"   # session id（可选）
)

print(f"AC: {ac}")
# 输出: s_v3#X8Xnl+A7fAkv1MS...
```

### 核心类

```python
class ACEncoder:
    def __init__(self, sid: str = ""):
        self._ua = b""       # 字节数组
        self._sa = []        # 轨迹数据
        self.tm = int(time.time() * 1000)
    
    def recordSA(self, x, y, timestamp):
        """记录轨迹点"""
        relative_time = timestamp - self.tm
        data = self.bs4(relative_time) + self.bs2(x) + self.bs2(y)
        encrypted = self.encryptSA(data)
        self._sa.append(encrypted)
    
    def sendSA(self):
        """发送所有轨迹"""
        for sa_data in self._sa:
            self.app(17, sa_data)
    
    def sendTemp(self, temp_str):
        """发送 TEMP 数据"""
        temp_bytes = self.bss(temp_str)
        data = self.bs2(len(temp_str)) + temp_bytes
        encrypted = self.encryptTEMP(data)
        self.app(10, encrypted)
    
    def getUA(self):
        """生成最终 AC"""
        encoded = self.btoa(self._ua)
        return f"s_v3#{encoded}"
```

## 🎯 关键点

### 1. 事件类型
- `1`: 时间戳 (TM)
- `10`: TEMP 数据（最终坐标）
- `17`: 轨迹点 (SA)

### 2. 数据编码
- `bs2(n)`: 数字转2字节 `[n>>8, n&0xFF]`
- `bs4(n)`: 数字转4字节
- `bss(s)`: 字符串转字节数组

### 3. 轨迹要求
- **时间戳**：必须是毫秒级（`timestamp_ms`）
- **相对时间**：轨迹点时间相对于 `tm`（起始时间）
- **坐标格式**：`(x, y, timestamp_ms)`

### 4. 坐标计算
```python
# 最终提交的坐标
final_x = trajectory[-1][0]              # 轨迹最后一点的 x
final_y = server_y + trajectory[-1][1]   # 服务端 y + 轨迹 y 偏移
```

### 5. TEMP 字符串格式
```python
temp_str = f"x={final_x}&y={final_y}"
```

## 📊 完整示例

```python
#!/usr/bin/env python3
from ac_encoder_v2 import ACEncoder
import time

# 1. 初始化编码器
encoder = ACEncoder(sid="abc123")

# 2. 添加时间戳（可选，简化流程可以跳过）
encoder.getTM()

# 3. 生成并记录轨迹
base_time = int(time.time() * 1000)
trajectory = [
    (0, 0, base_time),
    (10, 1, base_time + 50),
    (25, 0, base_time + 100),
    (45, -1, base_time + 150),
    (187, 0, base_time + 1000)
]

for x, y, timestamp in trajectory:
    encoder.recordSA(x, y, timestamp)

# 4. 发送轨迹数据
encoder.sendSA()

# 5. 发送最终坐标
final_x = 187
final_y = 67
encoder.sendTemp(f"x={final_x}&y={final_y}")

# 6. 生成 AC
ac = encoder.getUA()
print(f"AC: {ac}")
```

## 🔧 注意事项

### 1. 图片缩放
```python
# 注意图片可能被缩放，需要调整坐标
actual_distance = slider_distance + 20  # 偏移量
```

### 2. 轨迹生成
- 使用拟人化轨迹算法（贝塞尔曲线等）
- 添加抖动和回弹
- 时间间隔要合理（不能太快）

### 3. 服务端 Y 坐标
```python
# 优先使用服务端返回的 y 坐标
server_y = captcha_data.get('y', 0)
final_y = server_y + trajectory[-1][1]
```

### 4. SID 参数
```python
# sid 可以从初始化接口获取
sid = captcha_data.get('sid', '')
```

## 📝 文件说明

- `ac_encoder_v2.py`: AC 参数生成器（核心实现）
- `captcha_handler.py`: 验证码处理器（集成 AC 生成）
- `calculate_captcha_params.py`: 参数计算工具
- `greenseerAST.js`: JS 反混淆工具
- `decode_dx.js`: 反混淆后的代码

## ✅ 测试

```bash
# 测试 AC 生成器
python3 ac_encoder_v2.py

# 测试参数计算工具
python3 calculate_captcha_params.py
```

## 🎉 总结

AC 参数生成的核心流程：

1. **初始化** → `reload()`
2. **收集环境信息** → `start()`（可选，简化版可跳过）
3. **记录轨迹** → `recordSA(x, y, t)`
4. **发送轨迹** → `sendSA()` → app(17, data)
5. **发送坐标** → `sendTemp("x=...&y=...")` → app(10, data)
6. **生成 AC** → `getUA()` → `s_v3#` + btoa(_ua)

**关键：** 所有数据都通过 `app(eventType, data)` 追加到 `_ua`，最后 Base64 编码！
