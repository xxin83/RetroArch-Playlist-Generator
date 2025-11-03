"""
RetroArch 播放列表生成器 V0.51

==================================================
开源声明：
本软件为开源项目，旨在帮助 RetroArch 用户生成和管理播放列表。
您可以自由修改、复制和分发本软件的源代码。

- 作者不对软件的任何使用后果负责，包括但不限于数据丢失或硬件损坏。
- 如果您对软件进行了改进，欢迎分享回原作者或社区，但非强制要求。

原作者：@爱折腾的老家伙
==================================================
"""

import customtkinter as ctk 
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
from collections import OrderedDict
import json
import os
import threading
from PIL import Image, ImageTk 


ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue") 


# --- 常量和映射表 ---

MODE_TO_CN = {
    0: "0 | 禁用", 1: "1 | 截图 (Snap)", 2: "2 | 标题 (Title)",
    3: "3 | 封面 (Boxart)", 4: "4 | 优先封面 (Prefer Boxart)", 5: "5 | 优先标题 (Prefer Title)"
}
CN_TO_MODE = {v: k for k, v in MODE_TO_CN.items()}
THUMBNAIL_MODES_DISPLAY = list(MODE_TO_CN.values())

# 启动时的多行默认状态提示
INITIAL_STATUS_TEXT = (
    "查找结果: 等待选中 ROM\n"
    "当前模式: 未选择\n"
    "查找目录: 等待提供 LPL 列表名称\n"
    "查找文件名: 等待选择 ROM 文件\n"
    "--- 三种模式拥有状态 ---\n"
    " - 截图: 等待选择\n"
    " - 标题: 等待选择\n"
    " - 封面: 等待选择"
)

