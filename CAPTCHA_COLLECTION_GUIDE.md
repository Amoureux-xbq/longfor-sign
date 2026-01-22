# 📸 验证码图片收集指南

## 🎯 功能说明

当 GitHub Actions 自动运行时，会自动保存每次验证码的图片，用于后续优化识别算法。

---

## 📍 图片存储位置

### 在 GitHub 上

Artifacts（工件）存储在 **GitHub Actions 运行记录中**，而**不是**代码仓库中。

**访问路径**：
```
1. 打开您的 GitHub 仓库
2. 点击顶部的 "Actions" 标签
3. 选择一个工作流运行记录
4. 滚动到页面底部，找到 "Artifacts" 部分
5. 点击下载对应的压缩包
```

**可视化示例**：
```
GitHub 仓库页面
├── Code (代码)
├── Issues
├── Pull requests
└── Actions ← 点击这里
    └── 工作流运行列表
        └── 龙湖天街自动签到 #123
            ├── 运行日志
            └── Artifacts ← 在页面底部
                └── captcha-images-123.zip (下载)
```

---

## 🔍 查看和下载步骤

### 方法 1: 通过 GitHub 网页界面

1. **打开 Actions 页面**
   ```
   https://github.com/YOUR_USERNAME/longfor-sign/actions
   ```

2. **选择一个工作流运行**
   - 点击任意一次运行记录（例如："龙湖天街自动签到 #123"）

3. **找到 Artifacts 部分**
   - 滚动到页面底部
   - 会看到类似这样的区块：
   ```
   Artifacts
   ┌─────────────────────────────────────────┐
   │ 📦 captcha-images-123                   │
   │    Expires in 30 days                   │
   │    [Download]                           │
   └─────────────────────────────────────────┘
   ```

4. **点击下载**
   - 会下载一个 ZIP 文件
   - 解压后可以看到所有收集的图片

### 方法 2: 使用 GitHub CLI

```bash
# 安装 GitHub CLI
brew install gh  # macOS
# 或访问 https://cli.github.com/

# 登录
gh auth login

# 列出最近的运行
gh run list --workflow="龙湖天街自动签到"

# 下载指定运行的 artifacts
gh run download RUN_ID

# 或下载最新的
gh run download --name captcha-images-123
```

---

## 📂 下载后的文件结构

```
captcha-images-123.zip
└── captcha_collection/
    ├── 20260122_090123/         ← 第一次运行
    │   ├── bg_restored.png      ← 还原后的背景图
    │   ├── slider.png           ← 滑块图
    │   └── info.txt             ← 识别信息
    │       ├── 时间: 20260122_090123
    │       ├── X 坐标: 187
    │       ├── Y 坐标: 90
    │       ├── 验证结果: True
    │       └── 错误信息: SUCCESS
    │
    ├── 20260123_090145/         ← 第二次运行
    │   ├── bg_restored.png
    │   ├── slider.png
    │   └── info.txt
    │
    └── ...                      ← 更多运行记录
```

---

## ⚙️ 配置说明

### 当前配置

在 `.github/workflows/daily-sign.yml` 中：

```yaml
- name: 执行签到
  env:
    SAVE_CAPTCHA_IMAGES: 'true'  # ✅ 启用图片保存
  run: python main.py

- name: 上传验证码图片
  if: always()                    # 即使失败也上传
  uses: actions/upload-artifact@v4
  with:
    name: captcha-images-${{ github.run_number }}
    path: captcha_collection/
    retention-days: 30            # 保留30天
    if-no-files-found: ignore     # 没有文件也不报错
```

### 配置参数说明

| 参数 | 值 | 说明 |
|------|-----|------|
| `SAVE_CAPTCHA_IMAGES` | `'true'` | 启用图片保存功能 |
| `name` | `captcha-images-{run_number}` | Artifact 名称，包含运行编号 |
| `path` | `captcha_collection/` | 要上传的目录 |
| `retention-days` | `30` | 保留天数（1-90天） |
| `if` | `always()` | 即使签到失败也上传图片 |

### 修改保留天数

如果想保留更长时间（最多 90 天）：

```yaml
retention-days: 90  # 最长保留时间
```

---

## 🔐 隐私说明

### ✅ 安全特性

1. **仅仓库所有者可访问**
   - Artifacts 只有仓库所有者和协作者可以下载
   - 外部用户无法访问

2. **不在代码仓库中**
   - 不会占用 Git 仓库空间
   - 不会被 `git clone` 下载

3. **自动过期**
   - 默认 30 天后自动删除
   - 不会永久占用空间

