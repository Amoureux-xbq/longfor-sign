# 龙湖天街自动签到 🎯

基于 Python 的龙湖天街每日签到脚本，支持验证码自动识别，可配合 GitHub Actions 定时运行。

## ✨ 特性

- ✅ 自动完成每日签到
- ✅ 自动识别滑块验证码（顶象验证）
- ✅ 图像自动还原和缺口检测
- ✅ 轨迹生成和 AC 参数编码
- ✅ GitHub Actions 定时运行（每天 9-15 点随机一次）
- ✅ Bark 推送签到结果到手机

## 🚀 快速开始

### 方式1：GitHub Actions（推荐）

#### 1. Fork 本仓库

点击页面右上角的 **Fork** 按钮

#### 2. 配置 Secrets

在你的仓库中：**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

添加以下 Secrets：

| Secret 名称 | 说明 | 必需 |
|------------|------|------|
| `TOKEN` | 龙湖天街登录 token | ✅ |
| `DXRISK_TOKEN` | 顶象风控 token | ✅ |
| `BARK_KEY` | Bark 推送 key | ⭕ 可选 |

**获取 Token 方法**：使用微信开发者工具打开龙湖天街小程序，在 Network 面板中查看请求头。

详细配置步骤请查看：[GitHub Actions 配置指南](./GITHUB_ACTIONS_SETUP.md)

#### 3. 启用 Actions

在仓库页面点击 **Actions** 标签，启用工作流。

#### 4. 完成！

脚本将在每天 9-15 点之间随机选择一个时刻自动运行。

---

### 方式2：本地运行

#### 1. 安装依赖

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/longfor-sign.git
cd longfor-sign

# 安装 Python 依赖
pip install -r requirements.txt
```

#### 2. 配置环境变量

```bash
export TOKEN="你的 token"
export DXRISK_TOKEN="你的 dxrisk token"
export BARK_KEY="你的 Bark Key"  # 可选
```

或创建 `.env` 文件：

```env
TOKEN=你的token
DXRISK_TOKEN=你的dxrisk_token
BARK_KEY=你的bark_key
```

#### 3. 运行

```bash
python main.py
```

---

## 📂 项目结构

```
longfor-sign/
├── main.py                      # 主程序入口
├── longfor.py                   # 龙湖天街 API 封装
├── captcha_handler.py           # 验证码处理核心
├── image_recognition_v2.py      # 图像识别（形状匹配）
├── ac_encoder_full.py          # AC 参数编码器
├── trajectory.py                # 轨迹生成
├── decode_o_string.py          # 切片顺序解码
├── restore_correct.py          # 图像还原
├── calculate_xy.py             # X/Y 坐标计算工具 🆕
├── bark_notify.py              # Bark 推送通知
├── requirements.txt            # Python 依赖
├── .github/workflows/          # GitHub Actions 配置
│   └── daily-sign.yml         # 定时签到工作流
├── README.md                   # 本文件
├── GITHUB_ACTIONS_SETUP.md    # GitHub Actions 详细配置
├── CALCULATE_XY_USAGE.md      # X/Y 坐标计算工具使用指南 🆕
└── AC_ENCODER_README.md       # AC 参数技术文档
```

---

## 🔧 技术细节

### 验证码处理流程

1. **获取验证码**：调用龙湖天街 API 获取背景图和滑块图
2. **图像还原**：根据切片顺序 (`o` 参数) 还原被打乱的背景图
3. **缺口识别**：使用形状匹配算法识别滑块缺口位置
4. **轨迹生成**：生成拟人化的滑动轨迹（贝塞尔曲线 + 抖动）
5. **AC 编码**：根据 greenseer.js 逻辑编码环境信息和轨迹
6. **提交验证**：提交 AC 参数和坐标完成验证

详细技术文档：[AC_ENCODER_README.md](./AC_ENCODER_README.md)

### 核心算法

- **图像识别**：OpenCV 模板匹配 (TM_CCOEFF_NORMED)
- **偏移修正**：检测位置 - 60px = 实际滑动距离
- **轨迹生成**：三次贝塞尔曲线 + 随机抖动 + 回弹
- **AC 编码**：完整实现 greenseer.js 的所有环境检测和加密

---

## 📊 运行时间表

| 触发时间 | 随机延迟 | 实际运行时间 | 频率 |
|---------|---------|------------|------|
| 北京时间 9:00 | 0-6 小时 | 9:00 - 15:00 之间随机 | 每天一次 |

**说明**：
- 每天早上 9 点触发
- 随机延迟 0-6 小时后执行
- 最终在 9-15 点之间的任意时刻运行
- 避免固定时间被检测

---

## ⚠️ 注意事项

1. **Token 安全**
   - 不要泄露你的 Token
   - 定期检查和更换 Token
   - 使用 GitHub Secrets 存储敏感信息

2. **验证码识别**
   - 识别成功率约 85-95%
   - 失败后会在下次运行时重试
   - 可查看 Actions 日志定位问题

3. **运行策略**
   - 每天只运行 1 次，避免频繁请求
   - 9-15 点之间随机时刻，避免固定时间被检测

---

## 🛠️ 故障排查

### Token 失效

```
❌ 错误: 401 Unauthorized
```

**解决方法**：重新抓包获取最新 Token，并更新 GitHub Secrets

### 验证码识别失败

```
❌ 验证失败: 缺口识别错误
```

**解决方法**：
- 查看日志中的识别坐标
- 正常情况下会在下次运行时重试
- 持续失败可能需要调整识别参数

### 工作流未运行

**可能原因**：
- GitHub Actions 未启用
- Secrets 未配置
- cron 表达式错误
- GitHub 服务延迟

---

## 📝 本地测试

### 快速计算 x, y 坐标

```bash
# 计算滑动距离和垂直位置
python calculate_xy.py <背景图> <滑块图> [方法]

# 示例
python calculate_xy.py restored_bg.jpg slider.png shape
python calculate_xy.py restored_bg.jpg slider.png auto
```

**参数说明**：
- `背景图`：需要先使用 `restore_correct.py` 还原的完整背景图
- `滑块图`：PNG 格式的滑块图片
- `方法`：可选，`shape`（推荐）/`auto`/`contour`/`color`

详细说明见：[CALCULATE_XY_USAGE.md](./CALCULATE_XY_USAGE.md)

### 测试图像识别

```bash
python test_recognition.py <背景图> <滑块图> [期望x坐标]
```

### 测试完整流程

```bash
python main.py
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- OpenCV 图像识别
- 顶象验证码逆向分析
- GitHub Actions 自动化

---

**祝签到顺利！** 🎉
