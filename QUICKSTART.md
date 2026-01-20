# 快速开始指南

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

如果 OpenCV 安装失败，可以尝试：
```bash
pip install opencv-python-headless  # 无GUI版本，体积更小
```

## 🚀 基础使用

### 1. 配置环境变量

```bash
# 单个账号
export LONGFOR_TOKEN="你的token"
export LONGFOR_DXRISK_TOKEN="你的dxrisk_token"

# 多个账号（换行分隔）
export LONGFOR_TOKEN="token1
token2
token3"

export LONGFOR_DXRISK_TOKEN="dxrisk1
dxrisk2
dxrisk3"

# Bark通知（可选）
export BARK_KEY="你的BarkKey"
export BARK_SERVER="https://api.day.app"
```

### 2. 运行签到

```bash
python main.py
```

**程序会自动处理验证码！** 当遇到滑块验证时，会：
- 自动识别缺口位置
- 生成拟人化轨迹
- 提交验证并继续签到

## 🧪 测试验证码功能

### 完整流程测试
```bash
python test_captcha_flow.py
```

这将依次测试：
1. ✓ UV类型检查
2. ✓ 验证码初始化
3. ✓ 图像识别（会保存调试图片）
4. ✓ 轨迹生成
5. ✓ AC参数编码

### 单独测试各模块

#### 测试图像识别
```python
from image_recognition import find_gap_position

x, y = find_gap_position("bg.png", "slider.png", debug=True)
print(f"缺口位置: x={x}, y={y}")

# 会生成调试图片：
# - debug_bg_edges.png (背景边缘)
# - debug_slider_edges.png (滑块边缘)
# - debug_result.png (标记位置)
```

#### 测试轨迹生成
```python
from trajectory import generate_trajectory, add_shake_at_end

trajectory = generate_trajectory(187)  # 移动187像素
trajectory = add_shake_at_end(trajectory)

print(f"轨迹点数: {len(trajectory)}")
for x, y, t in trajectory[:5]:
    print(f"x={x}, y={y}, t={t}ms")
```

#### 测试AC编码
```python
from ac_encoder import encode_ac_parameter
import base64

trajectory = [(0,0,0), (10,1,50), (20,0,100)]
ac = encode_ac_parameter(trajectory)

print(f"AC长度: {len(ac)}")
print(f"解码: {base64.b64decode(ac).decode()}")
```

## 📋 签到流程说明

### 正常情况（无验证码）
```
┌─────────────┐
│   运行签到   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  签到成功   │ ✓
└─────────────┘
```

### 触发验证码时
```
┌─────────────┐
│   运行签到   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│返回 8040012 │ ⚠️ 需要验证
└──────┬──────┘
       │
       ▼
┌─────────────┐
│检查UV类型   │ GET /v2/api/uv/type
└──────┬──────┘
       │ 返回 "c"
       ▼
┌─────────────┐
│初始化验证码 │ GET /api/a
└──────┬──────┘
       │ 获得 sid, p1, p2
       ▼
┌─────────────┐
│ 下载图片    │ GET /api/p1, /api/p2
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 识别缺口    │ OpenCV 图像识别
└──────┬──────┘
       │ x=187, y=67
       ▼
┌─────────────┐
│ 生成轨迹    │ 模拟人类滑动
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 编码轨迹    │ Base64(JSON)
└──────┬──────┘
       │ ac参数
       ▼
┌─────────────┐
│ 提交验证    │ POST /api/v1
└──────┬──────┘
       │ 获得 token
       ▼
┌─────────────┐
│ 重新签到    │ 带验证token
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  签到成功   │ ✓
└─────────────┘
```

## 🔧 调试技巧

