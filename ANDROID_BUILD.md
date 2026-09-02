# Gudo Snake Android 打包指南

竖屏 **1080×1920**、大号虚拟按键、应用图标与 Release 签名均已配置。

---

## 目录

1. [本地预览（Windows）](#1-本地预览windows)
2. [云端构建（GitHub Actions，推荐）](#2-云端构建github-actions推荐)
3. [WSL 完整安装与构建（逐步命令）](#3-wsl-完整安装与构建逐步命令)
4. [Docker 构建](#4-docker-构建)
5. [应用图标](#5-应用图标)
6. [Release 签名版 APK](#6-release-签名版-apk)
7. [安装到手机](#7-安装到手机)
8. [常见问题](#8-常见问题)

---

## 1. 本地预览（Windows）

```powershell
cd c:\Users\Matri\pytorch_env\pygame\gudosnake
python demo_mobile.py
```

桌面以 540×960 窗口预览；手机为全屏。

---

## 2. 云端构建（GitHub Actions，推荐）

**不需要 WSL、Docker 或 Ubuntu**，把代码推到 GitHub，在云端 Linux 上自动打包 APK。

### 第 1 步：推送代码到 GitHub

项目远程仓库：`git@github.com:TianruiDai/GudoSnake.git`

在 Windows PowerShell 中：

```powershell
cd c:\Users\Matri\pytorch_env\pygame\gudosnake
git add .
git commit -m "Add Android cloud build"
git push origin main
```

### 第 2 步：在 GitHub 上触发构建

1. 打开 https://github.com/TianruiDai/GudoSnake
2. 点击 **Actions** 标签
3. 左侧选择 **Build Android APK**
4. 点击 **Run workflow** → 选择 `debug` → **Run workflow**

也可以：每次 `push` 到 `main` 分支且改动了 Python / buildozer 相关文件时，会自动触发 Debug 构建。

### 第 3 步：下载 APK

1. 构建完成后（**首次约 45–90 分钟**，有缓存后更快）
2. 进入该次运行的页面
3. 在 **Artifacts** 区域下载 `GudoSnake-android-debug`
4. 解压得到 `.apk`，传到手机安装

### 云端 Release 签名版（可选）

若需要正式签名包，在 GitHub 仓库设置 **Secrets**（Settings → Secrets and variables → Actions）：

| Secret 名称 | 内容 |
|-------------|------|
| `ANDROID_KEYSTORE_BASE64` | keystore 文件的 base64 编码 |
| `ANDROID_KEYSTORE_PASSWORD` | keystore 密码 |
| `ANDROID_KEY_ALIAS` | 别名（默认 `gudosnake`） |
| `ANDROID_KEY_PASSWORD` | key 密码 |

生成 base64（在已有 keystore 的机器上）：

```bash
base64 -w 0 signing/gudosnake-release.keystore
```

Windows PowerShell：

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("signing\gudosnake-release.keystore"))
```

然后在 Actions 里 **Run workflow** → 选择 `release`。

---

## 3. WSL 完整安装与构建（逐步命令）

Buildozer **不能在 Windows 原生环境构建**，请使用 WSL2 + Ubuntu。

### 第 1 步：在 Windows 安装 WSL

**PowerShell（管理员）** 执行：

```powershell
wsl --install
```

若提示选择发行版，推荐 **Ubuntu**：

```powershell
wsl --install -d Ubuntu
```

**重启电脑**。

重启后首次打开 **Ubuntu**，按提示创建 Linux 用户名和密码。

验证 WSL 是否正常：

```powershell
wsl -l -v
```

应看到 Ubuntu，`VERSION` 为 `2`。

---

### 第 2 步：进入 Ubuntu 终端

方式任选其一：

- 开始菜单 → 打开 **Ubuntu**
- 或在 PowerShell 中：`wsl`

---

### 第 3 步：一键安装构建依赖

在 Ubuntu 中执行（项目路径在 Windows 的 C 盘，WSL 下为 `/mnt/c/...`）：

```bash
cd /mnt/c/Users/Matri/pytorch_env/pygame/gudosnake
bash wsl-setup.sh
```

或手动逐步执行：

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装编译依赖
sudo apt install -y \
  git zip unzip openjdk-17-jdk python3-pip python3-venv \
  autoconf automake libtool pkg-config zlib1g-dev \
  libncurses5-dev libncursesw5-dev libtinfo5 cmake \
  libffi-dev libssl-dev ccache

# 安装 buildozer
pip3 install --user --upgrade pip
pip3 install --user buildozer "Cython<0.30"

# 把 buildozer 加入 PATH（只需做一次）
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 验证
buildozer --version
```

---

### 第 4 步：进入项目目录

```bash
cd /mnt/c/Users/Matri/pytorch_env/pygame/gudosnake
```

> **提示：** WSL 访问 Windows 文件较慢。若构建很慢，可把项目复制到 Linux 家目录：
> ```bash
> cp -r /mnt/c/Users/Matri/pytorch_env/pygame/gudosnake ~/gudosnake
> cd ~/gudosnake
> ```

---

### 第 5 步：生成应用图标（可选，已预生成）

```bash
pip3 install --user pillow
python3 scripts/generate_assets.py
```

会生成：

- `assets/icon.png`（512×512 应用图标）
- `assets/presplash.png`（启动闪屏）
- `assets/icon_foreground.png` / `icon_background.png`（Android 自适应图标）

---

### 第 6 步：构建 Debug APK（首次约 30–60 分钟）

```bash
buildozer -v android debug
```

或使用快捷脚本：

```bash
bash wsl-build-debug.sh
```

首次会下载 Android SDK、NDK 并编译 pygame-ce，请保持网络畅通。

成功后 APK 位于：

```text
bin/gudosnake-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

---

### 第 7 步：后续增量构建

代码改动后重新打包：

```bash
cd /mnt/c/Users/Matri/pytorch_env/pygame/gudosnake
buildozer -v android debug
```

若依赖或配方有变，先清理：

```bash
buildozer android clean
buildozer -v android debug
```

---

## 4. Docker 构建

若已安装 Docker Desktop：

```powershell
cd c:\Users\Matri\pytorch_env\pygame\gudosnake
.\build-android.ps1
```

或 Git Bash / WSL：

```bash
bash build-android.sh
```

---

## 5. 应用图标

图标已在 `buildozer.spec` 中配置：

```ini
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
icon.adaptive_foreground.filename = %(source.dir)s/assets/icon_foreground.png
icon.adaptive_background.filename = %(source.dir)s/assets/icon_background.png
```

更换图标：替换 `assets/icon.png` 等文件（建议 512×512 PNG），或运行：

```bash
python3 scripts/generate_assets.py
```

修改 `scripts/generate_assets.py` 可自定义图案。

---

## 6. Release 签名版 APK

Debug APK 可直接 sideload 测试；上架或正式分发需 **签名 Release 包**。

### 6.1 生成签名密钥（只需一次）

在 **WSL/Ubuntu** 中：

```bash
cd /mnt/c/Users/Matri/pytorch_env/pygame/gudosnake
bash scripts/generate-keystore.sh
```

按提示输入：

- Keystore 密码
- Key 密码（可直接回车与 Keystore 密码相同）

会生成（**切勿提交到 Git**）：

- `signing/gudosnake-release.keystore`
- `signing/keystore.properties`

也可手动配置：

```bash
cp signing/keystore.properties.example signing/keystore.properties
# 编辑 keystore.properties，填入密码
```

手动生成 keystore 示例：

```bash
mkdir -p signing
keytool -genkeypair -v \
  -keystore signing/gudosnake-release.keystore \
  -alias gudosnake \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -storepass YOUR_STORE_PASS \
  -keypass YOUR_KEY_PASS \
  -dname "CN=Gudo Snake, OU=Mobile, O=GudoSnake, L=Local, ST=Local, C=CN"
```

### 6.2 构建 Release APK

```bash
cd /mnt/c/Users/Matri/pytorch_env/pygame/gudosnake
bash scripts/build-release.sh
```

脚本会：

1. 读取 `signing/keystore.properties`
2. 临时写入签名配置到 `buildozer.spec`
3. 执行 `buildozer android release`
4. 构建结束后 **自动恢复** `buildozer.spec`（密码不会留在仓库里）

Release APK 输出示例：

```text
bin/gudosnake-1.0.0-arm64-v8a_armeabi-v7a-release.apk
```

### 6.3 密钥备份

**务必备份** `signing/gudosnake-release.keystore` 和密码。丢失后无法更新同一应用，只能换包名重新发布。

---

## 7. 安装到手机

### USB 安装（WSL 需配置 adb）

Windows 安装 [Platform Tools](https://developer.android.com/tools/releases/platform-tools)，PowerShell：

```powershell
adb install bin\gudosnake-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

或把 APK 传到手机，开启「允许安装未知来源应用」后点击安装。

### 查看崩溃日志

```bash
adb logcat | grep -i python
```

---

## 8. 常见问题

### WSL 构建很慢

把项目复制到 Linux 文件系统（`~/gudosnake`）再构建，通常比 `/mnt/c/` 快很多。

### pygame-ce 编译失败

确认 `buildozer.spec`：

```ini
requirements = python3,hostpython3,pyjnius,pyyaml,pygame-ce
p4a.local_recipes = ./p4a-recipes
```

然后：

```bash
buildozer android clean
buildozer -v android debug
```

### Release 构建报签名错误

检查 `signing/keystore.properties` 中密码、别名是否与 keystore 一致：

```bash
keytool -list -v -keystore signing/gudosnake-release.keystore
```

### 手机操作说明

| 按键 | 功能 |
|------|------|
| W / A / S / D | 方向 |
| Shift（按住） | 三倍速度 |
| R | 游戏结束后重新开始 |

---

## 项目文件一览

| 文件 | 作用 |
|------|------|
| `main.py` | Android 入口 |
| `demo_mobile.py` | 竖屏游戏 + 虚拟按键 |
| `buildozer.spec` | 打包配置（图标、竖屏、架构） |
| `assets/icon.png` | 应用图标 |
| `.github/workflows/build-android.yml` | GitHub Actions 云端打包 |
| `scripts/build-android-ci.sh` | 云端/CI 构建脚本 |
| `wsl-setup.sh` | WSL 一键安装依赖 |
| `wsl-build-debug.sh` | WSL 快捷 Debug 构建 |
| `scripts/generate-keystore.sh` | 生成签名密钥 |
| `scripts/build-release.sh` | 构建签名 Release APK |
| `scripts/generate_assets.py` | 重新生成图标/闪屏 |
