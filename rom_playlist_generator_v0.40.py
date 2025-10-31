"""
开源声明：
本软件为开源项目，旨在帮助 RetroArch 用户生成和管理播放列表。
您可以自由修改、复制和分发本软件的源代码。

- 作者不对软件的任何使用后果负责，包括但不限于数据丢失或硬件损坏。
- 如果您对软件进行了改进，欢迎分享回原作者或社区，但非强制要求。

原作者：@爱折腾的老家伙
版本：V0.40
如有问题，请通过适当渠道联系作者。
"""

import os
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk
import threading
from collections import OrderedDict
import subprocess
import platform

# 缩略图模式映射表
MODE_TO_CN = {
    0: "0 | 禁用", 
    1: "1 | 截图 (Snap)", 
    2: "2 | 标题 (Title)",
    3: "3 | 封面 (Boxart)", 
    4: "4 | 优先封面 (Prefer Boxart)", 
    5: "5 | 优先标题 (Prefer Title)"
}
CN_TO_MODE = {v: k for k, v in MODE_TO_CN.items()}
THUMBNAIL_MODES_DISPLAY = list(MODE_TO_CN.values())

# --- 核心路径和名称的平台映射 ---
# Windows 核心配置 (使用相对路径和 .dll)
WINDOWS_MAPPING = {
    "ext_map": { 
        '.nes':  "cores\\nestopia_libretro.dll", 
        '.gb':   "cores\\gambatte_libretro.dll",
        '.gbc':  "cores\\gambatte_libretro.dll",
        '.gba':  "cores\\mgba_libretro.dll",
        '.sfc':  "cores\\snes9x2010_libretro.dll",
        '.smc':  "cores\\snes9x2010_libretro.dll",
        '.md':   "cores\\genesis_plus_gx_libretro.dll",
        '.gg':   "cores\\genesis_plus_gx_libretro.dll",
        '.z64':  "cores\\mupen64plus_next_libretro.dll",
        '.n64':  "cores\\mupen64plus_next_libretro.dll",
        '.bin':  "cores\\pcsx_rearmed_libretro.dll",
        '.cue':  "cores\\pcsx_rearmed_libretro.dll",
        '.iso':  "cores\\pcsx_rearmed_libretro.dll",
        '.chd':  "cores\\flycast_libretro.dll",
        '.pbp':  "cores\\ppsspp_libretro.dll",
        '.elf':  "cores\\pcsx2_libretro.dll",
        '.cso':  "cores\\ppsspp_libretro.dll",
        '.exe':  "cores\\dosbox_pure_libretro.dll",
        '.zip':  "cores\\fbneo_libretro.dll",
        '.m3u':  "cores\\mame_libretro.dll",
    },
    "name_map": {
        "cores\\snes9x2010_libretro.dll": "Nintendo - SNES / SFC (Snes9x 2010)",
        "cores\\nestopia_libretro.dll": "Nintendo - NES / Famicom (Nestopia UE)",
        "cores\\gambatte_libretro.dll": "Nintendo - GB / GBC (Gambatte)",
        "cores\\mgba_libretro.dll": "Nintendo - GBA (mGBA)",
        "cores\\genesis_plus_gx_libretro.dll": "Sega - MD/GG (Genesis Plus GX)",
        "cores\\mupen64plus_next_libretro.dll": "Nintendo 64 (Mupen64Plus-Next)",
        "cores\\pcsx_rearmed_libretro.dll": "Sony - PS1 (PCSX ReARMed)",
        "cores\\flycast_libretro.dll": "Sega - DC (Flycast)",
        "cores\\ppsspp_libretro.dll": "Sony - PSP (PPSSPP)",
        "cores\\pcsx2_libretro.dll": "Sony - PS2 (PCSX2)",
        "cores\\dosbox_pure_libretro.dll": "DOS (DOSBox-Pure)",
        "cores\\fbneo_libretro.dll": "Arcade (FinalBurn Neo)",
        "cores\\mame_libretro.dll": "Arcade (MAME)",
    },
    "default_core": "cores\\snes9x2010_libretro.dll",
}
# Nintendo Switch 核心配置 (使用绝对路径和 .nro)
SWITCH_MAPPING = {
    "ext_map": {
        '.nes':  "/retroarch/cores/nestopia_libretro_libnx.nro",
        '.gb':   "/retroarch/cores/gambatte_libretro_libnx.nro",
        '.gbc':  "/retroarch/cores/gambatte_libretro_libnx.nro",
        '.gba':  "/retroarch/cores/mgba_libretro_libnx.nro",
        '.sfc':  "/retroarch/cores/snes9x2010_libretro_libnx.nro",
        '.smc':  "/retroarch/cores/snes9x2010_libretro_libnx.nro",
        '.md':   "/retroarch/cores/genesis_plus_gx_libretro_libnx.nro",
        '.gg':   "/retroarch/cores/genesis_plus_gx_libretro_libnx.nro",
        '.z64':  "/retroarch/cores/mupen64plus_next_libretro_libnx.nro",
        '.n64':  "/retroarch/cores/mupen64plus_next_libretro_libnx.nro",
        '.bin':  "/retroarch/cores/pcsx_rearmed_libretro_libnx.nro",
        '.cue':  "/retroarch/cores/pcsx_rearmed_libretro_libnx.nro",
        '.iso':  "/retroarch/cores/pcsx_rearmed_libretro_libnx.nro",
        '.chd':  "/retroarch/cores/flycast_libretro_libnx.nro",
        '.pbp':  "/retroarch/cores/ppsspp_libretro_libnx.nro",
        '.elf':  "/retroarch/cores/pcsx2_libretro_libnx.nro",
        '.cso':  "/retroarch/cores/ppsspp_libretro_libnx.nro",
        '.exe':  "/retroarch/cores/dosbox_pure_libretro_libnx.nro",
        '.zip':  "/retroarch/cores/fbneo_libretro_libnx.nro",
        '.m3u':  "/retroarch/cores/mame_libretro_libnx.nro",
    },
    "name_map": {
        "/retroarch/cores/snes9x2010_libretro_libnx.nro": "Nintendo - SNES / SFC (Snes9x 2010)",
        "/retroarch/cores/nestopia_libretro_libnx.nro": "Nintendo - NES / Famicom (Nestopia UE)",
        "/retroarch/cores/gambatte_libretro_libnx.nro": "Nintendo - GB / GBC (Gambatte)",
        "/retroarch/cores/mgba_libretro_libnx.nro": "Nintendo - GBA (mGBA)",
        "/retroarch/cores/genesis_plus_gx_libretro_libnx.nro": "Sega - MD/GG (Genesis Plus GX)",
        "/retroarch/cores/mupen64plus_next_libretro_libnx.nro": "Nintendo 64 (Mupen64Plus-Next)",
        "/retroarch/cores/pcsx_rearmed_libretro_libnx.nro": "Sony - PS1 (PCSX ReARMed)",
        "/retroarch/cores/flycast_libretro_libnx.nro": "Sega - DC (Flycast)",
        "/retroarch/cores/ppsspp_libretro_libnx.nro": "Sony - PSP (PPSSPP)",
        "/retroarch/cores/pcsx2_libretro_libnx.nro": "Sony - PS2 (PCSX2)",
        "/retroarch/cores/dosbox_pure_libretro_libnx.nro": "DOS (DOSBox-Pure)",
        "/retroarch/cores/fbneo_libretro_libnx.nro": "Arcade (FinalBurn Neo)",
        "/retroarch/cores/mame_libretro_libnx.nro": "Arcade (MAME)",
    },
    "default_core": "/retroarch/cores/snes9x2010_libretro_libnx.nro",
}