### 1. 查看详细日志
程序会自动输出每个步骤的详细信息：
```
==================================================
开始验证码处理流程
==================================================
✓ UV类型检查: c
✓ 确认需要滑块验证
✓ 验证码初始化成功
  - SID: xxx
  - Challenge: xxx
  - Y坐标: 67

==================================================
开始处理滑块验证码
==================================================
1️⃣ 正在下载验证码图片...
   ✓ 图片下载成功
2️⃣ 正在识别缺口位置...
   ✓ 识别成功: x=187, y=67
3️⃣ 正在生成滑动轨迹...
   ✓ 生成 28 个轨迹点
4️⃣ 正在编码轨迹数据...
   ✓ AC参数长度: 512
5️⃣ 正在提交验证...
   ✓ 验证成功! Token: 19BDA2...
```

### 2. 保存调试图片
在 `image_recognition.py` 中启用 debug 模式：
```python
x, y = find_gap_position(bg_path, slider_path, debug=True)
```

这会在当前目录生成：
- `debug_bg_edges.png` - 背景图的边缘检测结果
- `debug_slider_edges.png` - 滑块图的边缘检测结果  
- `debug_result.png` - 标记了识别位置的结果图

### 3. 调整识别参数

如果识别不准确，修改 Canny 边缘检测的阈值：

```python
# image_recognition.py 第24-25行
bg_edges = cv2.Canny(bg_gray, 50, 150)  # 当前值
slider_edges = cv2.Canny(slider_gray, 50, 150)

# 如果识别到太多噪点，提高阈值：
bg_edges = cv2.Canny(bg_gray, 100, 200)

# 如果识别不到边缘，降低阈值：
bg_edges = cv2.Canny(bg_gray, 30, 100)
```

### 4. 调整轨迹参数

如果验证总是失败，可能是轨迹太机械化：

```python
# trajectory.py
# 增加随机性
a = random.randint(2, 5)  → random.randint(1, 6)

# 增加抖动幅度  
y_offset = random.randint(-2, 2)  → random.randint(-3, 3)

# 增加抖动次数
shake_count = random.randint(3, 5)  → random.randint(5, 8)
```

## ❓ 常见问题

### Q1: 识别不准确怎么办？

**A:** 开启 debug 模式查看边缘图：
```python
x, y = find_gap_position(bg_path, slider_path, debug=True)
```
检查 `debug_bg_edges.png` 和 `debug_slider_edges.png`：
- 如果边缘太多（噪点），提高 Canny 阈值
- 如果边缘太少（看不清），降低 Canny 阈值

### Q2: 验证总是失败？

**A:** 可能原因：
1. **AC参数格式不对** - 对比真实抓包的 ac 参数
2. **轨迹太假** - 增加随机性和抖动
3. **时间不对** - 检查总时长是否在合理范围（1-2秒）

解决方法：
- 抓包一次成功的验证，解码 ac 参数查看格式
- 调整 `trajectory.py` 的参数
- 确保轨迹总时长在 1000-2000ms 之间

### Q3: ImportError: No module named 'cv2'

**A:** OpenCV 未安装成功，尝试：
```bash
pip install opencv-python --upgrade
# 或者安装无GUI版本
pip install opencv-python-headless
```

### Q4: 如何在 GitHub Actions 中使用？

**A:** 需要安装系统依赖：
```yaml
- name: Install dependencies
  run: |
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y libopencv-dev python3-opencv
    pip install -r requirements.txt
```

或者使用 headless 版本（推荐）：
```txt
# requirements.txt
opencv-python-headless>=4.8.0  # 无GUI，适合服务器
```

### Q5: 验证码下载失败？

**A:** 检查网络和代理设置：
```python
# 如果需要代理
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
response = requests.get(url, proxies=proxies)
```

## 📚 更多文档

- [README_CAPTCHA.md](README_CAPTCHA.md) - 详细的技术文档
- [README.md](README.md) - 项目说明

## ⚠️ 注意事项

1. **仅供学习研究** - 不要用于生产环境
2. **控制频率** - 不要频繁运行，容易触发更严格的风控
3. **及时更新** - 验证码算法可能随时变化，需要调整代码
4. **保护隐私** - 不要泄露你的 token

## 📝 许可

仅供学习研究使用。