### ⚠️ 注意事项

- Artifacts **不包含敏感信息**（仅图片和坐标）
- 图片是**还原后的验证码图片**，不包含用户数据
- 如果不想保存图片，删除 `SAVE_CAPTCHA_IMAGES: 'true'` 即可

---

## 📊 使用收集的数据

### 1. 分析识别准确率

```python
import os
from pathlib import Path

# 读取所有收集的数据
collection_dir = Path('captcha_collection')

success_count = 0
fail_count = 0

for session_dir in collection_dir.iterdir():
    info_file = session_dir / 'info.txt'
    if info_file.exists():
        content = info_file.read_text(encoding='utf-8')
        if '验证结果: True' in content:
            success_count += 1
        else:
            fail_count += 1

print(f"成功率: {success_count / (success_count + fail_count) * 100:.2f}%")
print(f"成功: {success_count}, 失败: {fail_count}")
```

### 2. 优化偏移量

```python
import re
from collections import Counter

# 统计失败时的 X 坐标分布
failed_x_coords = []

for session_dir in collection_dir.iterdir():
    info_file = session_dir / 'info.txt'
    if info_file.exists():
        content = info_file.read_text(encoding='utf-8')
        if '验证结果: False' in content and 'POSITION_MISMATCH' in content:
            x_match = re.search(r'X 坐标: (\d+)', content)
            if x_match:
                failed_x_coords.append(int(x_match.group(1)))

# 分析失败的坐标分布
if failed_x_coords:
    print(f"失败的 X 坐标统计:")
    print(f"平均值: {sum(failed_x_coords) / len(failed_x_coords):.1f}")
    print(f"范围: {min(failed_x_coords)} - {max(failed_x_coords)}")
```

### 3. 训练机器学习模型

收集足够数据后，可以：
- 使用 OpenCV 训练更好的识别模型
- 使用 CNN 进行端到端的缺口检测
- 优化滑块位置识别算法

---

## 🛠️ 本地测试

### 启用图片保存

```bash
# 设置环境变量
export SAVE_CAPTCHA_IMAGES=true

# 运行程序
python main.py

# 查看保存的图片
ls -la captcha_collection/
```

### 临时禁用图片保存

```bash
# 不设置环境变量，或设置为 false
export SAVE_CAPTCHA_IMAGES=false
python main.py
```

---

## 📈 数据收集建议

### 最佳实践

1. **至少收集 30 天数据**
   - 每天 1 次 = 30 个样本
   - 可以看出不同时间段的图片差异

2. **记录失败案例**
   - 特别关注 `POSITION_MISMATCH` 错误
   - 这些数据最有价值，用于优化偏移量

3. **定期分析**
   - 每周下载一次 artifacts
   - 分析成功率和失败原因

### 存储配额

GitHub Actions Artifacts 存储：
- **免费账户**: 500MB 存储空间
- **Pro 账户**: 2GB 存储空间
- 每张图片约 20-50KB
- 30 天 × 2 张图片 × 50KB ≈ 3MB（远低于限额）

---

## 🚫 如何禁用

如果不想收集图片，有两种方法：

### 方法 1: 删除环境变量

```yaml
# 在 .github/workflows/daily-sign.yml 中
- name: 执行签到
  env:
    # SAVE_CAPTCHA_IMAGES: 'true'  ← 注释掉或删除这行
    LONGFOR_TOKEN: ${{ secrets.LONGFOR_TOKEN }}
    ...
```

### 方法 2: 删除上传步骤

```yaml
# 删除或注释整个上传步骤
# - name: 上传验证码图片
#   if: always()
#   uses: actions/upload-artifact@v3
#   ...
```

---

## 📝 总结

| 特性 | 说明 |
|------|------|
| **存储位置** | GitHub Actions 运行记录中 |
| **访问权限** | 仅仓库所有者可访问 |
| **保留时间** | 30 天（可配置 1-90 天） |
| **文件类型** | 还原后的背景图 + 滑块图 + 信息文本 |
| **用途** | 优化识别算法、分析失败原因 |
| **空间占用** | 约 3MB/月（远低于限额） |
| **隐私性** | ✅ 安全，不包含敏感信息 |

---

## 🔗 相关链接

- [GitHub Actions Artifacts 文档](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
- [GitHub CLI 文档](https://cli.github.com/manual/gh_run_download)
- [Actions 使用限制](https://docs.github.com/en/actions/learn-github-actions/usage-limits-billing-and-administration)

---

**提示**: 定期下载并分析这些数据，可以持续优化验证码识别的准确率！
