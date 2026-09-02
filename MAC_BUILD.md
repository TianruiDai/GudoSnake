# Gudo Snake macOS 打包指南

在 Mac 上生成可直接双击运行的 `GudoSnake.app`。

> **说明**：PyInstaller **不能**在 Windows 上交叉编译 macOS 程序，必须在 Mac 本机构建，或通过 GitHub Actions 自动构建。

---

## 1. 在 Mac 上本地构建

```bash
cd /path/to/gudosnake
bash scripts/build-mac.sh
```

构建完成后：

- 应用：`dist/GudoSnake.app`（双击运行）
- 压缩包：`dist/GudoSnake-mac.zip`（方便分发）

首次运行若被 Gatekeeper 拦截，请 **右键 → 打开**，或执行：

```bash
xattr -cr dist/GudoSnake.app
open dist/GudoSnake.app
```

---

## 2. 手动构建（可选）

```bash
python3 -m venv .venv-mac
source .venv-mac/bin/activate
pip install pyinstaller pygame-ce pyyaml
pyinstaller --noconfirm --clean GudoSnake-mac.spec
```

---

## 3. 通过 GitHub Actions 构建

仓库已包含 `.github/workflows/build-mac.yml`。在 GitHub 网页：

1. 打开 **Actions** → **Build macOS App**
2. 点击 **Run workflow**
3. 完成后在 Artifacts 中下载 `GudoSnake-mac.zip`

---

## 4. 与 Windows 版的区别

| 平台 | 入口 | 产物 |
|------|------|------|
| Windows | `demo.py` / `SnakeGame.spec` | `dist/SnakeGame.exe` |
| macOS | `main.py` / `GudoSnake-mac.spec` | `dist/GudoSnake.app` |

macOS 版使用 `main.py`（竖屏 + 虚拟按键界面），与 Android 版一致。

---

## 5. 常见问题

**Q: 能在 Windows 上直接打出 .app 吗？**  
A: 不能。请在 Mac 上运行 `scripts/build-mac.sh`，或使用 GitHub Actions。

**Q: 提示「已损坏，无法打开」？**  
A: 未签名的应用常见此提示。执行 `xattr -cr dist/GudoSnake.app` 后右键打开即可。

**Q: 键盘操作？**  
A: 支持 WASD、Shift 加速、R 重开、Esc 退出。
