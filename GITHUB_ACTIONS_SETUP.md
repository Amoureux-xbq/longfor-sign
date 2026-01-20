# GitHub Actions 自动签到配置指南

## 📋 功能说明

- **运行时间**：每天在 9-15 点之间随机选择一个时刻运行一次
- **随机策略**：9 点触发，随机延迟 0-6 小时后执行
- **手动触发**：支持在 GitHub Actions 页面手动运行

## 🔧 配置步骤

### 1. 推送代码到 GitHub

```bash
# 初始化 Git 仓库（如果还没有）
git init
git add .
git commit -m "Initial commit: 龙湖天街自动签到"

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/longfor-sign.git

# 推送代码
git push -u origin main
```

### 2. 配置 GitHub Secrets

在 GitHub 仓库页面：

1. 点击 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下 Secrets：

#### 必需的 Secrets：

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `LONGFOR_TOKEN` | 龙湖天街登录 token | 从小程序抓包获取 |
| `DXRISK_TOKEN` | 顶象风控 token | 从小程序抓包获取 |

#### 可选的 Secrets：

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `BARK_KEY` | Bark 推送通知 key | 从 Bark App 获取 |

### 3. 获取 Token 的方法

#### 方法1：使用微信开发者工具

1. 打开**微信开发者工具**
2. 登录你的微信账号
3. 打开**龙湖天街**小程序
4. 在开发者工具中打开 **Network** 面板
5. 执行签到操作
6. 查找请求头中的：
   - `token`: 即为 `LONGFOR_TOKEN`
   - `dxriskToken`: 即为 `DXRISK_TOKEN`

#### 方法2：使用 Charles/Fiddler 抓包

1. 配置手机代理到电脑
2. 打开龙湖天街小程序
3. 执行签到操作
4. 在抓包工具中查找相关请求的请求头

### 4. 启用 GitHub Actions

1. 在仓库页面点击 **Actions** 标签
2. 如果看到提示，点击 **I understand my workflows, go ahead and enable them**
3. 等待下次定时运行，或点击 **Run workflow** 手动触发

## 📊 运行时间表

| 触发时间（北京） | UTC 时间 | 随机延迟 | 实际运行时间 |
|----------------|---------|---------|------------|
| 9:00 | 1:00 | 0-6小时 | 9:00 - 15:00 之间随机 |

**说明**：
- 每天 9 点触发 GitHub Actions
- 随机延迟 0-21600 秒（0-6 小时）
- 最终在 9-15 点之间的任意时刻执行
- 每天只运行一次

## 🔍 查看运行日志

1. 在仓库页面点击 **Actions** 标签
2. 点击最近的工作流运行
3. 查看各步骤的详细日志

## ⚠️ 注意事项

1. **Token 安全**：
   - 不要在代码中硬编码 Token
   - 不要将 Token 提交到 Git
   - 定期更换 Token

2. **运行频率**：
   - 每天运行 4 次，避免过于频繁
   - 随机延迟避免固定时间被检测

3. **失败处理**：
   - 验证码识别可能失败
   - Token 可能过期需要更新
   - 查看日志定位问题

## 🛠️ 故障排查

### Token 失效

**症状**：签到失败，日志显示认证错误

**解决**：
1. 重新抓包获取最新的 Token
2. 更新 GitHub Secrets 中的 Token
3. 手动触发工作流测试

### 验证码识别失败

**症状**：日志显示验证码识别错误

**解决**：
- 正常现象，识别算法有一定失败率
- 下次定时运行会重试
- 查看具体错误信息优化识别参数

### 工作流未运行

**症状**：到了运行时间但没有执行

**解决**：
1. 检查 Actions 是否已启用
2. 检查 cron 表达式是否正确
3. GitHub Actions 可能有延迟（最多几分钟）

## 📝 修改运行时间

编辑 `.github/workflows/daily-sign.yml`：

```yaml
schedule:
  # 修改这里的时间（UTC 时间）
  - cron: '0 1,3,5,7 * * *'
```

**时间换算**：
- 北京时间 = UTC 时间 + 8 小时
- 例如：北京 9 点 = UTC 1 点

## 🎉 成功标志

看到以下日志说明签到成功：
```
✅ 签到成功！
获得积分：XX
连续签到：X天
```

---

**祝签到顺利！** 🎊
