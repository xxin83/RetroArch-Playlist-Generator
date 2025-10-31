# RetroArch Playlist Generator (v0.40)

## 🎮 项目简介

这是一个基于 Python 和 Tkinter 的图形界面（GUI）工具，专为 **RetroArch** 模拟器设计。它可以帮助用户批量扫描本地 ROM 文件，并自动生成符合 RetroArch 规范的 **LPL 播放列表文件**。

**本项目由原作者 @爱折腾的老家伙 与 Google Gemini 配合开发及优化。**

**核心特色:**
* **双平台核心支持:** 轻松切换 Windows 和 Switch 等不同平台的核心路径配置。
* **内置 ROM 路径编辑:** 允许用户在生成前对单个 ROM 的路径、核心进行精细化修改。
* **缩略图路径生成与替换:** 支持双击预览框直接添加或替换缩略图，并将其保存到正确的 `thumbnails` 目录结构中。
* **图形化界面:** 简单直观的操作界面，无需手动编辑复杂的 JSON 或 LPL 文件。

## 📦 如何获取和运行

### 选项一：下载可执行文件 (.exe) (推荐)

对于 Windows 用户，这是最简单的运行方式。您无需安装 Python 或任何依赖库。

1.  访问 [GitHub Releases 页面](https://github.com/xxin83/RetroArch-Playlist-Generator/releases)。
2.  下载最新的 `RetroArch_Playlist_Generator_v0.40.exe` 文件。
3.  双击运行即可。

### 选项二：运行 Python 源代码 (.py)

如果您是其他系统用户（如 Linux/macOS）或希望从源码运行：

1.  **克隆仓库:**
    ```bash
    git clone [https://github.com/xxin83/RetroArch-Playlist-Generator.git](https://github.com/xxin83/RetroArch-Playlist-Generator.git)
    cd RetroArch-Playlist-Generator
    ```

2.  **安装依赖:** 本工具依赖于 `Pillow` 库来处理 GUI 中的图像。
    ```bash
    pip install pillow
    ```

3.  **运行程序:**
    ```bash
    python rom_playlist_generator_v0.40.py
    ```

## ⚙️ 使用说明

1.  **选择平台:** 在界面中选择您的目标平台（如 Windows 或 Switch），程序将自动加载对应平台的默认核心路径。
2.  **选择 RetroArch 根目录:** 指定您的 RetroArch 安装目录。
3.  **选择 ROM 文件夹:** 选择包含您 ROM 文件的文件夹。
4.  **生成列表:** 程序将根据 ROM 扩展名自动匹配核心信息并生成播放列表。
5.  **编辑/导出:** 在详细列表中检查并修改 ROM 路径，然后点击导出按钮生成 `.lpl` 文件。

## ✨ 新增功能与优化 (v0.40)

* **代码优化:** 代码结构精简，清除了冗余和不必要的注释，使代码更加简洁易读。
* **窗口优化:** GUI 窗口默认启动时最大化 (`self.state('zoomed')`)，提升用户体验。
* **缩略图替换:** 支持双击左/右侧预览框，直接选择本地图片替换或新增缩略图文件。
* **版本更新:** 文件名从 `rom_playlist_generator_v0.39.py` 更新为 `rom_playlist_generator_v0.40.py`。

## 许可协议

本项目使用 [MIT License](LICENSE) 开源。您可以自由使用、修改和分发。

---