# 核心路径和名称的平台映射
WINDOWS_MAPPING = {
    "ext_map": { 
        '.nes': "cores\\nestopia_libretro.dll", '.gb': "cores\\gambatte_libretro.dll",
        '.gbc': "cores\\gambatte_libretro.dll", '.gba': "cores\\mgba_libretro.dll",
        '.sfc': "cores\\snes9x2010_libretro.dll", '.smc': "cores\\snes9x2010_libretro.dll",
        '.md': "cores\\genesis_plus_gx_libretro.dll", '.gg': "cores\\genesis_plus_gx_libretro.dll",
        '.z64': "cores\\mupen64plus_next_libretro.dll", '.n64': "cores\\mupen64plus_next_libretro.dll",
        '.bin': "cores\\pcsx_rearmed_libretro.dll", '.cue': "cores\\pcsx_rearmed_libretro.dll",
        '.iso': "cores\\pcsx_rearmed_libretro.dll", '.chd': "cores\\flycast_libretro.dll",
        '.pbp': "cores\\ppsspp_libretro.dll", '.elf': "cores\\pcsx2_libretro.dll",
        '.cso': "cores\\ppsspp_libretro.dll", '.exe': "cores\\dosbox_pure_libretro.dll",
        '.zip': "cores\\fbneo_libretro.dll", '.7z': "cores\\fbneo_libretro.dll",
        '.m3u': "cores\\mame_libretro.dll",
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
SWITCH_MAPPING = {
    "ext_map": {
        '.nes': "/retroarch/cores/nestopia_libretro_libnx.nro", '.gb': "/retroarch/cores/gambatte_libretro_libnx.nro",
        '.gbc': "/retroarch/cores/gambatte_libretro_libnx.nro", '.gba': "/retroarch/cores/mgba_libretro_libnx.nro",
        '.sfc': "/retroarch/cores/snes9x2010_libretro_libnx.nro", '.smc': "/retroarch/cores/snes9x2010_libretro_libnx.nro",
        '.md': "/retroarch/cores/genesis_plus_gx_libretro_libnx.nro", '.gg': "/retroarch/cores/genesis_plus_gx_libretro_libnx.nro",
        '.z64': "/retroarch/cores/mupen64plus_next_libretro_libnx.nro", '.n64': "/retroarch/cores/mupen64plus_next_libretro_libnx.nro",
        '.bin': "/retroarch/cores/pcsx_rearmed_libretro_libnx.nro", '.cue': "/retroarch/cores/pcsx_rearmed_libretro_libnx.nro",
        '.iso': "/retroarch/cores/pcsx_rearmed_libretro_libnx.nro", '.chd': "/retroarch/cores/flycast_libretro_libnx.nro",
        '.pbp': "/retroarch/cores/ppsspp_libretro_libnx.nro", '.elf': "/retroarch/cores/pcsx2_libretro_libnx.nro",
        '.cso': "/retroarch/cores/ppsspp_libretro_libnx.nro", '.exe': "/retroarch/cores/dosbox_pure_libretro_libnx.nro",
        '.zip': "/retroarch/cores/fbneo_libretro_libnx.nro", '.7z': "/retroarch/cores/fbneo_libretro_libnx.nro",
        '.m3u': "/retroarch/cores/mame_libretro_libnx.nro",
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


# --- 核心辅助函数 ---
def get_all_cores_list():
    all_cores = {}
    for platform in PLATFORM_MAPPING:
        name_map = PLATFORM_MAPPING[platform]["name_map"]
        for core_path, core_name in name_map.items():
            if core_name not in all_cores:
                 all_cores[core_name] = {}
            all_cores[core_name][platform] = core_path

    display_list = []
    sorted_all_cores = OrderedDict(sorted(all_cores.items(), key=lambda item: item[0]))
    
    for core_name, paths in sorted_all_cores.items():
        platforms = ", ".join(sorted(paths.keys()))
        display_list.append(f"{core_name} ({platforms})")
        
    return display_list

def suggest_core_by_extension(file_path, platform):
    ext = Path(file_path).suffix.lower()
    platform_data = PLATFORM_MAPPING.get(platform)
    if not platform_data: return "" 
    mapping = platform_data['ext_map']
    default_core = platform_data['default_core']
    return mapping.get(ext, default_core)

def get_core_name(core_path, platform):
    platform_data = PLATFORM_MAPPING.get(platform)
    if not platform_data: return "Unknown Core"
    name_map = platform_data['name_map']
    return name_map.get(core_path, "Unknown Core")

def filter_rom_files(files, extensions=None):
    if extensions is None:
        extensions = set()
        for data in PLATFORM_MAPPING.values():
            extensions.update(data['ext_map'].keys())

    roms = []
    for fp in files:
        if any(fp.lower().endswith(ext) for ext in extensions):
            rom_path = os.path.normpath(fp).replace('\\', '/')
            roms.append({
                'path': rom_path,
                'label': Path(fp).stem,
            })
    return roms

def load_playlist(playlist_path):
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
    core_name = get_core_name(core_path, platform)

    playlist = {
        "version": "1.5",
        "default_core_path": core_path,
        "default_core_name": core_name,
        "label_display_mode": settings.get('label_display_mode', 0),
        "right_thumbnail_mode": settings.get('right_thumbnail_mode', 4),
        "left_thumbnail_mode": settings.get('left_thumbnail_mode', 2),
        "thumbnail_match_mode": settings.get('thumbnail_match_mode', 0),
        "sort_mode": 2, # 2 = Sort by label
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


# --- CTk 主应用类 ---

class PlaylistGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RetroArch 播放列表生成器 V0.51") 
        self.geometry("1450x850") 

        # 配置网格布局 
        self.grid_rowconfigure(1, weight=1)    
        self.grid_rowconfigure(2, weight=0)    
        
        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_columnconfigure(2, weight=1) 
        self.grid_columnconfigure(3, weight=0) 
        
        # 实例变量 
        self.rom_list = []
        self.retroarch_dir = tk.StringVar()
        self.current_lpl_name = "" 
        self.last_selection_id = 0 
        self.core_list = get_all_cores_list()
        self.selected_platform = tk.StringVar(value="Windows") 
        self.selected_core = tk.StringVar(value=self.core_list[0] if self.core_list else "") 
        self.playlist_name = tk.StringVar(value="MyPlaylist") 
        self.lpl_list = []
        self.selected_lpl = tk.StringVar(value="选择已有播放列表 (.lpl)") 
        
        # 缩略图模式设置变量
        self.playlist_settings = {
            'right_thumbnail_mode': tk.IntVar(value=4),
            'left_thumbnail_mode': tk.IntVar(value=2),
        }
        self.settings_vars_str = {
            'right_thumbnail_mode': tk.StringVar(value=MODE_TO_CN[4]),
            'left_thumbnail_mode': tk.StringVar(value=MODE_TO_CN[2]),
        }
        
        # 路径状态变量 (使用初始多行提示)
        self.left_path_status = tk.StringVar(value=INITIAL_STATUS_TEXT)
        self.right_path_status = tk.StringVar(value=INITIAL_STATUS_TEXT)
        
        # 原始 PIL 图片引用
        self.original_left_img = None
        self.original_right_img = None
        
        # UI 组件引用
        self.rom_name_list = None
        self.rom_detail_list = None
        self.preview_textbox = None
        self.lpl_combo = None 

        self.build_ui()
        self.on_platform_change() 
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    # --- UI 搭建部分 ---
    def build_ui(self):
        
        # 0. 顶部工具栏 
        top_frame = ctk.CTkFrame(self) 
        top_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=10, pady=(10, 5))

        ctk.CTkButton(top_frame, text="选择 RA 目录", command=self.select_retroarch_dir).pack(side='left', padx=5, pady=5)
        ctk.CTkLabel(top_frame, textvariable=self.retroarch_dir, text_color='blue').pack(side='left', padx=(5, 15), pady=5)
        
        self.lpl_combo = ctk.CTkComboBox(
            top_frame,
            variable=self.selected_lpl,
            values=["选择已有播放列表 (.lpl)"],
            command=self.on_lpl_combo_select,
            width=250,
            state='readonly'
        )
        self.lpl_combo.pack(side='left', padx=5, pady=5) 
        self.lpl_combo.set("选择已有播放列表 (.lpl)")
        
        ctk.CTkButton(top_frame, text="加载 .lpl", command=self.load_lpl, width=100).pack(side='left', padx=(15, 10), pady=5)
        ctk.CTkButton(top_frame, text="保存 .lpl", command=self.do_save, width=100).pack(side='left', padx=10, pady=5)
        ctk.CTkButton(top_frame, text="添加 ROM", command=self.add_single_rom, width=100).pack(side='left', padx=10, pady=5)
        ctk.CTkButton(top_frame, text="添加文件夹", command=self.add_folder_roms, width=100).pack(side='left', padx=10, pady=5)
        ctk.CTkButton(top_frame, text="全局路径修改", command=self.global_edit_rom_path, width=120).pack(side='left', padx=(20, 5), pady=5)


        # 1. 中间主区域 
        
        # 1.1. 左侧主框架 
        left_main_frame = ctk.CTkFrame(self)
        left_main_frame.grid(row=1, column=0, sticky="nswe", padx=(10, 5), pady=5)
        left_main_frame.grid_columnconfigure(0, weight=1)
        
        left_main_frame.grid_rowconfigure(0, weight=0) 
        left_main_frame.grid_rowconfigure(1, weight=1) 
        left_main_frame.grid_rowconfigure(2, weight=0) 
        
        # 1.1.A. 左侧顶部 - 配置 
        left_config_frame = ctk.CTkFrame(left_main_frame)
        left_config_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 5)) 
        left_config_frame.grid_columnconfigure(0, weight=1)
        
        for i in range(6): 
             left_config_frame.grid_rowconfigure(i, weight=0)

        ctk.CTkLabel(left_config_frame, text="列表名:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=(5, 2), pady=(5, 0))
        self.playlist_name_entry = ctk.CTkEntry(left_config_frame, textvariable=self.playlist_name, width=280)
        self.playlist_name_entry.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        ctk.CTkLabel(left_config_frame, text="目标平台:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", padx=(5, 2), pady=(5, 0))
        self.platform_combo = ctk.CTkComboBox(left_config_frame, variable=self.selected_platform, values=list(PLATFORM_MAPPING.keys()), command=self.on_platform_change, width=280)
        self.platform_combo.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        ctk.CTkLabel(left_config_frame, text="核心代码:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=4, column=0, sticky="w", padx=(5, 2), pady=(5, 0))
        self.core_combo = ctk.CTkComboBox(left_config_frame, variable=self.selected_core, values=self.core_list, command=self.on_core_change, width=280)
        self.core_combo.grid(row=5, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        
        # 1.1.B. 左侧中间 - 缩略图预览 
        left_thumb_frame = ctk.CTkFrame(left_main_frame)
        left_thumb_frame.grid(row=1, column=0, sticky="nswe", padx=5, pady=(5, 5)) 
        left_thumb_frame.grid_columnconfigure(0, weight=1)
        left_thumb_frame.grid_rowconfigure(1, weight=1) 

        ctk.CTkLabel(left_thumb_frame, text="左侧图预览 (Titles/Snaps)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=(5, 0), sticky='n')
        
        self.thumb_label_left = ctk.CTkLabel(left_thumb_frame, text="左侧图", fg_color="#333", corner_radius=6)
        self.thumb_label_left.grid(row=1, column=0, padx=5, pady=5, sticky='n') 
        self.thumb_label_left.bind('<Double-1>', lambda e: self.replace_thumbnail('left'))
        
        
        # 1.1.C. 左侧底部 - 缩略图模式设置和路径状态 
        left_bottom_frame = ctk.CTkFrame(left_main_frame)
        left_bottom_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(5, 5)) 
        left_bottom_frame.grid_columnconfigure(0, weight=1)
        
        left_bottom_frame.grid_rowconfigure(0, weight=0) 
        left_bottom_frame.grid_rowconfigure(1, weight=0) 
        left_bottom_frame.grid_rowconfigure(2, weight=0) 
        
        ctk.CTkLabel(left_bottom_frame, text="左侧图模式:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        left_mode_combo = ctk.CTkComboBox(left_bottom_frame, variable=self.settings_vars_str['left_thumbnail_mode'], values=THUMBNAIL_MODES_DISPLAY, command=lambda e: self.update_thumbnail_mode('left_thumbnail_mode'), width=280)
        left_mode_combo.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        
        self.left_path_status_label = ctk.CTkLabel(left_bottom_frame, textvariable=self.left_path_status, wraplength=350, justify='left', text_color='gray', font=ctk.CTkFont(size=10))
        self.left_path_status_label.grid(row=2, column=0, padx=5, pady=(5, 5), sticky='sw') 


        # 1.2. ROM 名称列表 
        name_list_frame = ctk.CTkFrame(self)
        name_list_frame.grid(row=1, column=1, sticky="nswe", padx=(5, 5), pady=5)
        name_list_frame.grid_columnconfigure(0, weight=1)
        name_list_frame.grid_rowconfigure(0, weight=1)
        
        self.rom_name_list = tk.Listbox(name_list_frame, font=("Consolas", 12), width=20, selectmode=tk.SINGLE, exportselection=False, highlightthickness=0)
        self.rom_name_list.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.rom_name_list.bind('<Button-1>', lambda e: "break") 
        self.rom_name_list.bind('<<ListboxSelect>>', lambda e: self.rom_name_list.selection_clear(0, 'end')) 
        self.rom_name_list.bind('<Double-1>', self.edit_rom_label_on_double_click) 


        # 1.3. ROM 路径/核心列表 
        detail_list_frame = ctk.CTkFrame(self)
        detail_list_frame.grid(row=1, column=2, sticky="nswe", padx=(0, 5), pady=5)
        detail_list_frame.grid_columnconfigure(0, weight=1)
        detail_list_frame.grid_rowconfigure(0, weight=1)
        
        self.rom_detail_list = tk.Listbox(detail_list_frame, font=("Consolas", 12), selectmode=tk.SINGLE, exportselection=False, highlightthickness=0)
        self.rom_detail_list.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.rom_detail_list.bind('<Double-1>', self.edit_rom_path_on_double_click)
        self.rom_detail_list.bind('<<ListboxSelect>>', self.sync_selection_and_refresh)
        
        # 共享滚动条
        sb_center = ctk.CTkScrollbar(detail_list_frame, command=self.on_scroll_yview)
        sb_center.grid(row=0, column=1, sticky="ns")
        self.rom_detail_list.config(yscrollcommand=sb_center.set)
        self.rom_name_list.config(yscrollcommand=sb_center.set)
        
        
        # 1.4. 右侧主框架 
        right_main_frame = ctk.CTkFrame(self)
        right_main_frame.grid(row=1, column=3, sticky="nswe", padx=(5, 10), pady=5)
        right_main_frame.grid_columnconfigure(0, weight=1)
        
        right_main_frame.grid_rowconfigure(0, weight=0) 
        right_main_frame.grid_rowconfigure(1, weight=1) 
        right_main_frame.grid_rowconfigure(2, weight=0) 

        # 1.4.A. 右侧顶部 - ROM 详情 
        right_detail_frame = ctk.CTkFrame(right_main_frame)
        right_detail_frame.grid(row=0, column=0, sticky="nswe", padx=5, pady=(5, 5)) 
        right_detail_frame.grid_columnconfigure(0, weight=1)
        right_detail_frame.grid_rowconfigure(0, weight=0) 
        right_detail_frame.grid_rowconfigure(1, weight=1) 

        ctk.CTkLabel(right_detail_frame, text="ROM 详情 / 核心配置", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=(5, 2), sticky='n')
        self.preview_textbox = ctk.CTkTextbox(right_detail_frame, font=("Consolas", 10), corner_radius=6) 
        self.preview_textbox.grid(row=1, column=0, sticky='nswe', padx=5, pady=5)


        # 1.4.B. 右侧中间 - 缩略图预览 
        right_thumb_frame = ctk.CTkFrame(right_main_frame)
        right_thumb_frame.grid(row=1, column=0, sticky="nswe", padx=5, pady=(5, 5)) 
        right_thumb_frame.grid_columnconfigure(0, weight=1) 
        right_thumb_frame.grid_rowconfigure(1, weight=1) 

        ctk.CTkLabel(right_thumb_frame, text="右侧图预览 (Boxarts)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=(5, 0), sticky='n')
        
        self.thumb_label_right = ctk.CTkLabel(right_thumb_frame, text="右侧图", fg_color="#333", corner_radius=6)
        self.thumb_label_right.grid(row=1, column=0, padx=5, pady=5, sticky='n') 
        self.thumb_label_right.bind('<Double-1>', lambda e: self.replace_thumbnail('right'))

        
        # 1.4.C. 右侧底部 - 缩略图模式设置和路径状态 
        right_bottom_frame = ctk.CTkFrame(right_main_frame)
        right_bottom_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(5, 5)) 
        right_bottom_frame.grid_columnconfigure(0, weight=1)
        
        right_bottom_frame.grid_rowconfigure(0, weight=0) 
        right_bottom_frame.grid_rowconfigure(1, weight=0) 
        right_bottom_frame.grid_rowconfigure(2, weight=0) 
        
        ctk.CTkLabel(right_bottom_frame, text="右侧图模式:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        right_mode_combo = ctk.CTkComboBox(right_bottom_frame, variable=self.settings_vars_str['right_thumbnail_mode'], values=THUMBNAIL_MODES_DISPLAY, command=lambda e: self.update_thumbnail_mode('right_thumbnail_mode'), width=280)
        right_mode_combo.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        self.right_path_status_label = ctk.CTkLabel(right_bottom_frame, textvariable=self.right_path_status, wraplength=350, justify='left', text_color='gray', font=ctk.CTkFont(size=10))
        self.right_path_status_label.grid(row=2, column=0, padx=5, pady=(5, 5), sticky='sw') 


        # 2. 底部功能区域 
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkButton(bottom_frame, text="帮助", command=self.show_help, width=100).pack(side='right', padx=5, pady=5)
        ctk.CTkButton(bottom_frame, text="清空列表", command=self.clear_list, width=100).pack(side='right', padx=5, pady=5)
        ctk.CTkButton(bottom_frame, text="编辑名称", command=self.edit_rom_label, width=100).pack(side='right', padx=5, pady=5)
        ctk.CTkButton(bottom_frame, text="删除选中", command=self.delete_rom, width=100).pack(side='right', padx=5, pady=5)


    # --- 核心 UI 刷新方法 ---
    def on_scroll_yview(self, *args):
        self.rom_detail_list.yview(*args)
        self.rom_name_list.yview(*args)
        
    def sync_selection_and_refresh(self, idx_or_event=None):
        idx = None
        if isinstance(idx_or_event, int):
            idx = idx_or_event
        elif idx_or_event is not None:
            try:
                sel = self.rom_detail_list.curselection() 
                if not sel: return
                idx = sel[0]
            except Exception:
                return

        if idx is None or idx < 0 or idx >= len(self.rom_list):
            self.update_ui_only()
            return
            
        self.rom_detail_list.selection_clear(0, 'end')
        self.rom_detail_list.selection_set(idx)
        self.rom_detail_list.activate(idx)
        self.rom_detail_list.see(idx)

        self.rom_name_list.selection_clear(0, 'end')
        self.rom_name_list.selection_set(idx)
        self.rom_name_list.activate(idx)
        self.rom_name_list.see(idx)

        self.after(10, self.update_ui_only)

    def update_lists(self):
        current_selection = self.rom_detail_list.curselection()
        current_idx = current_selection[0] if current_selection else -1

        self.rom_detail_list.unbind('<<ListboxSelect>>')

        self.rom_detail_list.delete(0, 'end')
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
            self.rom_detail_list.insert('end', *paths_display)
            self.rom_name_list.insert('end', *names_display)

        self.rom_detail_list.bind('<<ListboxSelect>>', self.sync_selection_and_refresh)

        if current_idx >= 0 and current_idx < len(self.rom_list):
            self.after(1, lambda: self.sync_selection_and_refresh(current_idx))
        elif self.rom_list:
            self.after(1, lambda: self.sync_selection_and_refresh(0))
        else:
            self.update_ui_only()

    def update_preview(self):
        sel = self.rom_detail_list.curselection()
        self.preview_textbox.delete(1.0, 'end')
        if not sel or not self.rom_list:
            self.preview_textbox.insert('end', "选择 ROM 查看详情...")
            return
        
        idx = sel[0]
        rom = self.rom_list[idx]
        platform = self.selected_platform.get()
        core_display_text = self.selected_core.get()
        
        core_path = ""
        core_name = ""
        try:
            if ' | ' in core_display_text: 
                parts = core_display_text.split(' | ')
                if len(parts) == 2:
                    core_path = parts[1].strip()
                    core_name = parts[0].strip()
            
            if not core_path:
                last_open_paren = core_display_text.rindex(' (')
                friendly_name = core_display_text[:last_open_paren].strip() 
                platform_data = PLATFORM_MAPPING.get(platform)
                if platform_data:
                    for path, name in platform_data.get("name_map", {}).items():
                        if name == friendly_name:
                            core_path = path
                            break
                core_name = get_core_name(core_path, platform) if core_path else "Unknown Core" 
        except Exception:
            core_path = "Unknown Path"
            core_name = "Unknown Core"
        
        self.preview_textbox.insert('end', f"平台：{platform}\n")
        self.preview_textbox.insert('end', f"列表名：{self.playlist_name.get()}\n")
        self.preview_textbox.insert('end', f"核心名称：{core_name}\n")
        self.preview_textbox.insert('end', f"核心路径：{core_path}\n\n")
        self.preview_textbox.insert('end', f"ROM 名称：{rom['label']}\n")
        self.preview_textbox.insert('end', f"ROM 路径：{rom['path']}")
        
    
    def update_left_thumbnail(self):
        sel = self.rom_detail_list.curselection()
        if not sel or not self.rom_list:
            self.thumb_label_left.configure(image='', text="请选中一个 ROM\n\n双击此处添加", width=258, height=258, text_color='gray') 
            self.thumb_label_left.image = None
            self.original_left_img = None
            self.left_path_status.set(INITIAL_STATUS_TEXT)
            return
        idx = sel[0]
        if idx >= len(self.rom_list): return
        
        rom = self.rom_list[idx]
        self.last_selection_id += 1
        current_request_id = self.last_selection_id
        ra_path_root = self.retroarch_dir.get()
        lpl_name_root = self.playlist_name.get() or self.current_lpl_name or "Unknown"
        left_mode_val = self.playlist_settings['left_thumbnail_mode'].get()
        
        self.thumb_label_left.configure(text="正在加载...", image='')
        self.left_path_status.set("正在查找缩略图...")
        self.original_left_img = None 

        
        t_left = threading.Thread(
            target=self._load_thumbnail_async_worker,
            args=(rom, ra_path_root, lpl_name_root, left_mode_val, self.thumb_label_left, self.left_path_status, current_request_id, 'left'),
            daemon=True 
        )
        t_left.start()

    
    def update_right_thumbnail(self):
        sel = self.rom_detail_list.curselection()
        if not sel or not self.rom_list:
            self.thumb_label_right.configure(image='', text="请选中一个 ROM\n\n双击此处添加", width=258, height=258, text_color='gray')
            self.thumb_label_right.image = None
            self.original_right_img = None
            self.right_path_status.set(INITIAL_STATUS_TEXT)
            return
        idx = sel[0]
        if idx >= len(self.rom_list): return
        
        rom = self.rom_list[idx]
        current_request_id = self.last_selection_id 
        ra_path_root = self.retroarch_dir.get()
        lpl_name_root = self.playlist_name.get() or self.current_lpl_name or "Unknown"
        right_mode_val = self.playlist_settings['right_thumbnail_mode'].get()
        
        self.thumb_label_right.configure(text="正在加载...", image='')
        self.right_path_status.set("正在查找缩略图...")
        self.original_right_img = None 
        
        t_right = threading.Thread(
            target=self._load_thumbnail_async_worker,
            args=(rom, ra_path_root, lpl_name_root, right_mode_val, self.thumb_label_right, self.right_path_status, current_request_id, 'right'),
            daemon=True 
        )
        t_right.start()

    def _check_thumbnail_existence(self, rom_name, ra_path_root, lpl_name_root, mode):
        """检查特定模式（1/2/3）的缩略图是否存在。"""
        folder_map = {1: "Named_Snaps", 2: "Named_Titles", 3: "Named_Boxarts"}
        folder = folder_map.get(mode)
        
        if not folder:
            return "N/A", "N/A"
            
        path_prefix = Path(ra_path_root) / "thumbnails" / lpl_name_root / folder / rom_name
        
        found = False
        found_filename = ""
        
        for ext in ['.png', '.jpg', '.jpeg']:
            check_path_attempt = path_prefix.with_suffix(ext) 
            if check_path_attempt.exists():
                found = True
                found_filename = check_path_attempt.name
                break
        
        status_text = "✅ 有" if found else "❌ 无"
        
        return status_text, found_filename

    def _load_thumbnail_async_worker(self, rom, ra_path_root, lpl_name_root, mode_val_to_use, target_thumb_label, target_status_var, request_id, side):
        try:
            from PIL import Image, ImageTk 
        except ImportError:
            self.after(0, lambda: target_status_var.set("❌ 依赖库 PIL 未安装！"))
            return
        
        if request_id < self.last_selection_id: return
        
        try: thumbnail_name = Path(rom['path']).stem
        except Exception: thumbnail_name = rom['label']
        
        folder_map = {1: "Named_Snaps", 2: "Named_Titles", 3: "Named_Boxarts"}
        
        # --- Part 1: Find and load the DISPLAYED image ---
        
        final_modes = []
        mode_to_use = int(mode_val_to_use)
        
        if mode_to_use == 5: final_modes.extend([2, 3, 1]) 
        elif mode_to_use == 4: final_modes.extend([3, 2, 1])
        elif mode_to_use != 0: final_modes.append(mode_to_use)
        
        found_image = False
        found_path = ""
        current_mode_folder = "N/A"
        
        for mode in final_modes:
            if request_id < self.last_selection_id: return
            folder = folder_map.get(mode)
            if not folder: continue
            
            path_prefix = Path(ra_path_root) / "thumbnails" / lpl_name_root / folder / thumbnail_name
            
            for ext in ['.png', '.jpg', '.jpeg']:
                check_path = path_prefix.with_suffix(ext) 
                
                if check_path.exists():
                    try:
                        img = Image.open(check_path).convert("RGBA") 
                        
                        if side == 'left':
                            self.original_left_img = img
                        elif side == 'right':
                            self.original_right_img = img
                        
                        self.after(0, lambda: self._create_photo_and_update(request_id, img, target_thumb_label, side))
                        
                        found_image = True
                        found_path = str(check_path)
                        current_mode_folder = folder
                        break
                    except Exception:
                        continue 
            if found_image: break
            
        # --- Part 2: Check ALL 3 thumbnail existence statuses ---
        
        snap_status, snap_filename = self._check_thumbnail_existence(thumbnail_name, ra_path_root, lpl_name_root, 1)
        title_status, title_filename = self._check_thumbnail_existence(thumbnail_name, ra_path_root, lpl_name_root, 2)
        boxart_status, boxart_filename = self._check_thumbnail_existence(thumbnail_name, ra_path_root, lpl_name_root, 3)

        # --- Part 3: Construct the multi-line status string ---
        
        current_mode_cn = MODE_TO_CN.get(mode_val_to_use)
        current_mode_status = f"{'✅ 已找到' if found_image else '❌ 未找到'}"
        
        # 1. 查找结果状态
        status_line_1 = f"查找结果: {current_mode_status}"
        
        # 2. 当前模式
        status_line_2 = f"当前模式: {current_mode_cn}"
        
        # 3. 查找目录
        if mode_val_to_use in [1, 2, 3]:
            search_folder = folder_map.get(mode_val_to_use, "N/A")
        elif found_image:
            search_folder = current_mode_folder
        else:
            if mode_val_to_use == 4: search_folder = "Named_Boxarts/..."
            elif mode_val_to_use == 5: search_folder = "Named_Titles/..."
            else: search_folder = "N/A"

        status_line_3 = f"查找目录: .../thumbnails/{lpl_name_root}/{search_folder}"

        # 4. 查找文件名
        status_line_4 = f"查找文件名: {Path(found_path).name if found_path else thumbnail_name}.(png/jpg)"
        
        # 5. 状态检查
        status_line_5 = f"--- 三种模式拥有状态 ---"

        status_snap = f"截图 (Snap): {snap_status} ({snap_filename or '无文件'})"
        status_title = f"标题 (Title): {title_status} ({title_filename or '无文件'})"
        status_boxart = f"封面 (Boxart): {boxart_status} ({boxart_filename or '无文件'})"

        final_status = (
            f"{status_line_1}\n"
            f"{status_line_2}\n"
            f"{status_line_3}\n"
            f"{status_line_4}\n"
            f"{status_line_5}\n"
            f" - {status_snap}\n"
            f" - {status_title}\n"
            f" - {status_boxart}"
        )
        
        # 5. Update status variable
        self.after(0, lambda: target_status_var.set(final_status))
        
        # If image was not found, update label for failure
        if not found_image:
             self.after(0, lambda: target_thumb_label.configure(image='', text=f"未找到缩略图\n\n双击此处添加", width=258, height=258, text_color='gray'))
             
        if side == 'left':
            self.original_left_img = None
        elif side == 'right':
            self.original_right_img = None

    
    def _create_photo_and_update(self, request_id, original_img, target_thumb_label, side):
        if request_id < self.last_selection_id: return
        try:
            self._resize_and_update_image(target_thumb_label, original_img)
        except Exception:
            target_thumb_label.configure(image='', text=f"图片加载失败", width=258, height=258, text_color='darkred')
            target_thumb_label.image = None

    def _resize_and_update_image(self, target_label, original_img):
        TARGET_WIDTH = 258 
        MAX_HEIGHT = 258 
        
        orig_w, orig_h = original_img.size
        
        if orig_w == 0 or orig_h == 0:
            return 
        
        scale_factor_by_width = TARGET_WIDTH / orig_w
        target_h_by_width = int(orig_h * scale_factor_by_width)
        
        final_w = TARGET_WIDTH
        final_h = target_h_by_width
        
        if target_h_by_width > MAX_HEIGHT:
            scale_factor_by_height = MAX_HEIGHT / orig_h
            
            final_w = int(orig_w * scale_factor_by_height)
            final_h = MAX_HEIGHT 
            
        final_size = (final_w, final_h)
        
        resized_img = original_img.resize(final_size, Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(resized_img)
        
        label_w = TARGET_WIDTH
        label_h = MAX_HEIGHT 

        target_label.configure(
            image=photo, 
            text="", 
            width=label_w, 
            height=label_h,
            compound='center'
        )
        
        target_label.image = photo 


    def update_ui_only(self, event=None):
        if not self.rom_list or not self.rom_detail_list.curselection():
            self.left_path_status.set(INITIAL_STATUS_TEXT)
            self.right_path_status.set(INITIAL_STATUS_TEXT)
            
        self.update_preview()
        self.update_left_thumbnail()
        self.update_right_thumbnail()

    # --- 功能方法 ---
    def on_platform_change(self, event=None):
        platform = self.selected_platform.get()
        default_core_path = PLATFORM_MAPPING[platform]["default_core"]
        default_core_name = get_core_name(default_core_path, platform)
        
        match = [c for c in self.core_list if c.startswith(default_core_name)]
        if match:
            self.selected_core.set(match[0])
        
        self.update_ui_only()

    def on_core_change(self, event=None):
        self.update_ui_only()
        
    def update_thumbnail_mode(self, var_name):
        mode_map = CN_TO_MODE
        new_display = self.settings_vars_str[var_name].get()
        new_mode = mode_map.get(new_display, self.playlist_settings[var_name].get())
        self.playlist_settings[var_name].set(new_mode)
        
        if 'left' in var_name:
            self.after(10, self.update_left_thumbnail) 
        elif 'right' in var_name:
            self.after(10, self.update_right_thumbnail) 
        
    def select_retroarch_dir(self):
        dir_path = filedialog.askdirectory(title="选择 RetroArch 根目录")
        
        if dir_path:
            self.retroarch_dir.set(dir_path)
            playlists_dir = Path(dir_path) / "playlists"
            
            lpl_files = []
            if playlists_dir.is_dir():
                for f in playlists_dir.iterdir():
                    if f.suffix.lower() == '.lpl':
                        lpl_files.append(f.name)
            
            self.lpl_list = sorted(lpl_files)
            
            display_values = ["选择已有播放列表 (.lpl)"] + self.lpl_list
            self.lpl_combo.configure(values=display_values)
            self.selected_lpl.set(display_values[0])
            
            self.after(10, self.update_ui_only)

    def on_lpl_combo_select(self, selection):
        if selection == "选择已有播放列表 (.lpl)":
            return

        ra_dir = self.retroarch_dir.get().strip()
        if not ra_dir:
            messagebox.showwarning("警告", "请先选择 RetroArch 目录！")
            self.selected_lpl.set("选择已有播放列表 (.lpl)")
            return
            
        lpl_path = Path(ra_dir) / "playlists" / selection
        
        if lpl_path.is_file():
            try:
                self._load_lpl_from_path(str(lpl_path))
            except Exception as e:
                messagebox.showerror("加载错误", f"加载播放列表失败：{e}")
                self.selected_lpl.set("选择已有播放列表 (.lpl)")
                
        else:
            messagebox.showerror("错误", f"找不到文件：{lpl_path}")
            self.selected_lpl.set("选择已有播放列表 (.lpl)")

    def do_save(self):
        if not self.rom_list:
            messagebox.showwarning("警告", "列表为空，无需保存。")
            return
            
        lpl_name = self.playlist_name.get().strip()
        if not lpl_name:
             messagebox.showwarning("警告", "请设置一个播放列表名称（左上角）！")
             return

        ra_dir_val = self.retroarch_dir.get().strip()
        
        target_path = None
        should_save = False

        if ra_dir_val and Path(ra_dir_val).is_dir():
            playlists_dir = Path(ra_dir_val) / "playlists"
            playlists_dir.mkdir(parents=True, exist_ok=True)
            target_path = playlists_dir / f"{lpl_name}.lpl"
            
            is_existing_file = target_path.is_file()
            
            if is_existing_file:
                should_save = messagebox.askyesno(
                    "确认覆盖",
                    f"播放列表 '{lpl_name}.lpl' 已存在于 RetroArch 目录中。\n是否覆盖此文件？"
                )
            else:
                should_save = messagebox.askyesno(
                    "确认新建",
                    f"播放列表 '{lpl_name}.lpl' 文件是新的。\n是否在 RetroArch 目录新建文件？"
                )
        else:
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

        if should_save and target_path:
            self.current_lpl_name = lpl_name
            
            platform = self.selected_platform.get()
            core_display_text = self.selected_core.get()
            core_path = ""
            
            if ' | ' in core_display_text:
                core_path = core_display_text.split(' | ')[-1].strip()
            else:
                try:
                    last_open_paren = core_display_text.rindex(' (')
                    friendly_name = core_display_text[:last_open_paren].strip() 
                except ValueError:
                    friendly_name = core_display_text.strip()
                
                platform_data = PLATFORM_MAPPING.get(platform)
                if platform_data:
                    for path, name in platform_data["name_map"].items():
                        if name == friendly_name:
                            core_path = path
                            break

            if not core_path:
                 core_path = PLATFORM_MAPPING[platform]["default_core"]
                 
            settings = {k: v.get() for k, v in self.playlist_settings.items()} 
            count = generate_playlist(self.rom_list, str(target_path), core_path, settings, platform) 
                 
            messagebox.showinfo("成功", f"保存完成！\n保存至: {os.path.basename(target_path)}\n共 {count} 个游戏")
            self.after(10, self.update_lists) 

    def load_lpl(self):
        try:
            path = filedialog.askopenfilename(filetypes=[("Playlist", "*.lpl")])
            if path:
                self._load_lpl_from_path(path)
        except Exception as e:
            messagebox.showerror("错误", f"选择 LPL 文件时发生错误: {e}")
            return

    def _load_lpl_from_path(self, path):
        try:
            self.rom_list, settings, loaded_core_path = load_playlist(path)
        except Exception as e:
            messagebox.showerror("错误", f"解析 LPL 文件内容时发生错误: {e}\n文件路径: {path}")
            return
            
        self.current_lpl_name = Path(path).stem
        self.playlist_name.set(self.current_lpl_name) 
        
        inferred_platform = "Windows"
        inferred_name = "Unknown Core"
        
        for platform, data in PLATFORM_MAPPING.items():
            if loaded_core_path in data["name_map"].keys():
                inferred_platform = platform
                inferred_name = data["name_map"][loaded_core_path]
                break
        
        self.selected_platform.set(inferred_platform)
        
        target_display = ""
        for core_display in self.core_list:
            if core_display.startswith(inferred_name):
                target_display = core_display
                break
        
        if target_display:
            self.selected_core.set(target_display)
        else:
            custom_name = f"{inferred_name} ({inferred_platform}) | {loaded_core_path}"
            if custom_name not in self.core_list:
                self.core_list.insert(0, custom_name)
                self.core_combo.configure(values=self.core_list) 
            self.selected_core.set(custom_name)

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
        
        self.preview_textbox.delete(1.0, 'end')
        self.preview_textbox.insert('end', f"已加载 {len(self.rom_list)} 个项目")

    
    def edit_rom_path_on_double_click(self, event):
        sel = self.rom_detail_list.curselection()
        if not sel: return
        idx = sel[0]
        if idx >= len(self.rom_list): return

        current_path = self.rom_list[idx]['path']
        current_dir = os.path.dirname(current_path) if os.path.dirname(current_path) else "."

        new_file = filedialog.askopenfilename(
            title="选择新的 ROM 文件",
            initialdir=current_dir,
            initialfile=os.path.basename(current_path),
            filetypes=[
                ("所有支持的 ROM", "*.nes *.sfc *.smc *.gb *.gba *.bin *.cue *.iso *.chd *.zip *.7z *.cso *.exe *.md *.z64 *.n64 *.m3u"),
                ("所有文件", "*.*")
            ]
        )

        if new_file:
            new_path = os.path.normpath(new_file).replace('\\', '/')
            old_path = self.rom_list[idx]['path']
            self.rom_list[idx]['path'] = new_path
            self.rom_list[idx]['label'] = Path(new_path).stem
            self.update_lists()
            self.sync_selection_and_refresh(idx)
            messagebox.showinfo(
                "路径已更新",
                f"已将路径从：\n{old_path}\n\n更新为：\n{new_path}"
            )
            
    def global_edit_rom_path(self):
        if not self.rom_list:
            messagebox.showwarning("警告", "列表为空，无需修改路径。")
            return
            
        platform = self.selected_platform.get()
        is_manual_mode = platform != "Windows" 
            
        first_path = self.rom_list[0]['path']
        
        try:
            path_suggestion = Path(first_path).parent.parent
            initial_old_value = str(path_suggestion).replace('\\', '/')
        except Exception:
            initial_old_value = ""

        old_prefix_prompt = ("请输入您想在所有 ROM 路径中替换掉的**旧路径前缀**。...")
        old_prefix = simpledialog.askstring("全局路径修改 - 步骤 1/2", old_prefix_prompt, initialvalue=initial_old_value)
        
        if not old_prefix: return
        old_prefix = os.path.normpath(old_prefix).replace('\\', '/')
        if old_prefix and not old_prefix.endswith('/'):
            old_prefix += '/'

        new_base_dir = None
        
        if is_manual_mode:
            manual_prompt = ("【非 Windows 系统，路径指定手动输入】\n请输入完整的**新根目录路径**。...")
            new_base_dir = simpledialog.askstring("全局路径修改 - 步骤 2/2 (手动输入)", manual_prompt, initialvalue="/new/roms/")
            if not new_base_dir: return
        else:
            new_base_dir = filedialog.askdirectory(title="全局路径修改 - 步骤 2/2: 选择新的根目录")
            if not new_base_dir: return

        new_base_dir = os.path.normpath(new_base_dir).replace('\\', '/')
        if new_base_dir and not new_base_dir.endswith('/'): new_base_dir += '/'

        modified_count = 0
        
        for r in self.rom_list:
            original_path = r['path']
            
            if original_path.startswith(old_prefix):
                relative_path = original_path[len(old_prefix):]
                new_path = new_base_dir + relative_path
                r['path'] = new_path
                modified_count += 1
                
        self.update_lists()
        
        if modified_count > 0:
            messagebox.showinfo("成功", f"全局路径修改完成！\n成功修改了 {modified_count} 个 ROM 的路径。")
        else:
            messagebox.showwarning("警告", "没有 ROM 的路径以您输入的旧前缀开始，请检查路径和斜杠。未进行任何修改。")

    def add_single_rom(self):
        try:
            path = filedialog.askopenfilename(
                filetypes=[("ROM Files", "*.nes *.gb *.gba *.sfc *.bin *.cue *.iso *.chd *.pbp *.exe *.md *.z64 *.n64 *.zip *.7z *.cso *.m3u")]
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
        try:
            folder = filedialog.askdirectory()
        except Exception as e:
            messagebox.showerror("错误", f"选择文件夹时发生错误: {e}")
            return
            
        if folder:
            files = [os.path.join(r, f) for r, _, fs in os.walk(folder) for f in fs]
            candidates = filter_rom_files(files)
            if candidates and messagebox.askyesno("确认", f"发现 {len(candidates)} 个 ROM，是否全部添加？"):
                self.rom_list.extend(candidates)
                self.update_lists()
                if self.rom_list:
                    last_idx = len(self.rom_list)-1
                    self.sync_selection_and_refresh(last_idx)

    def clear_list(self):
        if messagebox.askyesno("确认", "确定清空所有 ROM？"):
            self.rom_list.clear()
            self.update_lists()

    def edit_rom_label(self):
        sel = self.rom_detail_list.curselection()
        if not sel: 
             messagebox.showwarning("警告", "请先选中一个 ROM！")
             return
             
        idx = sel[0]
        new = simpledialog.askstring("编辑名称", "新名称:", initialvalue=self.rom_list[idx]['label'])
        if new and new.strip():
            self.rom_list[idx]['label'] = new.strip()
            self.update_lists()
            self.sync_selection_and_refresh(idx)

    def edit_rom_label_on_double_click(self, event):
        try:
            idx = self.rom_name_list.nearest(event.y)
        except Exception:
            return
            
        if idx is not None and idx < len(self.rom_list):
            self.sync_selection_and_refresh(idx) 
            self.after(10, self.edit_rom_label) 

                
    def delete_rom(self):
        sel = self.rom_detail_list.curselection()
        if sel and messagebox.askyesno("确认", "确定删除该 ROM？"):
            idx_to_delete = sel[0]
            del self.rom_list[idx_to_delete]
            self.update_lists()
            new_idx = min(idx_to_delete, len(self.rom_list) - 1)
            if new_idx >= 0:
                self.sync_selection_and_refresh(new_idx)
                
    def replace_thumbnail(self, side):
        sel = self.rom_detail_list.curselection()
        if not sel:
            messagebox.showwarning("警告", "请先选中一个 ROM！")
            return
        
        idx = sel[0]
        
        try:
            rom_file_stem = Path(self.rom_list[idx]['path']).stem 
        except Exception:
            messagebox.showwarning("警告", "无法获取 ROM 文件名。请确保路径有效。")
            return
            
        ra_dir = self.retroarch_dir.get().strip()
        lpl_name = self.playlist_name.get().strip()

        if not ra_dir or not lpl_name:
            messagebox.showwarning("警告", "请先选择 RetroArch 目录并设置播放列表名称！")
            return

        if side == 'left':
            mode_val = self.playlist_settings['left_thumbnail_mode'].get()
        elif side == 'right':
            mode_val = self.playlist_settings['right_thumbnail_mode'].get()
        else:
            return

        mode_folder_map = {1: "Named_Snaps", 2: "Named_Titles", 3: "Named_Boxarts"}
        mode_folder = mode_folder_map.get(mode_val)
        
        if mode_val == 0 or mode_val in [4, 5] or not mode_folder:
            messagebox.showwarning("警告", "当前缩略图模式为非标准模式 (0, 4, 5)，请切换到具体模式 (1, 2, 3) 后再尝试替换。")
            return

        try:
            new_img_path = filedialog.askopenfilename(
                title="选择新缩略图 (PNG/JPG)",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
            )
            if not new_img_path: return
            new_img_path = Path(new_img_path)
            
            target_dir = Path(ra_dir) / "thumbnails" / lpl_name / mode_folder
            target_dir.mkdir(parents=True, exist_ok=True)
            
            original_suffix = new_img_path.suffix.lower()
            target_ext = '.jpg' if original_suffix in ['.jpg', '.jpeg'] else '.png'
            other_ext = '.png' if target_ext == '.jpg' else '.jpg'

            target_file = target_dir / f"{rom_file_stem}{target_ext}" 
            other_file = target_dir / f"{rom_file_stem}{other_ext}" 

            if other_file.exists():
                os.remove(other_file)
            
            img = Image.open(new_img_path)
            
            if target_ext == '.png':
                img.save(target_file, format='PNG')
            else:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(target_file, format='JPEG', quality=90)
            
            messagebox.showinfo("成功", f"缩略图已成功替换！\n保存至：{target_file.name}")
            
            if side == 'left':
                self.update_left_thumbnail()
            elif side == 'right':
                self.update_right_thumbnail()

        except Exception as e:
            messagebox.showerror("错误", f"替换缩略图时发生错误: {e}")
            self.after(10, self.update_ui_only)


    def show_help(self):
        help_text = ("RetroArch 播放列表生成器 V0.51  说明：\n\n"
                     "1. 点击 **'选择 RetroArch 目录'** 设置您的配置文件夹。\n"
                     "   - 脚本会自动尝试找到缩略图路径并加载已有的 .lpl 文件名。\n"
                     "2. 使用 **'加载 .lpl'** 或下拉菜单加载现有列表，或直接 **'添加 ROM'**。\n"
                     "3. **双击 ROM 路径** 可修改单个 ROM 文件的路径。\n"
                     "4. **双击右列 (ROM 路径) → 弹出文件选择框修改路径**。\n"
                     "5. **双击缩略图预览框** 可替换当前模式下的缩略图（仅支持 截图, 标题, 封面 模式）。\n"
                     "6. 设置核心和缩略图模式后，点击 **'保存 .lpl'** 生成文件。\n"
                     "图片建议: 建议图片尺寸小于 512px，文件大小小于 3MB。\n"
                     "原作者：@爱折腾的老家伙"
                     )
        messagebox.showinfo("帮助与说明", help_text)

    def on_closing(self):
        self.destroy()

if __name__ == "__main__":
    try:
        app = PlaylistGenerator()
        app.mainloop()
    except Exception as e:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("致命错误", f"程序运行发生致命错误，请检查 Python 环境和依赖库：\n{e}")
        root.destroy()
        exit()