PLATFORM_MAPPING = {
    "Windows": WINDOWS_MAPPING,
    "Switch": SWITCH_MAPPING,
}

def get_all_cores_list():
    """获取所有平台的可用核心列表，并格式化为显示名称 (支持平台)。"""
    all_cores = {}
    for platform in PLATFORM_MAPPING:
        name_map = PLATFORM_MAPPING[platform]["name_map"]
        for core_path, core_name in name_map.items():
            if core_name not in all_cores:
                 all_cores[core_name] = {}
            all_cores[core_name][platform] = core_path

    display_list = []
    # 按核心名称排序
    sorted_all_cores = OrderedDict(sorted(all_cores.items(), key=lambda item: item[0]))
    
    for core_name, paths in sorted_all_cores.items():
        platforms = ", ".join(sorted(paths.keys()))
        display_list.append(f"{core_name} ({platforms})")
        
    return display_list

# --- 动态核心选择函数 ---
def suggest_core_by_extension(file_path, platform):
    """根据文件扩展名和目标平台建议核心路径。"""
    ext = Path(file_path).suffix.lower()
    platform_data = PLATFORM_MAPPING.get(platform)
    if not platform_data: return "" 
    mapping = platform_data['ext_map']
    default_core = platform_data['default_core']
    return mapping.get(ext, default_core)

# --- 动态核心名称获取函数 ---
def get_core_name(core_path, platform):
    """根据核心路径和平台获取友好的核心名称。"""
    platform_data = PLATFORM_MAPPING.get(platform)
    if not platform_data: return "Unknown Core"
    name_map = platform_data['name_map']
    return name_map.get(core_path, "Unknown Core")

def filter_rom_files(files, extensions=None):
    """从文件列表中过滤出 ROM 文件。"""
    if extensions is None:
        extensions = [
            '.nes', '.gb', '.gbc', '.gba', '.sfc', '.smc',
            '.zip', '.7z', '.bin', '.cue', '.iso', '.chd',
            '.pbp', '.elf', '.cso', '.exe', '.md', '.gg',
            '.z64', '.n64', '.m3u'
        ]
    roms = []
    for fp in files:
        if any(fp.lower().endswith(ext) for ext in extensions):
            # 统一路径分隔符为 '/'
            rom_path = os.path.normpath(fp).replace('\\', '/')
            roms.append({
                'path': rom_path,
                'label': Path(fp).stem,
            })
    return roms


