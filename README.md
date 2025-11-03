## RetroArch Playlist Generator (v0.51)

### ✨ 🚀 项目简介

这是一个基于 Python 和 **CustomTkinter** 的现代化图形界面（GUI）工具，专为 **RetroArch** 模拟器设计。它旨在帮助用户批量扫描本地 ROM 文件，并自动生成符合 RetroArch 规范的 **LPL 播放列表文件**。

本版本 **v0.51** 采用了 CustomTkinter 框架重制，界面更加美观、现代化，并支持深色模式。

**核心特色:**

* **CustomTkinter 界面:** 提供更美观、响应式的现代 GUI 体验。
* **双平台核心支持:** 轻松切换 Windows 和 Switch 等不同平台的核心路径配置。
* **内置 ROM 路径编辑:** 允许用户在生成前对单个 ROM 的显示名称、路径进行精细化修改。
    * **新增:** **双击** 中间列表的 ROM 路径，可快速选择新文件替换路径。
* **缩略图路径生成与替换:** 支持双击预览框直接添加或替换缩略图，并将其保存到正确的 `thumbnails` 目录结构中。
* **列表名下拉加载:** 从 RetroArch 目录自动扫描并加载现有 `.lpl` 文件名，方便切换和编辑。

---

### 📦 如何获取和运行

#### 选项一：下载可执行文件 (.exe) (推荐)

对于 Windows 用户，这是最简单的运行方式。您无需安装 Python 或任何依赖库。

1.  访问 **[GitHub Releases 页面]** (请替换为您项目的实际 Releases 链接)。
2.  下载最新的 `RetroArch_Playlist_Generator_v0.51.exe` 文件。
3.  双击运行即可。

#### 选项二：运行 Python 源代码 (.py)

如果您是其他系统用户（如 Linux/macOS）或希望从源码运行，需要 Python 3.8+ 环境。

1.  **克隆或下载文件:**
    将 `rom_playlist_generator_v0.51.py` 文件下载到本地。

2.  **安装依赖:** 本工具依赖于 `customtkinter` 和 `Pillow` 库。

    ```bash
    pip install customtkinter pillow
    ```

3.  **运行脚本:**
    ```bash
    python rom_playlist_generator_v0.51.py
    ```

---

### 🛠️ 开发者：使用 PyInstaller 打包为 EXE

如果您对代码进行了修改，并希望打包成单文件 `.exe` 进行分发，推荐使用 PyInstaller。

1.  **安装 PyInstaller:**
    ```bash
    pip install pyinstaller
    ```

2.  **执行打包命令:**
    导航到 `rom_playlist_generator_v0.51.py` 所在的目录，然后运行以下命令。此命令确保 CustomTkinter 的主题资源被正确集成。

    ```bash
    pyinstaller --noconfirm --onefile --windowed --name "RetroArch_Playlist_Generator_V051" --hidden-import "customtkinter" --collect-all "customtkinter" "rom_playlist_generator_v0.51.py"
    ```

3.  最终的 `.exe` 文件将在 `dist` 文件夹内生成。

---

### 💡 使用指南 (v0.51)

1.  点击 **"选择 RA 目录"** 设置您的 RetroArch 配置文件夹（通常包含 `playlists` 和 `thumbnails` 文件夹）。
2.  使用 **"加载 .lpl"** 按钮或右侧的下拉菜单加载现有列表。
3.  使用 **"添加 ROM"** 或 **"添加文件夹"** 将新游戏导入列表。
4.  在底部设置目标 **平台** 和 **核心**，为整个列表指定默认配置。
5.  **精细化编辑：**
    * 双击 **ROM 路径**（中间列表），可选择新文件来修改单个游戏的路径。
    * 双击 **缩略图预览框**，可上传图片替换当前模式下的缩略图（仅支持模式 1, 2, 3）。
6.  设置完成后，点击 **"保存 .lpl"** 生成或更新播放列表文件。

---

**本项目由原作者 @爱折腾的老家伙 与 Google Gemini 配合开发及优化。**