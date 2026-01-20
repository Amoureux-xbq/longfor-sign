# 龙湖天街滑块验证码自动识别

## ⚠️ 重要发现：背景图需要还原！

**最新问题**：验证失败返回 `POSITION_MISMATCH`，原因是**背景图是乱序的**！

### 问题分析
```
❌ 当前流程：
   乱序背景图 → 直接识别 → x=95 (错误) → 验证失败

✅ 正确流程：
   乱序背景图 → 还原成正常图 → 识别 → x=120 (正确) → 验证成功
```

### 参考资料
- [验证码底图还原 - 极验/完美滑块](https://www.ayuge.top/mkdocs-material/tiny/mds/验证码底图还原/)
- JavaScript 代码中有 canvas 切片重组逻辑

### 解决方案（进行中）
1. ✅ 已创建 `image_restore.py` - 图片还原模块
2. ✅ 已创建 `extract_slice_order.py` - 切片顺序分析工具
3. ⏳ 需要从 JavaScript 中提取切片顺序数组
4. ⏳ 集成到识别流程

### 临时解决方法
```bash
# 分析下载的背景图
python extract_slice_order.py analyze bg_temp.png

# 尝试常见的乱序模式
python extract_slice_order.py try bg_temp.png

# 查看提取指南
python extract_slice_order.py guide
```

---

## 工作原理

当签到接口返回需要验证码时（错误码 `8040012` 或 `8040016`），程序会自动：

1. **检查验证类型** - 调用 `devops-prod.longfor.com/v2/api/uv/type` 确认需要什么验证
   - 返回 `"c"` 表示需要 captcha（滑块验证）
2. **初始化验证码** - 调用 `/api/a` 获取 sid、challenge 和图片URL
3. **下载图片** - 下载背景图 (p1) 和滑块图 (p2)
4. **识别缺口** - 使用 OpenCV 的边缘检测和模板匹配
5. **生成轨迹** - 模拟人类滑动行为（加速→减速→抖动）
6. **编码数据** - 将轨迹编码为 ac 参数
7. **提交验证** - 发送到 `/api/v1` 获取验证 token
8. **重新签到** - 使用验证 token 再次调用签到接口

## 完整请求流程

### 正常签到（无验证码）
```
POST /openapi/task/v1/signature/clock
→ {"code": "0000", "data": {...}}  ✓ 签到成功
```

### 触发验证码时
```
1. POST /openapi/task/v1/signature/clock
   → {"code": "8040012", "message": "网络故障，请稍后再试"}

2. GET /v2/api/uv/type?appId=LdIPdF3earg
   → {"code": "200", "data": "c"}  # c = captcha

3. GET /api/a?w=300&h=150&s=50&ak=xxx&c=xxx&...
   → {
       "sid": "xxx",
       "y": 67,
       "success": true,
       "p1": "/api/p1?sid=...",
       "p2": "/api/p2?sid=...",
       "result": 1
     }

4. GET /api/p1?sid=xxx&...  # 下载背景图
   → <图片数据>

5. GET /api/p2?sid=xxx&...  # 下载滑块图
   → <图片数据>

6. [本地处理] 图像识别 + 轨迹生成

7. POST /api/v1
   data: {
     "ac": "base64编码的轨迹",
     "ak": "xxx",
     "c": "challenge",
     "sid": "xxx",
     "aid": "xxx",
     "x": 187,
     "y": 67
   }
   → {"success": true, "token": "19BDA2..."}

8. POST /openapi/task/v1/signature/clock
   headers: {
     "X-LF-DXRisk-Captcha-Token": "19BDA2...",
     "X-LF-DXRisk-Source": "5"
   }
   → {"code": "0000", "data": {...}}  ✓ 签到成功
```

## 安装依赖

```bash
pip install opencv-python numpy requests
```

## 文件结构

```
longfor-sign/
├── longfor.py              # 主签到逻辑（已集成验证码处理）
├── captcha_handler.py      # 验证码处理器
├── image_recognition.py    # 图像识别模块
├── trajectory.py           # 轨迹生成模块
├── ac_encoder.py          # AC参数编码模块
└── main.py                # 主入口
```

## 使用方法

### 方式1：正常签到（自动处理验证码）

```bash
export LONGFOR_TOKEN="你的token"
export LONGFOR_DXRISK_TOKEN="你的dxrisk_token"
python main.py
```

如果触发验证码，程序会自动处理。

### 方式2：单独测试验证码识别

```python
from captcha_handler import CaptchaHandler

handler = CaptchaHandler(
    token="你的token",
    dxrisk_token="你的dxrisk_token"
)

# 测试完整流程
result = handler.handle_captcha_if_needed()
print(f"验证结果: {result}")
```

### 方式3：测试图像识别

```python
from image_recognition import find_gap_position

# 使用调试模式，会保存中间结果图片
x, y = find_gap_position(
    "bg_temp.png", 
    "slider_temp.png",
    debug=True
)
print(f"缺口位置: x={x}, y={y}")
```

## 调试技巧

### 1. 查看识别过程

在 `captcha_handler.py` 中修改：

```python
# 在 solve_captcha 方法中
x, y = find_gap_position(bg_path, slider_path, debug=True)
```

这会生成：
- `debug_bg_edges.png` - 背景边缘图
- `debug_slider_edges.png` - 滑块边缘图
- `debug_result.png` - 标记位置的结果图

### 2. 查看轨迹数据

```python
from trajectory import generate_trajectory, add_shake_at_end

traj = generate_trajectory(187)  # 187px距离
traj = add_shake_at_end(traj)

print(f"轨迹点数: {len(traj)}")
for i, (x, y, t) in enumerate(traj[:10]):
    print(f"{i}. x={x}, y={y}, t={t}ms")
```

### 3. 查看AC参数编码

```python
from ac_encoder import encode_ac_parameter
import base64

ac = encode_ac_parameter(trajectory)
print(f"AC长度: {len(ac)}")

# 解码查看
decoded = base64.b64decode(ac).decode()
print(f"解码内容: {decoded}")
```

## 参数调优

### 图像识别精度

在 `image_recognition.py` 中调整 Canny 参数：

```python
# 原值：50, 150
bg_edges = cv2.Canny(bg_gray, 50, 150)  
slider_edges = cv2.Canny(slider_gray, 50, 150)

# 如果识别不准，可以尝试：
# - 提高阈值: 100, 200 (减少噪点)
# - 降低阈值: 30, 100 (增加边缘)
```

### 轨迹生成

在 `trajectory.py` 中调整参数：

```python
# 加速阶段的加速度
a = random.randint(2, 5)  # 增大 = 更快到达

# 减速阶段的加速度
a = -random.randint(3, 5)  # 增大 = 更早开始减速

# Y轴抖动幅度
y_offset = random.randint(-2, 2)  # 增大 = 更明显的抖动
```

## 常见问题

### 1. 识别不准确

**原因**：
- 图片质量问题
- 边缘检测参数不合适
- 滑块形状特殊

**解决**：
- 开启 debug 模式查看边缘图
- 调整 Canny 参数
- 尝试多次识别取最优结果

### 2. 验证失败

**原因**：
- AC 参数编码格式不正确
- 轨迹太机械化
- 时间太快/太慢

**解决**：
- 对比真实抓包的 ac 参数格式
- 增加轨迹随机性
- 调整速度参数

### 3. 仍然提示需要验证

**原因**：
- 验证 token 未正确添加到请求头
- token 已过期
- 风控策略升级

**解决**：
- 检查 `X-LF-DXRisk-Captcha-Token` 头是否正确添加
- 确认 token 格式完整
- 可能需要更新 AC 编码算法

## AC参数逆向说明

从 JS 代码分析，AC 参数由以下组成：

```javascript
// 来自 basic-captcha-js.js
{
  ac: w ? w.getUA() : "",  // 加密后的轨迹数据
  ak: g.appId,             // AppID
  c: E || "",              // Challenge
  uid: g.uid,              // 用户ID
  jsv: _,                  // JS版本
  sid: y,                  // 会话ID  
  aid: C,                  // 设备ID
  x: B,                    // 最终X坐标
  y: Q                     // 最终Y坐标
}
```

`w.getUA()` 方法会收集：
1. 轨迹坐标序列
2. 时间戳序列
3. 可能的设备指纹信息
4. 鼠标事件类型

当前实现的是**简化版本**，如果验证失败，需要：
1. 抓取真实通过验证的 ac 参数
2. Base64 解码查看格式
3. 调整 `ac_encoder.py` 的编码逻辑

## 注意事项

⚠️ **重要提示**：

1. 此代码仅用于学习研究，不应用于生产环境
2. 频繁的自动化请求可能触发更严格的风控
3. 验证码服务商会持续升级对抗策略
4. 建议添加请求间隔，降低触发验证码的概率

## 许可

仅供学习研究使用。