def load_playlist(playlist_path):
    """加载 LPL 文件，返回 roms 列表、设置和核心路径。"""
    try:
        with open(playlist_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        with open(playlist_path, 'r', encoding='latin-1') as f:
            data = json.load(f)
    except Exception as e:
        raise Exception(f"文件编码或 JSON 格式错误: {e}")
    
    roms = []
    for item in data.get('items', []):
        roms.append({
            'path': item.get('path', ''),
            'label': item.get('label', Path(item.get('path', '')).stem or 'Unknown')
        })
    settings = {
        'label_display_mode': data.get('label_display_mode', 0),
        'right_thumbnail_mode': data.get('right_thumbnail_mode', 4),
        'left_thumbnail_mode': data.get('left_thumbnail_mode', 2),
        'thumbnail_match_mode': data.get('thumbnail_match_mode', 0),
    }
    
    core_path = data.get('default_core_path', '')
    
    return roms, settings, core_path 


def generate_playlist(roms, playlist_path, core_path, settings, platform):
    """生成 LPL 文件。"""
    core_name = get_core_name(core_path, platform)
    playlist = {
        "version": "1.5",
        "default_core_path": core_path,
        "default_core_name": core_name,
        "label_display_mode": settings['label_display_mode'],
        "right_thumbnail_mode": settings['right_thumbnail_mode'],
        "left_thumbnail_mode": settings['left_thumbnail_mode'],
        "thumbnail_match_mode": settings['thumbnail_match_mode'],
        "sort_mode": 2,
        "items": [
            {
                "path": r['path'],
                "label": r['label'],
                "core_path": core_path,
                "core_name": core_name,
                "crc32": "DETECT", 
                "db_name": Path(playlist_path).stem + ".lpl" 
            } for r in roms
        ]
    }
    with open(playlist_path, 'w', encoding='utf-8') as f:
        json.dump(playlist, f, indent=2, ensure_ascii=False)
    return len(roms)


class PlaylistGenerator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RetroArch 播放列表生成器 V0.40（@爱折腾的老家伙）") 
        self.configure(bg='#f0f0f0')

        # 实例变量
        self.rom_list = []
        self.retroarch_dir = tk.StringVar()
        self.current_lpl_name = "" # 当前列表的名称（不含.lpl）
        self.last_selection_id = 0 # 用于异步加载缩略图的请求ID
        
        # 缩略图模式设置变量
        self.playlist_settings = {
            'label_display_mode': tk.IntVar(value=0), 
            'right_thumbnail_mode': tk.IntVar(value=4),
            'left_thumbnail_mode': tk.IntVar(value=2),
            'thumbnail_match_mode': tk.IntVar(value=0),
        }
        # Combobox 关联的字符串变量
        self.settings_vars_str = {
            'right_thumbnail_mode': tk.StringVar(value=MODE_TO_CN[4]),
            'left_thumbnail_mode': tk.StringVar(value=MODE_TO_CN[2]),
        }
        
        # --- 平台选择和核心变量 ---
        self.selected_platform = tk.StringVar(value="Windows") 
        self.core_list = get_all_cores_list()
        self.selected_core = tk.StringVar(value=self.core_list[0] if self.core_list else "") 
        self.playlist_name = tk.StringVar(value="MyPlaylist")

        # UI 组件
        self.rom_detail = None
        self.rom_name_list = None
        self.thumb_label = None # 左侧缩略图
        self.right_thumb_label = None # 右侧缩略图
        self.playlist_name_combo = None
        self.preview = None
        self.path_btn = None
        self.path_debug_label = None
        self.selected_rom_name_display = None
        self.right_path_debug_label = None
        self.core_combo = None
        self.platform_combo = None

        self.build_ui()

        # --- 窗口最大化设置 ---
        try:
             # 'zoomed' 适用于 Windows 和部分 Linux (X11) 环境
             self.state('zoomed') 
        except tk.TclError:
             # 某些系统可能不支持 'zoomed'
             pass 
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 初始刷新
        self.on_platform_change() 

    def build_ui(self):
        # 顶部工具栏 (Top Bar)
        top = tk.Frame(self, bg='#f0f0f0')
        top.pack(fill='x', padx=10, pady=8)

        tk.Button(top, text="选择 RetroArch 目录", command=self.select_retroarch_dir,
                  bg='#44475a', fg='white', width=18).pack(side='left', padx=3)
        tk.Label(top, textvariable=self.retroarch_dir, bg='#f0f0f0', fg='blue', width=50, anchor='w').pack(side='left', padx=5)

        tk.Button(top, text="加载 .lpl", command=self.load_lpl, bg='#bb86fc', fg='white', width=10).pack(side='left', padx=3)
        tk.Button(top, text="保存 .lpl", command=self.do_save, bg='#ffb86c', fg='black', width=10).pack(side='left', padx=3) 
        tk.Button(top, text="清空列表", command=self.clear_list, bg='#cf6679', fg='white', width=10).pack(side='left', padx=3)
        tk.Button(top, text="帮助", command=self.show_help, bg='#6272a4', fg='white', width=10).pack(side='left', padx=3) 

        tk.Label(top, text="列表名:", bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(side='left', padx=10)
        
        # 列表名 Combobox
        self.playlist_name_combo = ttk.Combobox(
            top, 
            textvariable=self.playlist_name, 
            width=20, 
            values=[], 
        )
        self.playlist_name_combo.pack(side='left', padx=3)
        self.playlist_name_combo.bind("<<ComboboxSelected>>", self.load_playlist_on_select)

        # 中间主工作区域：水平 PanedWindow (分割左、中、右)
        mid = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        mid.pack(fill='both', expand=True, padx=10, pady=5)
        
        # ------------------ 1. 左侧容器：垂直 PanedWindow ------------------
        left_v_pane = ttk.PanedWindow(mid, orient=tk.VERTICAL)
        mid.add(left_v_pane, weight=0) 

        name_frame = tk.LabelFrame(left_v_pane, text=" 选中 ROM 名称 ", bg='#f0f0f0')
        left_v_pane.add(name_frame, weight=0) 
        
        self.selected_rom_name_display = tk.Text(name_frame, height=2, width=25, wrap='word', bg='#e0e0e0', relief='sunken', font=('Arial',10, 'bold'), borderwidth=1)
        self.selected_rom_name_display.pack(fill='x', padx=5, pady=(5, 50)) 
        self.selected_rom_name_display.insert('end', "请加载 LPL 或添加 ROM...")
        self.selected_rom_name_display.config(state=tk.DISABLED)

        left_thumb_options_container = tk.LabelFrame(left_v_pane, text=" 预览 (左侧图) ", bg='#f0f0f0')
        left_v_pane.add(left_thumb_options_container, weight=1) 

        thumb_frame = tk.Frame(left_thumb_options_container, bg='white', relief='sunken', bd=2, height=250, width=200) 
        thumb_frame.pack(fill='x', pady=(5, 0), padx=5) 
        thumb_frame.pack_propagate(False) 
        self.thumb_label = tk.Label(thumb_frame, text="选择 ROM 查看缩略图", bg='white', fg='gray')
        self.thumb_label.pack(expand=True)
        # 绑定双击事件，用于替换缩略图
        self.thumb_label.bind('<Double-1>', lambda e: self.replace_thumbnail('left'))
        
        left_mode_frame = tk.Frame(left_thumb_options_container, bg='#f0f0f0')
        left_mode_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(left_mode_frame, text="左侧图选项:", bg='#f0f0f0', font=('Arial', 9)).pack(side='left', padx=(0,5))
        left_mode_combo = ttk.Combobox(left_mode_frame, textvariable=self.settings_vars_str['left_thumbnail_mode'],
                                 values=THUMBNAIL_MODES_DISPLAY, state="readonly", width=15)
        left_mode_combo.pack(side='left')
        left_mode_combo.bind("<<ComboboxSelected>>", lambda e: self.update_thumbnail_mode('left_thumbnail_mode'))
        
        self.path_debug_label = tk.Label(left_thumb_options_container, text="", wraplength=240, justify=tk.LEFT, bg='#f0f0f0', font=('Arial', 8), height=15, anchor='n')
        self.path_debug_label.pack(fill='x', padx=5, pady=2)


        # ------------------ 2. 中间容器：ROM 路径列表 & 底部按钮 ------------------
        center_container = tk.Frame(mid)
        mid.add(center_container, weight=1) 
        
        center = tk.LabelFrame(center_container, text=" ROM 列表 ", bg='#f0f0f0')
        center.pack(fill='both', expand=True, padx=3, pady=0)

        center_list_frame = tk.Frame(center)
        center_list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        sb_center = tk.Scrollbar(center_list_frame, orient="vertical")
        sb_center.pack(side="right", fill="y")
        
        center_v_pane = ttk.PanedWindow(center_list_frame, orient=tk.HORIZONTAL)
        center_v_pane.pack(side="left", fill='both', expand=True) 

        self.rom_name_list = tk.Listbox(center_v_pane, font=("Consolas", 9), width=50, selectmode=tk.SINGLE, 
                                   exportselection=False, relief='flat', activestyle='none')
        center_v_pane.add(self.rom_name_list, weight=0) 
        self.rom_name_list.bind('<Button-1>', lambda e: "break")
        self.rom_name_list.bind('<<ListboxSelect>>', lambda e: self.rom_name_list.selection_clear(0, 'end')) 

        self.rom_detail = tk.Listbox(center_v_pane, font=("Consolas", 9), selectmode=tk.SINGLE, exportselection=False)
        center_v_pane.add(self.rom_detail, weight=1) 
        
        # 统一设置列表框滚动条
        def on_scroll_yview(*args):
            self.rom_detail.yview(*args)
            self.rom_name_list.yview(*args)

        sb_center.config(command=on_scroll_yview)
        self.rom_detail.config(yscrollcommand=sb_center.set)
        self.rom_name_list.config(yscrollcommand=sb_center.set)

        center_bottom_frame = tk.Frame(center_container, bg='#f0f0f0')
        center_bottom_frame.pack(fill='x', pady=5)
        
        tk.Button(center_bottom_frame, text="添加 ROM", command=self.add_single_rom,
                  bg='#03dac6', fg='black', width=12).pack(side='left', padx=10) 
        tk.Button(center_bottom_frame, text="添加文件夹", command=self.add_folder_roms,
                  bg='#018786', fg='white', width=12).pack(side='left', padx=10) 
                  
        tk.Button(center_bottom_frame, text="编辑名称", command=self.edit_rom_label,
                  bg='#ffb86c', fg='black', width=12).pack(side='left', padx=10)
        tk.Button(center_bottom_frame, text="删除选中", command=self.delete_rom,
                  bg='#ff5555', fg='white', width=12).pack(side='left', padx=10)
                  
        self.path_btn = tk.Button(center_bottom_frame, text="全局修改路径", command=self.global_edit_rom_path,
                             bg='#03dac6', fg='black', width=12, state='normal')
        self.path_btn.pack(side='left', padx=10)
        
        # 按钮
        tk.Button(center_bottom_frame, text="复制名称", command=self.copy_rom_name,
                  bg='#8be9fd', fg='black', width=12).pack(side='left', padx=10)


        # ------------------ 3. 右侧容器：垂直 PanedWindow ------------------
        right_v_pane = ttk.PanedWindow(mid, orient=tk.VERTICAL)
        mid.add(right_v_pane, weight=0) 
        
        preview_text_container = tk.LabelFrame(right_v_pane, text=" 预览文本 ", bg='#f0f0f0')
        right_v_pane.add(preview_text_container, weight=0) 

        preview_frame = tk.Frame(preview_text_container)
        preview_frame.pack(fill='both', expand=True, pady=5, padx=5)

        self.preview = tk.Text(preview_frame, height=6, width=25, wrap='word', bg='white', font=("Consolas", 9))
        sb_prev = tk.Scrollbar(preview_frame, orient="vertical", command=self.preview.yview)
        self.preview.configure(yscrollcommand=sb_prev.set)
        self.preview.pack(side="left", fill="both", expand=True)
        sb_prev.pack(side="right", fill="y")
        self.preview.insert('end', "选择 ROM 查看预览...")
        
        right_thumb_frame_container = tk.LabelFrame(right_v_pane, text=" 预览 (右侧图)  ", bg='#f0f0f0')
        right_v_pane.add(right_thumb_frame_container, weight=1) 
        
        thumb_frame_right = tk.Frame(right_thumb_frame_container, bg='white', relief='sunken', bd=2, height=250, width=200) 
        thumb_frame_right.pack(fill='x', pady=5, padx=5)
        thumb_frame_right.pack_propagate(False)
        
        self.right_thumb_label = tk.Label(thumb_frame_right, text="选择 ROM 查看右侧图", bg='white', fg='gray')
        self.right_thumb_label.pack(expand=True)
        # 绑定双击事件，用于替换缩略图
        self.right_thumb_label.bind('<Double-1>', lambda e: self.replace_thumbnail('right'))
        
        right_mode_frame = tk.Frame(right_thumb_frame_container, bg='#f0f0f0')
        right_mode_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(right_mode_frame, text="右侧图选项:", bg='#f0f0f0', font=('Arial', 9)).pack(side='left', padx=(0,5))
        right_mode_combo = ttk.Combobox(right_mode_frame, textvariable=self.settings_vars_str['right_thumbnail_mode'],
                                  values=THUMBNAIL_MODES_DISPLAY, state="readonly", width=15)
        right_mode_combo.pack(side='left')
        right_mode_combo.bind("<<ComboboxSelected>>", lambda e: self.update_thumbnail_mode('right_thumbnail_mode'))

        self.right_path_debug_label = tk.Label(right_thumb_frame_container, text="", wraplength=240, justify=tk.LEFT, bg='#f0f0f0', font=('Arial', 8), height=15, anchor='n')
        self.right_path_debug_label.pack(fill='x', padx=5, pady=2)

        # ------------------ 4. 核心和平台选择区 (Core Row) ------------------
        core_container = tk.Frame(self, bg='#f0f0f0')
        core_container.pack(fill='x', padx=10, pady=(5, 8)) 
        
        core_frame = tk.LabelFrame(core_container, text=" 核心和平台选择 ", bg='#f0f0f0')
        core_frame.pack(fill='x', padx=3, pady=0)

        tk.Label(core_frame, text="目标平台:", bg='#f0f0f0', font=('Arial', 9, 'bold')).pack(side='left', padx=(5, 0), pady=5)
        self.platform_combo = ttk.Combobox(core_frame, textvariable=self.selected_platform, 
                                      values=list(PLATFORM_MAPPING.keys()), state="readonly", width=10)
        self.platform_combo.pack(side='left', padx=5, pady=2)
        self.platform_combo.bind("<<ComboboxSelected>>", self.on_platform_change)

        tk.Label(core_frame, text="选择核心:", bg='#f0f0f0', font=('Arial', 9, 'bold')).pack(side='left', padx=10, pady=5)
        self.core_combo = ttk.Combobox(core_frame, textvariable=self.selected_core, values=self.core_list, state="readonly")
        self.core_combo.pack(fill='x', padx=5, pady=2, expand=True)
        self.core_combo.bind("<<ComboboxSelected>>", self.on_core_change)
        
        # **事件绑定**
        self.rom_detail.bind('<<ListboxSelect>>', self.sync_selection_and_refresh)

    # ------------------ 缩略图/预览 UI 更新函数 ------------------
    
    def _update_thumb_label_safe(self, request_id, photo, target_thumb_label, target_path_debug_label, search_results, error_text=None):
        """线程安全地更新缩略图和路径报告。"""
        if request_id < self.last_selection_id: return
        current_rom_name = "N/A"
        sel = self.rom_detail.curselection()
        if sel and sel[0] < len(self.rom_list):
             current_rom_name = self.rom_list[sel[0]]['label']
        
        # --- 路径显示逻辑：生成详细的搜索报告 ---
        path_report = ["--- 缩略图搜索报告 ---"]
        path_fg_color = 'darkgray'
        
        if search_results:
            for status, mode_cn, path in search_results:
                if status == "Found":
                    path_report.append(f"✅ 找到 ({mode_cn}): {Path(path).name}")
                    path_fg_color = 'darkgreen'
                elif status == "Failed_Load":
                    path_report.append(f"⚠️ 文件损坏 ({mode_cn}): {Path(path).name}")
                    path_fg_color = 'darkred'
                else:
                    path_report.append(f"❌ 未找到 ({mode_cn}): {Path(path).name}")
            
            if photo is None and path_fg_color == 'darkgreen':
                path_fg_color = 'darkred'
                
            path_display = "\n".join(path_report)
        else:
            path_display = error_text if error_text else "缩略图模式已禁用或列表为空。"
            path_fg_color = 'darkred'

        # 更新缩略图主标签
        if photo is not None:
            target_thumb_label.config(image=photo, text="")
            target_thumb_label.image = photo 
            target_path_debug_label.config(text=path_display, fg='darkgreen')
        else:
            # 增强提示：双击添加
            target_thumb_label.config(image='', text=f"未找到缩略图:\n{current_rom_name}\n\n双击此处添加", fg='gray')
            target_path_debug_label.config(text=path_display, fg=path_fg_color)
            target_thumb_label.image = None

    def _create_photo_and_update(self, request_id, img, target_thumb_label, target_path_debug_label, search_results, full_path):
        """在主线程中创建 PhotoImage 并更新 UI。"""
        if request_id < self.last_selection_id: return
        try:
            photo = ImageTk.PhotoImage(img) 
            self._update_thumb_label_safe(request_id, photo, target_thumb_label, target_path_debug_label, search_results)
        except Exception as e:
            error_text = f"缩略图创建失败: {Path(full_path).name}\n错误: {e}"
            self._update_thumb_label_safe(request_id, None, target_thumb_label, target_path_debug_label, search_results, error_text)

    def _load_thumbnail_async_worker(self, rom, ra_path_root, lpl_name_root, mode_val_to_use, target_thumb_label, target_path_debug_label, request_id):
        """异步加载缩略图文件。"""
        if request_id < self.last_selection_id: return
        if rom is None: return
        try: thumbnail_name = Path(rom['path']).stem
        except Exception: thumbnail_name = rom['label']
        
        final_modes = []
        mode_to_use = int(mode_val_to_use)
        if mode_to_use == 5: final_modes.extend([2, 3, 1]) 
        elif mode_to_use == 4: final_modes.extend([3, 2, 1])
        elif mode_to_use != 0: final_modes.append(mode_to_use)
        final_modes = list(dict.fromkeys(final_modes)) 
        
        search_results = []
        
        folder_map = {1: "Named_Snaps", 2: "Named_Titles", 3: "Named_Boxarts"}

        if mode_to_use == 0 or not lpl_name_root or not ra_path_root:
             path_display_text = "缩略图模式已禁用 (模式 0) 或列表/RA目录未设置。"
             self.after(0, lambda: self._update_thumb_label_safe(request_id, None, target_thumb_label, target_path_debug_label, search_results, path_display_text))
             return
             
        for mode in final_modes:
            if request_id < self.last_selection_id: return
            folder = folder_map.get(mode)
            if not folder: continue
            
            mode_cn = MODE_TO_CN.get(mode, "未知类型")
            # 缩略图路径格式: RA_DIR/thumbnails/PLAYLIST_NAME/FOLDER/ROM_NAME.ext
            path_prefix = Path(ra_path_root) / "thumbnails" / lpl_name_root / folder / thumbnail_name
            
            for ext in ['.png', '.jpg']:
                check_path = path_prefix.with_suffix(ext) 
                check_path_str = str(check_path)
                
                if check_path.exists():
                    try:
                        img = Image.open(check_path)
                        # 缩放以适应预览框 (200x250)
                        img.thumbnail((180, 230), Image.Resampling.LANCZOS)
                        img = img.convert("RGBA") 
                        
                        search_results.append(("Found", mode_cn, check_path_str))
                        
                        self.after(0, lambda: self._create_photo_and_update(request_id, img, target_thumb_label, target_path_debug_label, search_results, check_path_str))
                        return
                        
                    except Exception:
                        search_results.append(("Failed_Load", mode_cn, check_path_str))
                        continue
                else:
                    search_results.append(("Not Found", mode_cn, check_path_str))
                    
        # 如果循环结束仍未找到
        error_text = "所有尝试的路径均未找到有效缩略图文件。"
        self.after(0, lambda: self._update_thumb_label_safe(request_id, None, target_thumb_label, target_path_debug_label, search_results, error_text))


    def update_left_thumbnail(self):
        sel = self.rom_detail.curselection()
        self.thumb_label.config(image='', text="正在加载缩略图...", fg='blue')
        self.path_debug_label.config(text="正在检查文件路径...", fg='darkgray')
        if not sel or not self.rom_list:
            self.thumb_label.config(image='', text="请先选中一个 ROM\n\n双击此处添加", fg='gray')
            self.path_debug_label.config(text="请在中间列表选中一个 ROM", fg='darkgray')
            return
        idx = sel[0]
        if idx >= len(self.rom_list): return
        rom = self.rom_list[idx]
        self.last_selection_id += 1
        current_request_id = self.last_selection_id
        ra_path_root = self.retroarch_dir.get()
        lpl_name_root = self.current_lpl_name
        left_mode_val = self.playlist_settings['left_thumbnail_mode'].get()
        t_left = threading.Thread(
            target=self._load_thumbnail_async_worker,
            args=(rom, ra_path_root, lpl_name_root, left_mode_val, self.thumb_label, self.path_debug_label, current_request_id),
            daemon=True 
        )
        t_left.start()

    def update_right_thumbnail(self):
        sel = self.rom_detail.curselection()
        self.right_thumb_label.config(image='', text="正在加载右侧图...", fg='blue')
        self.right_path_debug_label.config(text="正在检查文件路径...", fg='darkgray')
        if not sel or not self.rom_list:
            self.right_thumb_label.config(image='', text="请先选中一个 ROM\n\n双击此处添加", fg='gray')
            self.right_path_debug_label.config(text="请在中间列表选中一个 ROM", fg='darkgray')
            return
        idx = sel[0]
        if idx >= len(self.rom_list): return
        rom = self.rom_list[idx]
        current_request_id = self.last_selection_id # 使用同一个ID，确保左侧更新时右侧停止
        ra_path_root = self.retroarch_dir.get()
        lpl_name_root = self.current_lpl_name
        right_mode_val = self.playlist_settings['right_thumbnail_mode'].get()
        t_right = threading.Thread(
            target=self._load_thumbnail_async_worker,
            args=(rom, ra_path_root, lpl_name_root, right_mode_val, self.right_thumb_label, self.right_path_debug_label, current_request_id),
            daemon=True 
        )
        t_right.start()


    def update_preview(self):
        """更新右侧文本预览框的内容。"""
        sel = self.rom_detail.curselection()
        if not sel or not self.rom_list:
            self.preview.delete(1.0, 'end')
            self.preview.insert('end', "选择 ROM 查看预览...")
            self.path_btn.config(state='normal') 
            return
        idx = sel[0]
        rom = self.rom_list[idx]
        platform = self.selected_platform.get()
        core_display_text = self.selected_core.get()
        
        core_path = ""
        core_name = ""
        
        # 1. 检查是否为加载 LPL 时的自定义/未知核心格式: "未知核心 (Platform) | core_path"
        if ' | ' in core_display_text: 
            parts = core_display_text.split(' | ')
            if len(parts) == 2:
                core_path = parts[1].strip()
                core_name = parts[0].strip()
            else:
                core_name = "Unknown Core"
                
        # 2. 标准核心选择情况: "Core Name (Platform1, Platform2)"
        else: 
            friendly_name = core_display_text
            
            if core_display_text.endswith(')'):
                try:
                    platform_start_idx = core_display_text.rindex(' (')
                    friendly_name = core_display_text[:platform_start_idx] 
                except ValueError:
                    pass

            platform_data = PLATFORM_MAPPING.get(platform)
            if platform_data:
                core_info = platform_data.get("name_map", {})
                for path, name in core_info.items():
                    if name == friendly_name:
                        core_path = path
                        break
            
            core_name = get_core_name(core_path, platform) 
            
            
        self.preview.delete(1.0, 'end')
        self.preview.insert('end', f"平台：{platform}\n")
        self.preview.insert('end', f"名称：{rom['label']}\n")
        self.preview.insert('end', f"路径：{rom['path']}\n")
        self.preview.insert('end', f"核心路径：{core_path}\n")
        self.preview.insert('end', f"核心名称：{core_name}")
        self.path_btn.config(state='normal')

    def update_ui_only(self, event=None):
        """统一刷新所有 UI 元素。"""
        self.update_preview()
        self.update_left_thumbnail()
        self.update_right_thumbnail()

    def update_thumbnail_mode(self, var_name):
        """更新缩略图模式设置，并刷新预览。"""
        mode_map = CN_TO_MODE
        new_display = self.settings_vars_str[var_name].get()
        new_mode = mode_map.get(new_display, self.playlist_settings[var_name].get())
        self.playlist_settings[var_name].set(new_mode)
        self.after(10, self.update_ui_only) 
        
    def sync_selection_and_refresh(self, idx_or_event=None):
        """同步列表选择状态并刷新 UI。"""
        idx = None
        if isinstance(idx_or_event, int):
            idx = idx_or_event
            if idx >= len(self.rom_list) or idx < 0:
                self.update_ui_only()
                return
        elif idx_or_event is not None:
            try:
                sel = self.rom_detail.curselection() 
                if not sel:
                    sel = self.rom_name_list.curselection() 
                    if not sel:
                        self.update_ui_only(); 
                        return
                idx = sel[0]
            except Exception:
                self.update_ui_only(); 
                return
        else:
            sel = self.rom_detail.curselection()
            if not sel: self.update_ui_only(); return
            idx = sel[0]

        # 确保选择和激活同步
        self.rom_detail.selection_clear(0, 'end')
        self.rom_detail.selection_set(idx)
        self.rom_detail.activate(idx)
        self.rom_detail.see(idx)

        self.rom_name_list.selection_clear(0, 'end')
        self.rom_name_list.selection_set(idx)
        self.rom_name_list.activate(idx)
        self.rom_name_list.see(idx)

        self.selected_rom_name_display.config(state=tk.NORMAL)
        self.selected_rom_name_display.delete(1.0, 'end')
        self.selected_rom_name_display.insert('end', self.rom_list[idx]['label'])
        self.selected_rom_name_display.config(state=tk.DISABLED)

        self.after(10, self.update_ui_only)

    def update_lists(self):
        """刷新列表框内容。"""
        current_selection = self.rom_detail.curselection()
        current_idx = current_selection[0] if current_selection else -1

        self.rom_detail.unbind('<<ListboxSelect>>')

        self.rom_detail.delete(0, 'end')
        self.rom_name_list.delete(0, 'end')

        paths_display = []
        names_display = []
        lpl_name_prefix = f"[{self.current_lpl_name}] " if self.current_lpl_name else ""

        for i, r in enumerate(self.rom_list):
            fp = r['path']
            fp_disp = fp if len(fp) <= 80 else fp[:60] + "..." + fp[-20:]
            paths_display.append(lpl_name_prefix + fp_disp)

            names_display.append(f"[{i+1}] {r['label']}")

        if paths_display:
            self.rom_detail.insert('end', *paths_display)
            self.rom_name_list.insert('end', *names_display)

        self.rom_detail.bind('<<ListboxSelect>>', self.sync_selection_and_refresh)

        if current_idx >= 0 and current_idx < len(self.rom_list):
            self.after(1, lambda: self.sync_selection_and_refresh(current_idx))
        elif self.rom_list:
            self.after(1, lambda: self.sync_selection_and_refresh(0))
        else:
            self.selected_rom_name_display.config(state=tk.NORMAL)
            self.selected_rom_name_display.delete(1.0, 'end')
            self.selected_rom_name_display.insert('end', "列表已清空。")
            self.selected_rom_name_display.config(state=tk.DISABLED)
            self.update_ui_only()

    def on_platform_change(self, event=None):
        """平台选择更改时调用。"""
        self.update_ui_only()

    def on_core_change(self, event=None):
        """核心选择更改时调用。"""
        self.update_ui_only()

    # --- 扫描 RetroArch/playlists 目录，获取现有 .lpl 文件列表 ---
    def scan_existing_playlists(self, ra_dir_val):
        """扫描并更新播放列表名称下拉框。"""
        try:
            playlists_dir = Path(ra_dir_val) / "playlists"
            if not playlists_dir.is_dir():
                # 目录不存在，尝试创建
                playlists_dir.mkdir(parents=True, exist_ok=True)
                
            lpl_files = [f.stem for f in playlists_dir.glob("*.lpl") if f.is_file()]
            lpl_files.sort()

            # 更新 Combobox 值
            self.playlist_name_combo['values'] = lpl_files

            return lpl_files
        except Exception as e:
            messagebox.showerror("错误", f"扫描 playlists 目录时发生错误: {e}")
            return []

    # --- 从路径加载 LPL 文件（内部调用） ---
    def _load_lpl_from_path(self, path):
        """加载指定 LPL 文件并更新程序状态。"""
        try:
            self.rom_list, settings, loaded_core_path = load_playlist(path)
        except Exception as e:
            messagebox.showerror("错误", f"解析 LPL 文件内容时发生错误: {e}\n文件路径: {path}")
            return
            
        self.current_lpl_name = Path(path).stem
        self.playlist_name.set(self.current_lpl_name)
        
        inferred_platform = "Windows" # 默认值
        inferred_name = "Unknown Core"
        
        # 尝试根据核心路径匹配平台和友好名称
        for platform, data in PLATFORM_MAPPING.items():
            if loaded_core_path in data["name_map"]:
                inferred_platform = platform
                inferred_name = data["name_map"][loaded_core_path]
                break
        
        # 设置平台
        self.selected_platform.set(inferred_platform)
        
        # 设置核心
        target_display = ""
        for core_display in self.core_list:
            if core_display.startswith(inferred_name):
                target_display = core_display
                break
        
        if target_display:
            self.selected_core.set(target_display)
        else:
            custom_name = f"未知核心 ({inferred_platform}) | {loaded_core_path}"
            # 如果是未知的核心路径，添加到列表的开头
            if custom_name not in self.core_list:
                self.core_list.insert(0, custom_name)
                self.core_combo.config(values=self.core_list)
            self.selected_core.set(custom_name)

        # 设置缩略图模式
        if 'right_thumbnail_mode' in settings:
           self.playlist_settings['right_thumbnail_mode'].set(settings['right_thumbnail_mode'])
           self.settings_vars_str['right_thumbnail_mode'].set(MODE_TO_CN.get(settings['right_thumbnail_mode']))
        if 'left_thumbnail_mode' in settings:
           self.playlist_settings['left_thumbnail_mode'].set(settings['left_thumbnail_mode'])
           self.settings_vars_str['left_thumbnail_mode'].set(MODE_TO_CN.get(settings['left_thumbnail_mode']))


        self.update_lists()
        if self.rom_list:
             self.after(1, lambda: self.sync_selection_and_refresh(0))
        else:
             self.after(1, self.update_ui_only)
        
        self.preview.delete(1.0, 'end')
        self.preview.insert('end', f"已加载 {len(self.rom_list)} 个项目")

    # --- Combobox 选中列表项时触发，自动加载 LPL 文件 ---
    def load_playlist_on_select(self, event):
        """从下拉列表中选择 LPL 文件时自动加载。"""
        selected_name = self.playlist_name.get()
        ra_dir_val = self.retroarch_dir.get().strip()
        
        if ra_dir_val and selected_name and Path(ra_dir_val).is_dir():
            ra_dir_path = Path(ra_dir_val)
            lpl_path = ra_dir_path / "playlists" / f"{selected_name}.lpl"
            
            if lpl_path.is_file():
                self._load_lpl_from_path(str(lpl_path))

    # ------------------ 核心功能函数 (CRUD & Save/Load) ------------------

    def select_retroarch_dir(self):
        """选择 RetroArch 根目录。"""
        try:
            dir_path = filedialog.askdirectory(title="选择 RetroArch 根目录")
            if dir_path:
                self.retroarch_dir.set(dir_path)
                
                # 自动扫描并加载列表名
                self.scan_existing_playlists(dir_path) 
                
                self.after(10, self.update_ui_only)
        except Exception as e:
            messagebox.showerror("错误", f"选择 RetroArch 目录时发生错误: {e}")

    def do_save(self):
        """保存播放列表为 LPL 文件。"""
        if not self.rom_list:
            messagebox.showwarning("警告", "列表为空，无需保存。")
            return
            
        lpl_name = self.playlist_name.get().strip()
        if not lpl_name:
             messagebox.showwarning("警告", "请设置一个播放列表名称！")
             return

        ra_dir_val = self.retroarch_dir.get().strip()
        
        target_path = None
        should_save = False

        if ra_dir_val and Path(ra_dir_val).is_dir():
            # 保存到 RetroArch/playlists 目录
            playlists_dir = Path(ra_dir_val) / "playlists"
            playlists_dir.mkdir(parents=True, exist_ok=True) # 确保 playlists 目录存在
            target_path = playlists_dir / f"{lpl_name}.lpl"
            
            # 检查覆盖/新建
            is_existing_file = target_path.is_file()
            
            if is_existing_file:
                # 文件存在：提示覆盖
                should_save = messagebox.askyesno(
                    "确认覆盖",
                    f"播放列表 '{lpl_name}.lpl' 已存在于 RetroArch 目录中。\n"
                    f"是否覆盖此文件？\n\n路径：{target_path}"
                )
            else:
                 # 文件不存在：提示新建
                should_save = messagebox.askyesno(
                    "确认新建",
                    f"播放列表 '{lpl_name}.lpl' 文件是新的。\n"
                    f"是否在以下路径新建文件？\n\n路径：{target_path}"
                )
        else:
            # 如果 RetroArch 目录未设置或无效，则弹出文件对话框
            try:
                initial_file = f"{lpl_name}.lpl"
                save_path_str = filedialog.asksaveasfilename(
                    defaultextension=".lpl",
                    initialfile=initial_file,
                    filetypes=[("Playlist", "*.lpl")]
                )
                if not save_path_str: return
                target_path = Path(save_path_str)
                should_save = True
            except Exception as e:
                messagebox.showerror("错误", f"选择保存路径时发生错误: {e}")
                return

        # 执行保存
        if should_save and target_path:
            self.current_lpl_name = lpl_name
            
            platform = self.selected_platform.get()
            core_display_text = self.selected_core.get()
            friendly_name = core_display_text.split(' (')[0]
            
            core_path = ""
            # 如果核心是未知核心，则 core_path 已经是它的路径
            if ' | ' in core_display_text:
                core_path = core_display_text.split(' | ')[1].strip()
            else:
                for path, name in PLATFORM_MAPPING[platform]["name_map"].items():
                    if name == friendly_name:
                        core_path = path
                        break

            if not core_path:
                 core_path = PLATFORM_MAPPING[platform]["default_core"] 
                 
            settings = {k: v.get() for k, v in self.playlist_settings.items()} 
            count = generate_playlist(self.rom_list, str(target_path), core_path, settings, platform) 
            
            if ra_dir_val and Path(ra_dir_val).is_dir():
                 self.scan_existing_playlists(ra_dir_val) # 重新扫描，更新列表名下拉框
                 
            messagebox.showinfo("成功", f"保存完成！\n保存至: {os.path.basename(target_path)}\n共 {count} 个游戏")
            self.after(10, self.update_lists) 


    def load_lpl(self):
        """通过文件选择对话框加载 LPL 文件。"""
        try:
            path = filedialog.askopenfilename(filetypes=[("Playlist", "*.lpl")])
            if path:
                self._load_lpl_from_path(path)
        except Exception as e:
            messagebox.showerror("错误", f"选择 LPL 文件时发生错误: {e}")
            return
            
    def global_edit_rom_path(self):
        """全局修改列表中所有 ROM 路径的前缀。"""
        if not self.rom_list:
            messagebox.showwarning("警告", "列表为空，无需修改路径。")
            return
            
        platform = self.selected_platform.get()
        # 判断是否为需要手动输入的无盘符系统（非 Windows）
        is_manual_mode = platform != "Windows" 
            
        # --- 步骤 1: 获取旧的前缀 ---
        first_path = self.rom_list[0]['path']
        
        # 尝试建议一个旧路径
        try:
            path_suggestion = Path(first_path).parent.parent
            initial_old_value = str(path_suggestion).replace('\\', '/')
        except Exception:
            initial_old_value = ""

        old_prefix_prompt = (
            "请输入您想在所有 ROM 路径中替换掉的**旧路径前缀**。\n"
            "例如: 如果路径是 '/old/games/SNES/Mario.sfc'，您可以输入 '/old/games/'\n"
            "（请注意大小写和斜杠方向！）\n\n"
            f"第一个路径示例: {first_path}"
        )
        old_prefix = simpledialog.askstring("全局路径修改 - 步骤 1/2", old_prefix_prompt, initialvalue=initial_old_value)
        
        if not old_prefix: return
        # 统一路径分隔符
        old_prefix = os.path.normpath(old_prefix).replace('\\', '/')
        if old_prefix and not old_prefix.endswith('/'):
            old_prefix += '/'

        # --- 步骤 2: 获取新的根目录 (根据平台选择方式) ---
        new_base_dir = None
        
        if is_manual_mode:
            # 无盘符系统 (Switch/Android/Linux) - 手动输入
            manual_prompt = (
                "【Switch、安卓等无盘符路径系统，路径指定手动输入】\n"
                "请输入完整的**新根目录路径**。\n"
                "例如: '/switch/roms/new_folder/' 或 '/storage/emulated/0/roms/'\n"
                "（请确保路径以 '/' 结尾！）"
            )
            new_base_dir = simpledialog.askstring("全局路径修改 - 步骤 2/2 (手动输入)", manual_prompt, initialvalue="/new/roms/")
            if not new_base_dir: return
        else:
            # Windows - 文件对话框选择
            new_base_dir = filedialog.askdirectory(title="全局路径修改 - 步骤 2/2: 选择新的根目录")
            if not new_base_dir: return

        # 统一路径分隔符
        new_base_dir = os.path.normpath(new_base_dir).replace('\\', '/')
        if new_base_dir and not new_base_dir.endswith('/'): new_base_dir += '/'

        # --- 步骤 3: 执行替换 ---
        modified_count = 0
        
        for r in self.rom_list:
            original_path = r['path']
            
            if original_path.startswith(old_prefix):
                # 替换前缀
                relative_path = original_path[len(old_prefix):]
                new_path = new_base_dir + relative_path
                r['path'] = new_path
                modified_count += 1
            else:
                # 无法匹配前缀，跳过
                pass
                
        self.update_lists()
        
        if modified_count > 0:
            messagebox.showinfo("成功", f"全局路径修改完成！\n成功修改了 {modified_count} 个 ROM 的路径。")
        else:
            messagebox.showwarning("警告", "没有 ROM 的路径以您输入的旧前缀开始，请检查路径和斜杠。未进行任何修改。")


    def add_single_rom(self):
        """添加单个 ROM 文件。"""
        try:
            path = filedialog.askopenfilename(
                filetypes=[("ROM Files", "*.nes *.gb *.gba *.sfc *.bin *.cue *.iso *.chd *.pbp *.exe *.md *.z64 *.zip *.7z *.cso *.m3u")]
            )
        except Exception as e:
            messagebox.showerror("错误", f"选择 ROM 文件时发生错误: {e}")
            return
            
        if path:
            platform = self.selected_platform.get()
            suggested_core_path = suggest_core_by_extension(path, platform)
            suggested_core_name = get_core_name(suggested_core_path, platform)
            
            match = [c for c in self.core_list if c.startswith(suggested_core_name)]
            if match:
                self.selected_core.set(match[0])
            
            norm_path = os.path.normpath(path).replace('\\', '/')
            
            self.rom_list.append({'path': norm_path,
                            'label': Path(path).stem})
            self.update_lists()
            last_idx = len(self.rom_list) - 1
            self.sync_selection_and_refresh(last_idx)

    def add_folder_roms(self):
        """添加整个文件夹内的 ROM 文件。"""
        try:
            folder = filedialog.askdirectory()
        except Exception as e:
            messagebox.showerror("错误", f"选择文件夹时发生错误: {e}")
            return
            
        if folder:
            files = [os.path.join(r, f) for r, _, fs in os.walk(folder) for f in fs]
            candidates = filter_rom_files(files)
            if candidates and messagebox.askyesno("确认", f"发现 {len(candidates)} 个 ROM，全部添加？"):
                self.rom_list.extend(candidates)
                self.update_lists()
                if self.rom_list:
                    last_idx = len(self.rom_list)-1
                    self.sync_selection_and_refresh(last_idx)

    def clear_list(self):
        """清空 ROM 列表。"""
        if messagebox.askyesno("确认", "清空所有 ROM？"):
            self.rom_list.clear()
            self.update_lists()

    def edit_rom_label(self):
        """编辑选中 ROM 的显示名称。"""
        sel = self.rom_detail.curselection()
        if sel:
            idx = sel[0]
            new = simpledialog.askstring("编辑名称", "新名称:", initialvalue=self.rom_list[idx]['label'])
            if new and new.strip():
                self.rom_list[idx]['label'] = new.strip()
                self.update_lists()
                self.sync_selection_and_refresh(idx)
                
    def delete_rom(self):
        """删除选中 ROM。"""
        sel = self.rom_detail.curselection()
        if sel and messagebox.askyesno("确认", "确定删除该 ROM？"):
            idx_to_delete = sel[0]
            del self.rom_list[idx_to_delete]
            self.update_lists()
            new_idx = min(idx_to_delete, len(self.rom_list) - 1)
            if new_idx >= 0:
                self.sync_selection_and_refresh(new_idx)

    # --- 缩略图双击替换函数 ---
    def replace_thumbnail(self, side):
        """双击预览框时，替换/新增缩略图。"""
        sel = self.rom_detail.curselection()
        if not sel:
            messagebox.showwarning("警告", "请先选中一个 ROM！")
            return
        
        idx = sel[0]
        
        # 使用 ROM 文件路径的名称（不含扩展名）作为缩略图文件名。
        try:
            rom_file_stem = Path(self.rom_list[idx]['path']).stem 
        except Exception:
            messagebox.showwarning("警告", "无法获取 ROM 文件名。请确保路径有效。")
            return
            
        ra_dir = self.retroarch_dir.get().strip()
        lpl_name = self.playlist_name.get().strip()

        if not ra_dir:
            messagebox.showwarning("警告", "请先选择 RetroArch 目录！")
            return
        if not lpl_name:
            messagebox.showwarning("警告", "请先设置播放列表名称！")
            return

        # 确定要替换的模式和文件夹
        if side == 'left':
            mode_val = self.playlist_settings['left_thumbnail_mode'].get()
        elif side == 'right':
            mode_val = self.playlist_settings['right_thumbnail_mode'].get()
        else:
            return

        mode_folder_map = {1: "Named_Snaps", 2: "Named_Titles", 3: "Named_Boxarts"}
        mode_folder = mode_folder_map.get(mode_val)
        
        if mode_val == 0:
            messagebox.showwarning("警告", "当前缩略图模式为 '禁用 (0)'，请选择 '截图 (1)'、'标题 (2)' 或 '封面 (3)' 后再尝试替换。")
            return
        if mode_val in [4, 5] or not mode_folder:
            messagebox.showwarning("警告", "当前缩略图模式为优先模式 (4/5)，请切换到具体模式 (1/2/3) 后再尝试替换。")
            return

        # 1. 提示和选择新图片
        perf_hint = (
            "RetroArch 图片加载顺序是**优先 PNG** (.png)。\n\n"
            "您选择的图片建议使用长宽**小于 512px**、文件**小于 3MB** 的图片。\n"
            "过大图片，可能**严重影响** RetroArch 的列表性能！"
        )
        messagebox.showinfo("缩略图替换提示", perf_hint)

        try:
            new_img_path = filedialog.askopenfilename(
                title="选择新缩略图 (PNG/JPG)",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
            )
            if not new_img_path: return
            new_img_path = Path(new_img_path)
            
            # --- 确定目标目录和文件名 ---
            target_dir = Path(ra_dir) / "thumbnails" / lpl_name / mode_folder
            target_dir.mkdir(parents=True, exist_ok=True) # 确保目录存在
            
            original_suffix = new_img_path.suffix.lower()
            
            # 确定目标扩展名：如果原始文件是JPG/JPEG，保存为.jpg；否则，保存为.png（优先PNG）
            if original_suffix in ['.jpg', '.jpeg']:
                target_ext = '.jpg'
                other_ext = '.png'
            else:
                target_ext = '.png'
                other_ext = '.jpg'

            target_file = target_dir / f"{rom_file_stem}{target_ext}" 
            other_file = target_dir / f"{rom_file_stem}{other_ext}" 

            # 2. 删除不同格式的原文件
            if other_file.exists():
                try:
                    os.remove(other_file)
                except Exception as e:
                    print(f"Warning: Could not remove old thumbnail file {other_file.name}: {e}") 
            
            # 3. 保存新文件
            img = Image.open(new_img_path)
            
            if target_ext == '.png':
                img.save(target_file, format='PNG')
            else: # .jpg
                # 确保转换为 RGB 格式
                img.convert('RGB').save(target_file, format='JPEG', quality=90)
            
            messagebox.showinfo("成功", f"缩略图已成功替换！\n保存至：{target_file.name}\n目录：{target_dir.parent.name}/{target_dir.name}")
            
            # 4. 强制刷新预览图
            if side == 'left':
                self.update_left_thumbnail()
            elif side == 'right':
                self.update_right_thumbnail()

        except Exception as e:
            messagebox.showerror("错误", f"替换缩略图时发生错误: {e}")

    # --- 帮助函数：弹出软件说明 ---
    def show_help(self):
        """显示软件帮助信息。"""
        help_text = (
            "RetroArch 播放列表生成器 V0.40 使用说明：\n\n"
            "1. 选择 RetroArch 目录：设置 RetroArch 根路径，并自动加载该目录下的现有列表名。\n"
            "2. 添加 ROM：单个文件或整个文件夹，支持常见 ROM 格式。\n"
            "3. 编辑名称：修改列表显示名称。\n"
            "4. 全局修改路径：统一替换所有 ROM 路径的前缀，用于迁移 ROM 目录。\n"
            "   - **Windows** 平台：使用文件夹选择对话框。\n"
            "   - **Switch/安卓** 等平台：需要手动输入目标路径。\n"
            "5. 缩略图模式：选择左侧/右侧缩略图显示偏好（封面、标题等）。\n"
            "6. 核心选择：根据平台和 ROM 类型自动建议核心。\n"
            "7. 保存/加载 LPL：生成或导入播放列表文件，保存时会检查覆盖/新建。\n\n"
            "🌟 **新功能：双击添加/替换缩略图**\n"
            "   - 在左侧或右侧预览框中，如果显示“双击此处添加”，双击即可选择图片进行替换。\n"
            "   - 替换图片会被自动命名为 ROM 文件名，并保存到当前列表和模式对应的 RetroArch 目录中。\n"
            "   - **性能提示：** 建议图片尺寸小于 512px，文件大小小于 3MB，以避免影响 RetroArch 列表加载速度。\n\n"
            "原作者：@爱折腾的老家伙"
        )
        messagebox.showinfo("帮助与说明", help_text)

    # --- 复制 ROM 名称到剪贴板函数 ---
    def copy_rom_name(self):
        """复制选中 ROM 名称到剪贴板。"""
        sel = self.rom_detail.curselection()
        if not sel:
            messagebox.showwarning("警告", "请先选中一个 ROM！")
            return
        idx = sel[0]
        if idx >= len(self.rom_list):
            return
        name = self.rom_list[idx]['label']
        self.clipboard_clear()
        self.clipboard_append(name)
        messagebox.showinfo("成功", f"已复制 ROM 名称到剪贴板：\n{name}")

    def on_closing(self):
        """窗口关闭时销毁程序。"""
        self.destroy()

if __name__ == "__main__":
    # 检查 PIL 库是否安装
    try:
        from PIL import Image, ImageTk
    except ImportError:
        try:
            import subprocess
            subprocess.check_call(['pip', 'install', 'Pillow'])
            from PIL import Image, ImageTk
        except Exception:
            # 使用 messagebox 而不是 print，以确保即使缺少依赖也能提示用户
            import tkinter as tk
            root = tk.Tk()
            root.withdraw() # 隐藏主窗口
            messagebox.showerror("依赖错误", "缺少 PIL/Pillow 库。\n请在命令行运行：pip install pillow")
            root.destroy()
            exit()
        
    try:
        app = PlaylistGenerator()
        app.mainloop()
    except Exception as e:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("致命错误", f"程序运行发生致命错误: {e}")
        root.destroy()