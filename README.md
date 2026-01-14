## 龙湖天街每日签到脚本

基于 Python 的龙湖天街每日签到脚本，可配合 GitHub Actions 定时运行，并支持 Bark 推送签到结果到手机。

### 一、快速开始（本地运行）

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 配置环境变量（推荐）：

```bash
export LONGFOR_TOKEN="你的 token"
export LONGFOR_DXRISK_TOKEN="你的 X-LF-DXRisk-Token"
export LONGFOR_ACTIVITY_NO="11111111111686241863606037740000"

# 可选：Bark 推送
export BARK_KEY="你的 Bark Key"
export BARK_SERVER="https://api.day.app"  # 可选，默认即为此
```

3. 运行：

```bash
python main.py
```

### 二、GitHub Actions 使用说明（示例）

在你的新仓库中创建 `.github/workflows/auto_sign.yml`，内容示例：

```yaml
name: Longfor Auto Sign

on:
  schedule:
    - cron: '0 1 * * *'  # 每天 09:00（UTC+8 为 17:00，请按需调整）
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd longfor-sign
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run longfor sign
        env:
          LONGFOR_TOKEN: ${{ secrets.LONGFOR_TOKEN }}
          LONGFOR_DXRISK_TOKEN: ${{ secrets.LONGFOR_DXRISK_TOKEN }}
          LONGFOR_ACTIVITY_NO: ${{ vars.LONGFOR_ACTIVITY_NO }}
          BARK_KEY: ${{ secrets.BARK_KEY }}
          BARK_SERVER: ${{ vars.BARK_SERVER }}
        run: |
          cd longfor-sign
          python main.py
```

### 三、环境变量说明

- **LONGFOR_TOKEN**：抓包得到的 `token` / `X-LF-UserToken`
- **LONGFOR_DXRISK_TOKEN**：抓包得到的 `X-LF-DXRisk-Token`
- **LONGFOR_ACTIVITY_NO**：活动编号，当前为 `11111111111686241863606037740000`
- **BARK_KEY**：Bark 推送 Key（可选）
- **BARK_SERVER**：Bark 服务器，默认为 `https://api.day.app`


