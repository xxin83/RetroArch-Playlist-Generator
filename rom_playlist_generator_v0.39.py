"""
开源声明：
本软件为开源项目，旨在帮助 RetroArch 用户生成和管理播放列表。
您可以自由修改、复制和分发本软件的源代码，但请遵守以下条款：
- 不得用于任何商业用途，包括但不限于出售、租赁或作为付费服务的一部分。
- 修改或分发时，必须保留原作者署名（@爱折腾的老家伙）和本开源声明。
- 作者不对软件的任何使用后果负责，包括但不限于数据丢失或硬件损坏。
- 如果您对软件进行了改进，欢迎分享回原作者或社区，但非强制要求。

原作者：@爱折腾的老家伙
版本：V0.3.10
最后更新：2023年（基于代码推测）
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
PLATFORM_MAPPING = {
    # Windows 核心配置 (使用相对路径和 .dll)
    "Windows": {
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
    },
    # Nintendo Switch 核心配置 (使用绝对路径和 .nro)
    "Switch": {
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
    },
}

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

# --- 动态核心选择函数 ---
def suggest_core_by_extension(file_path, platform):
    """根据文件扩展名和目标平台建议核心路径"""
    ext = Path(file_path).suffix.lower()
    platform_data = PLATFORM_MAPPING.get(platform)
    if not platform_data: return "" 
    
    mapping = platform_data['ext_map']
    default_core = platform_data['default_core']
    return mapping.get(ext, default_core)

# --- 动态核心名称获取函数 ---
def get_core_name(core_path, platform):
    """根据核心路径和目标平台获取友好名称"""
    platform_data = PLATFORM_MAPPING.get(platform)
    if not platform_data: return "Unknown Core"
    
    name_map = platform_data['name_map']
    return name_map.get(core_path, "Unknown Core")

def filter_rom_files(files, extensions=None):
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
    """生成 LPL 文件。现在需要 platform 参数来获取核心名称。"""
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


# ====================== GUI 主程序 (添加平台选择和缩略图打开功能) ======================
def create_gui():
    root = tk.Tk()
    root.title("RetroArch 播放列表生成器 V0.3.10（@爱折腾的老家伙）") 
    root.configure(bg='#f0f0f0')

    # 全局变量
    global rom_list, current_lpl_name, rom_detail, rom_name_list, thumb_label, playlist_settings, preview, path_btn, path_debug_label, last_selection_id, selected_rom_name_display, right_thumb_label, right_path_debug_label, core_list, core_combo, platform_combo
    rom_list = []
    retroarch_dir = tk.StringVar()
    current_lpl_name = ""
    last_selection_id = 0 
    
    # 缩略图模式设置变量
    playlist_settings = {
        'label_display_mode': tk.IntVar(value=0), 
        'right_thumbnail_mode': tk.IntVar(value=4),
        'left_thumbnail_mode': tk.IntVar(value=2),
        'thumbnail_match_mode': tk.IntVar(value=0),
    }
    # Combobox 关联的字符串变量
    settings_vars_str = {
        'right_thumbnail_mode': tk.StringVar(value=MODE_TO_CN[4]),
        'left_thumbnail_mode': tk.StringVar(value=MODE_TO_CN[2]),
    }
    
    # --- 平台选择和核心变量 ---
    selected_platform = tk.StringVar(value="Windows") 
    core_list_raw = get_all_cores_list()
    core_list = core_list_raw 
    selected_core = tk.StringVar(value=core_list[0] if core_list else "") 
    playlist_name = tk.StringVar(value="MyPlaylist")

    
    # ------------------ 缩略图/预览 UI 更新函数 ------------------
    
    def _update_thumb_label_safe(request_id, photo, found_type_cn, full_path, target_thumb_label, target_path_debug_label, search_results, error_text=None):
        if request_id < last_selection_id: return
        current_rom_name = "N/A"
        sel = rom_detail.curselection()
        if sel and sel[0] < len(rom_list):
             current_rom_name = rom_list[sel[0]]['label']
        
        # --- 新的路径显示逻辑：生成详细的搜索报告 ---
        path_report = ["--- 缩略图搜索报告 ---"]
        path_fg_color = 'darkgray'
        
        if search_results:
            for status, mode_cn, path in search_results:
                if status == "Found":
                    path_report.append(f"✅ 找到 ({mode_cn}): {path}")
                    path_fg_color = 'darkgreen'
                elif status == "Failed_Load":
                    path_report.append(f"⚠️ 文件损坏 ({mode_cn}): {path}")
                    path_fg_color = 'darkred'
                else:
                    path_report.append(f"❌ 未找到 ({mode_cn}): {path}")
            
            # 如果 photo 是 None，但有搜索结果，说明是全部失败或文件损坏
            if photo is None and path_fg_color == 'darkgreen':
                path_fg_color = 'darkred'
                
            path_display = "\n".join(path_report)
        else:
            # 模式 0 或未进行搜索
            path_display = error_text if error_text else "缩略图模式已禁用或列表为空。"
            path_fg_color = 'darkred'

        # 更新缩略图主标签
        if photo is not None:
            target_thumb_label.config(image=photo, text="")
            target_thumb_label.image = photo 
            target_path_debug_label.config(text=path_display, fg='darkgreen') # 找到图片，无论如何都是绿色
        else:
            target_thumb_label.config(image='', text=f"未找到缩略图:\n{current_rom_name}", fg='gray')
            target_path_debug_label.config(text=path_display, fg=path_fg_color)
            target_thumb_label.image = None

    def _create_photo_and_update(request_id, img, found_type_cn, full_path, target_thumb_label, target_path_debug_label, search_results):
        if request_id < last_selection_id: return
        try:
            photo = ImageTk.PhotoImage(img) 
            _update_thumb_label_safe(request_id, photo, found_type_cn, full_path, target_thumb_label, target_path_debug_label, search_results, None)
        except Exception as e:
            error_text = f"缩略图创建失败: {Path(full_path).name}\n错误: {e}"
            _update_thumb_label_safe(request_id, None, None, full_path, target_thumb_label, target_path_debug_label, search_results, error_text)

    def _load_thumbnail_async_worker(rom, ra_path_root, lpl_name_root, mode_val_to_use, target_thumb_label, target_path_debug_label, request_id):
        if request_id < last_selection_id: return
        if rom is None: return
        try: thumbnail_name = Path(rom['path']).stem
        except Exception: thumbnail_name = rom['label']
        
        final_modes = []
        mode_to_use = int(mode_val_to_use)
        if mode_to_use == 5: final_modes.extend([2, 3, 1]) 
        elif mode_to_use == 4: final_modes.extend([3, 2, 1])
        elif mode_to_use != 0: final_modes.append(mode_to_use)
        final_modes = list(dict.fromkeys(final_modes)) 
        
        search_results = [] # 存储所有搜索结果: (状态: "Found", "Not Found", "Failed_Load", 模式中文, 路径)
        found = False
        found_path = ""
        found_mode_cn = ""
        
        folder_map = {1: "Named_Snaps", 2: "Named_Titles", 3: "Named_Boxarts"}

        if mode_to_use == 0:
             # mode 0 禁用，results为空
             path_display_text = "缩略图模式已禁用 (模式 0)"
             root.after(0, lambda: _update_thumb_label_safe(request_id, None, None, "N/A", target_thumb_label, target_path_debug_label, search_results, path_display_text))
             return
             
        for mode in final_modes:
            if request_id < last_selection_id: return
            folder = folder_map.get(mode)
            if not folder: continue
            
            mode_cn = MODE_TO_CN.get(mode, "未知类型")
            path_prefix = Path(ra_path_root) / "thumbnails" / lpl_name_root / folder / thumbnail_name
            
            for ext in ['.png', '.jpg']:
                check_path = path_prefix.with_suffix(ext) 
                check_path_str = str(check_path)
                
                if check_path.exists():
                    try:
                        img = Image.open(check_path)
                        img = img.resize((180, 180), Image.Resampling.LANCZOS)
                        img = img.convert("RGBA") 
                        img.load() 
                        
                        # 记录找到的结果
                        search_results.append(("Found", mode_cn, check_path_str))
                        
                        found_mode_cn = mode_cn
                        found_path = check_path_str
                        found = True
                        
                        # 找到后，立即在主线程更新UI并退出
                        root.after(0, lambda: _create_photo_and_update(request_id, img, found_mode_cn, found_path, target_thumb_label, target_path_debug_label, search_results))
                        return
                        
                    except Exception as e:
                        # 找到文件但加载失败，记录并继续搜索（如果还有模式）
                        search_results.append(("Failed_Load", mode_cn, check_path_str))
                        continue # 继续尝试下一个扩展名或模式
                else:
                    # 未找到，记录路径
                    search_results.append(("Not Found", mode_cn, check_path_str))
                    
        # 如果循环结束仍未找到（或所有找到的文件都加载失败）
        if not found:
             # 如果搜索结果不为空，则显示完整的搜索报告
            if search_results:
                 error_text = "所有尝试的路径均未找到有效缩略图文件。"
                 # 注意：这里传递的是 photo=None，但包含了完整的 search_results
                 root.after(0, lambda: _update_thumb_label_safe(request_id, None, None, "N/A", target_thumb_label, target_path_debug_label, search_results, error_text))
            else:
                 # 理论上不会走到这里，除非 mode_to_use 非0但 final_modes 为空
                 error_text = "未执行搜索 (模式配置错误)。"
                 root.after(0, lambda: _update_thumb_label_safe(request_id, None, None, "N/A", target_thumb_label, target_path_debug_label, [], error_text))


    def update_left_thumbnail():
        sel = rom_detail.curselection()
        thumb_label.config(image='', text="正在加载缩略图...", fg='blue')
        path_debug_label.config(text="正在检查文件路径...", fg='darkgray')
        if not sel:
            thumb_label.config(image='', text="请先选中一个 ROM", fg='gray')
            path_debug_label.config(text="请在中间列表选中一个 ROM", fg='darkgray')
            return
        idx = sel[0]
        if idx >= len(rom_list): return
        rom = rom_list[idx]
        global last_selection_id
        last_selection_id += 1
        current_request_id = last_selection_id
        ra_path_root = retroarch_dir.get()
        lpl_name_root = current_lpl_name
        left_mode_val = int(playlist_settings['left_thumbnail_mode'].get())
        t_left = threading.Thread(
            target=_load_thumbnail_async_worker,
            args=(rom, ra_path_root, lpl_name_root, left_mode_val, thumb_label, path_debug_label, current_request_id),
            daemon=True 
        )
        t_left.start()

    def update_right_thumbnail():
        sel = rom_detail.curselection()
        right_thumb_label.config(image='', text="正在加载右侧图...", fg='blue')
        right_path_debug_label.config(text="正在检查文件路径...", fg='darkgray')
        if not sel:
            right_thumb_label.config(image='', text="请先选中一个 ROM", fg='gray')
            right_path_debug_label.config(text="请在中间列表选中一个 ROM", fg='darkgray')
            return
        idx = sel[0]
        if idx >= len(rom_list): return
        rom = rom_list[idx]
        global last_selection_id
        current_request_id = last_selection_id
        ra_path_root = retroarch_dir.get()
        lpl_name_root = current_lpl_name
        right_mode_val = int(playlist_settings['right_thumbnail_mode'].get())
        t_right = threading.Thread(
            target=_load_thumbnail_async_worker,
            args=(rom, ra_path_root, lpl_name_root, right_mode_val, right_thumb_label, right_path_debug_label, current_request_id),
            daemon=True 
        )
        t_right.start()


    def update_preview():
        sel = rom_detail.curselection()
        if not sel:
            preview.delete(1.0, 'end')
            preview.insert('end', "选择 ROM 查看预览...")
            path_btn.config(state='disabled')
            return
        idx = sel[0]
        rom = rom_list[idx]
        platform = selected_platform.get()
        
        core_display_text = selected_core.get()
        friendly_name = core_display_text.split(' (')[0]
        
        core_path = ""
        core_info = PLATFORM_MAPPING[platform]["name_map"]
        for path, name in core_info.items():
            if name == friendly_name:
                core_path = path
                break
        
        core_name = get_core_name(core_path, platform)
        
        preview.delete(1.0, 'end')
        preview.insert('end', f"平台: {platform}\n")
        preview.insert('end', f"名称: {rom['label']}\n")
        preview.insert('end', f"路径: {rom['path']}\n")
        preview.insert('end', f"核心路径: {core_path}\n")
        preview.insert('end', f"核心名称: {core_name}")
        path_btn.config(state='normal')

    def update_ui_only(event=None):
        update_preview()
        update_left_thumbnail()
        update_right_thumbnail()

    def update_thumbnail_mode(var_name):
        mode_map = CN_TO_MODE
        new_display = settings_vars_str[var_name].get()
        new_mode = mode_map.get(new_display, playlist_settings[var_name].get())
        playlist_settings[var_name].set(new_mode)
        root.after(10, update_ui_only) 
        
    def sync_selection_and_refresh(idx_or_event=None):
        idx = None
        if isinstance(idx_or_event, int):
            idx = idx_or_event
            if idx >= len(rom_list) or idx < 0:
                update_ui_only()
                return
        elif idx_or_event is not None:
            try:
                sel = rom_detail.curselection() 
                if not sel:
                    sel = rom_name_list.curselection() 
                    if not sel:
                        update_ui_only(); 
                        return
                idx = sel[0]
            except Exception:
                update_ui_only(); 
                return
        else:
            sel = rom_detail.curselection()
            if not sel: update_ui_only(); return
            idx = sel[0]

        # 确保选择和激活同步
        rom_detail.selection_clear(0, 'end')
        rom_detail.selection_set(idx)
        rom_detail.activate(idx) 
        rom_detail.see(idx) 
        
        rom_name_list.selection_clear(0, 'end')
        rom_name_list.selection_set(idx)
        rom_name_list.activate(idx)
        rom_name_list.see(idx) 
            
        selected_rom_name_display.config(state=tk.NORMAL)
        selected_rom_name_display.delete(1.0, 'end')
        selected_rom_name_display.insert('end', rom_list[idx]['label'])
        selected_rom_name_display.config(state=tk.DISABLED)

        root.after(10, update_ui_only) 

    def update_lists():
        global current_lpl_name
        
        current_selection = rom_detail.curselection() 
        current_idx = current_selection[0] if current_selection else -1
        
        rom_detail.unbind('<<ListboxSelect>>')
        
        rom_detail.delete(0, 'end')
        rom_name_list.delete(0, 'end')
        
        paths_display = []
        names_display = []
        lpl_name_prefix = f"[{current_lpl_name}] " if current_lpl_name else ""
        
        for i, r in enumerate(rom_list):
            fp = r['path']
            fp_disp = fp if len(fp) <= 80 else fp[:60] + "..." + fp[-20:]
            paths_display.append(lpl_name_prefix + fp_disp)
            
            names_display.append(f"[{i+1}] {r['label']}")
            
        if paths_display:
            rom_detail.insert('end', *paths_display)
            rom_name_list.insert('end', *names_display)
            
        # 滚动条配置已移至 create_gui() 初始化部分
            
        rom_detail.bind('<<ListboxSelect>>', sync_selection_and_refresh)
            
        if current_idx >= 0 and current_idx < len(rom_list):
            root.after(1, lambda: sync_selection_and_refresh(current_idx)) 
        elif rom_list:
             root.after(1, lambda: sync_selection_and_refresh(0)) 
        else:
            selected_rom_name_display.config(state=tk.NORMAL)
            selected_rom_name_display.delete(1.0, 'end')
            selected_rom_name_display.insert('end', "列表已清空。")
            selected_rom_name_display.config(state=tk.DISABLED)
            update_ui_only() 

    def on_platform_change(event=None):
        update_ui_only()

    def on_core_change(event=None):
        update_ui_only()

    # ------------------ UI 组件定义 (省略大部分不变的代码) ------------------
    
    # 顶部工具栏 (Top Bar)
    top = tk.Frame(root, bg='#f0f0f0')
    top.pack(fill='x', padx=10, pady=8)

    tk.Button(top, text="选择 RetroArch 目录", command=lambda: select_retroarch_dir(),
              bg='#44475a', fg='white', width=18).pack(side='left', padx=3)
    tk.Label(top, textvariable=retroarch_dir, bg='#f0f0f0', fg='blue', width=50, anchor='w').pack(side='left', padx=5)

    tk.Button(top, text="加载 .lpl", command=lambda: load_lpl(), bg='#bb86fc', fg='white', width=10).pack(side='left', padx=3)
    tk.Button(top, text="保存 .lpl", command=lambda: do_save(), bg='#ffb86c', fg='black', width=10).pack(side='left', padx=3) 
    tk.Button(top, text="清空列表", command=lambda: clear_list(), bg='#cf6679', fg='white', width=10).pack(side='left', padx=3)
    tk.Button(top, text="帮助", command=lambda: show_help(), bg='#6272a4', fg='white', width=10).pack(side='left', padx=3)  # 新增帮助按钮

    tk.Label(top, text="列表名:", bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(side='left', padx=10)
    tk.Entry(top, textvariable=playlist_name, width=20).pack(side='left', padx=3)

    # 中间主工作区域：水平 PanedWindow (分割左、中、右)
    mid = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    mid.pack(fill='both', expand=True, padx=10, pady=5)
    
    # ------------------ 1. 左侧容器：垂直 PanedWindow ------------------
    left_v_pane = ttk.PanedWindow(mid, orient=tk.VERTICAL)
    mid.add(left_v_pane, weight=0) 

    name_frame = tk.LabelFrame(left_v_pane, text=" 选中 ROM 名称 ", bg='#f0f0f0')
    name_frame.pack(fill='both', expand=True, padx=3, pady=0)
    left_v_pane.add(name_frame, weight=0) 
    
    selected_rom_name_display = tk.Text(name_frame, height=2, width=25, wrap='word', bg='#e0e0e0', relief='sunken', font=('Arial',10, 'bold'), borderwidth=1)
    selected_rom_name_display.pack(fill='x', padx=5, pady=(5, 50)) 
    selected_rom_name_display.insert('end', "请加载 LPL 或添加 ROM...")
    selected_rom_name_display.config(state=tk.DISABLED)

    left_thumb_options_container = tk.LabelFrame(left_v_pane, text=" 预览 (左侧图) ", bg='#f0f0f0')
    left_thumb_options_container.pack(fill='both', expand=True, padx=3, pady=0)
    left_v_pane.add(left_thumb_options_container, weight=1) 

    thumb_frame = tk.Frame(left_thumb_options_container, bg='white', relief='sunken', bd=2, height=250, width=200) 
    thumb_frame.pack(fill='x', pady=(5, 0), padx=5) 
    thumb_frame.pack_propagate(False) 
    thumb_label = tk.Label(thumb_frame, text="选择 ROM 查看缩略图", bg='white', fg='gray')
    thumb_label.pack(expand=True)
    
    left_mode_frame = tk.Frame(left_thumb_options_container, bg='#f0f0f0')
    left_mode_frame.pack(fill='x', padx=5, pady=5)
    tk.Label(left_mode_frame, text="左侧图选项:", bg='#f0f0f0', font=('Arial', 9)).pack(side='left', padx=(0,5))
    left_mode_combo = ttk.Combobox(left_mode_frame, textvariable=settings_vars_str['left_thumbnail_mode'],
                             values=THUMBNAIL_MODES_DISPLAY, state="readonly", width=15)
    left_mode_combo.pack(side='left')
    left_mode_combo.bind("<<ComboboxSelected>>", lambda e: update_thumbnail_mode('left_thumbnail_mode'))
    
    path_debug_label = tk.Label(left_thumb_options_container, text="", wraplength=240, justify=tk.LEFT, bg='#f0f0f0', font=('Arial', 8), height=15, anchor='n')
    path_debug_label.pack(fill='x', padx=5, pady=2)


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

    rom_name_list = tk.Listbox(center_v_pane, font=("Consolas", 9), width=50, selectmode=tk.SINGLE, 
                               exportselection=False, relief='flat', activestyle='none')
    center_v_pane.add(rom_name_list, weight=0) 
    rom_name_list.bind('<Button-1>', lambda e: "break")
    rom_name_list.bind('<<ListboxSelect>>', lambda e: rom_name_list.selection_clear(0, 'end')) 

    rom_detail = tk.Listbox(center_v_pane, font=("Consolas", 9), selectmode=tk.SINGLE, exportselection=False)
    center_v_pane.add(rom_detail, weight=1) 
    
    # --- 优化：统一设置列表框滚动条，只执行一次 ---
    def on_scroll_yview(*args):
        rom_detail.yview(*args)
        rom_name_list.yview(*args)

    sb_center.config(command=on_scroll_yview)
    rom_detail.config(yscrollcommand=sb_center.set)
    rom_name_list.config(yscrollcommand=sb_center.set)
    # ---------------------------------------------

    center_bottom_frame = tk.Frame(center_container, bg='#f0f0f0')
    center_bottom_frame.pack(fill='x', pady=5)
    
    tk.Button(center_bottom_frame, text="添加 ROM", command=lambda: add_single_rom(),
              bg='#03dac6', fg='black', width=12).pack(side='left', padx=10) 
    tk.Button(center_bottom_frame, text="添加文件夹", command=lambda: add_folder_roms(),
              bg='#018786', fg='white', width=12).pack(side='left', padx=10) 
              
    tk.Button(center_bottom_frame, text="编辑名称", command=lambda: edit_rom_label(),
              bg='#ffb86c', fg='black', width=12).pack(side='left', padx=10)
    tk.Button(center_bottom_frame, text="删除选中", command=lambda: delete_rom(),
              bg='#ff5555', fg='white', width=12).pack(side='left', padx=10)
    path_btn = tk.Button(center_bottom_frame, text="编辑路径", command=lambda: edit_rom_path(rom_detail.curselection()),
                         bg='#03dac6', fg='black', width=12, state='disabled')
    path_btn.pack(side='left', padx=10)
    
    # --- 按钮绑定新功能 ---
    tk.Button(center_bottom_frame, text="添加缩略图", command=lambda: add_thumbnail(),
              bg='#50fa7b', fg='black', width=12).pack(side='left', padx=10)
    tk.Button(center_bottom_frame, text="复制名称", command=lambda: copy_rom_name(),
              bg='#8be9fd', fg='black', width=12).pack(side='left', padx=10)  # 新增复制名称按钮


    # ------------------ 3. 右侧容器：垂直 PanedWindow ------------------
    right_v_pane = ttk.PanedWindow(mid, orient=tk.VERTICAL)
    mid.add(right_v_pane, weight=0) 
    
    preview_text_container = tk.LabelFrame(right_v_pane, text=" 预览文本 ", bg='#f0f0f0')
    preview_text_container.pack(fill='both', expand=True, padx=3, pady=0)
    right_v_pane.add(preview_text_container, weight=0) 

    preview_frame = tk.Frame(preview_text_container)
    preview_frame.pack(fill='both', expand=True, pady=5, padx=5)

    preview = tk.Text(preview_frame, height=6, width=25, wrap='word', bg='white', font=("Consolas", 9))
    sb_prev = tk.Scrollbar(preview_frame, orient="vertical", command=preview.yview)
    preview.configure(yscrollcommand=sb_prev.set)
    preview.pack(side="left", fill="both", expand=True)
    sb_prev.pack(side="right", fill="y")
    preview.insert('end', "选择 ROM 查看预览...")
    
    right_thumb_frame_container = tk.LabelFrame(right_v_pane, text=" 预览 (右侧图)  ", bg='#f0f0f0')
    right_thumb_frame_container.pack(fill='both', expand=True, padx=3, pady=0)
    right_v_pane.add(right_thumb_frame_container, weight=1) 
    
    thumb_frame_right = tk.Frame(right_thumb_frame_container, bg='white', relief='sunken', bd=2, height=250, width=200) 
    thumb_frame_right.pack(fill='x', pady=5, padx=5)
    thumb_frame_right.pack_propagate(False)
    
    right_thumb_label = tk.Label(thumb_frame_right, text="选择 ROM 查看右侧图", bg='white', fg='gray')
    right_thumb_label.pack(expand=True)
    
    right_mode_frame = tk.Frame(right_thumb_frame_container, bg='#f0f0f0')
    right_mode_frame.pack(fill='x', padx=5, pady=5)
    tk.Label(right_mode_frame, text="右侧图选项:", bg='#f0f0f0', font=('Arial', 9)).pack(side='left', padx=(0,5))
    right_mode_combo = ttk.Combobox(right_mode_frame, textvariable=settings_vars_str['right_thumbnail_mode'],
                              values=THUMBNAIL_MODES_DISPLAY, state="readonly", width=15)
    right_mode_combo.pack(side='left')
    right_mode_combo.bind("<<ComboboxSelected>>", lambda e: update_thumbnail_mode('right_thumbnail_mode'))

    right_path_debug_label = tk.Label(right_thumb_frame_container, text="", wraplength=240, justify=tk.LEFT, bg='#f0f0f0', font=('Arial', 8), height=15, anchor='n')
    right_path_debug_label.pack(fill='x', padx=5, pady=2)

    # ------------------ 4. 核心和平台选择区 (Core Row) ------------------
    core_container = tk.Frame(root, bg='#f0f0f0')
    core_container.pack(fill='x', padx=10, pady=(5, 8)) 
    
    core_frame = tk.LabelFrame(core_container, text=" 核心和平台选择 ", bg='#f0f0f0')
    core_frame.pack(fill='x', padx=3, pady=0)

    tk.Label(core_frame, text="目标平台:", bg='#f0f0f0', font=('Arial', 9, 'bold')).pack(side='left', padx=(5, 0), pady=5)
    platform_combo = ttk.Combobox(core_frame, textvariable=selected_platform, 
                                  values=list(PLATFORM_MAPPING.keys()), state="readonly", width=10)
    platform_combo.pack(side='left', padx=5, pady=2)
    platform_combo.bind("<<ComboboxSelected>>", on_platform_change)

    tk.Label(core_frame, text="选择核心:", bg='#f0f0f0', font=('Arial', 9, 'bold')).pack(side='left', padx=10, pady=5)
    core_combo = ttk.Combobox(core_frame, textvariable=selected_core, values=core_list, state="readonly")
    core_combo.pack(fill='x', padx=5, pady=2, expand=True)
    core_combo.bind("<<ComboboxSelected>>", on_core_change)
    
    # ------------------ 其它函数 (CRUD & Save/Load) ------------------

    def select_retroarch_dir():
        try:
            dir_path = filedialog.askdirectory(title="选择 RetroArch 根目录")
            if dir_path:
                retroarch_dir.set(dir_path)
                root.after(10, update_ui_only)
        except Exception as e:
            messagebox.showerror("错误", f"选择 RetroArch 目录时发生错误: {e}")

    def do_save():
        if not rom_list:
            messagebox.showwarning("警告", "列表为空，无需保存。")
            return
            
        if not playlist_name.get().strip():
             messagebox.showwarning("警告", "请设置一个播放列表名称！")
             return

        try:
            initial_file = f"{playlist_name.get()}.lpl"
            save_path = filedialog.asksaveasfilename(
                defaultextension=".lpl",
                initialfile=initial_file,
                filetypes=[("Playlist", "*.lpl")]
            )
        except Exception as e:
            messagebox.showerror("错误", f"选择保存路径时发生错误: {e}")
            return
            
        if save_path:
            global current_lpl_name
            current_lpl_name = Path(save_path).stem 
            
            platform = selected_platform.get()
            core_display_text = selected_core.get()
            friendly_name = core_display_text.split(' (')[0]
            
            core_path = ""
            for path, name in PLATFORM_MAPPING[platform]["name_map"].items():
                if name == friendly_name:
                    core_path = path
                    break

            if not core_path:
                 core_path = PLATFORM_MAPPING[platform]["default_core"] 
                 
            settings = {k: v.get() for k, v in playlist_settings.items()} 
            count = generate_playlist(rom_list, save_path, core_path, settings, platform) 
            messagebox.showinfo("成功", f"保存完成！\n保存至: {os.path.basename(save_path)}\n共 {count} 个游戏")
            root.after(10, update_lists) 


    def load_lpl():
        global rom_list, current_lpl_name, core_list
        try:
            path = filedialog.askopenfilename(filetypes=[("Playlist", "*.lpl")])
        except Exception as e:
            messagebox.showerror("错误", f"选择 LPL 文件时发生错误: {e}")
            return
            
        if path:
            try:
                rom_list, settings, loaded_core_path = load_playlist(path)
            except Exception as e:
                messagebox.showerror("错误", f"解析 LPL 文件内容时发生错误: {e}\n文件路径: {path}")
                return
                
            current_lpl_name = Path(path).stem
            playlist_name.set(current_lpl_name)
            
            inferred_platform = "Unknown"
            inferred_name = "Unknown Core"
            
            for platform, data in PLATFORM_MAPPING.items():
                if loaded_core_path in data["name_map"]:
                    inferred_platform = platform
                    inferred_name = data["name_map"][loaded_core_path]
                    break
            
            if inferred_platform in PLATFORM_MAPPING:
                selected_platform.set(inferred_platform)
            else:
                 selected_platform.set("Windows") 
            
            target_display = ""
            for core_display in core_list:
                if core_display.startswith(inferred_name):
                    target_display = core_display
                    break
            
            if target_display:
                selected_core.set(target_display)
            else:
                custom_name = f"未知核心 ({inferred_platform}) | {loaded_core_path}"
                if custom_name not in core_list:
                    core_list.insert(0, custom_name)
                    core_combo.config(values=core_list)
                selected_core.set(custom_name)

            if 'right_thumbnail_mode' in settings:
               playlist_settings['right_thumbnail_mode'].set(settings['right_thumbnail_mode'])
               settings_vars_str['right_thumbnail_mode'].set(MODE_TO_CN.get(settings['right_thumbnail_mode']))
            if 'left_thumbnail_mode' in settings:
               playlist_settings['left_thumbnail_mode'].set(settings['left_thumbnail_mode'])
               settings_vars_str['left_thumbnail_mode'].set(MODE_TO_CN.get(settings['left_thumbnail_mode']))


            update_lists()
            if rom_list:
                 root.after(1, lambda: sync_selection_and_refresh(0))
            else:
                 root.after(1, update_ui_only)
            
            preview.delete(1.0, 'end')
            preview.insert('end', f"已加载 {len(rom_list)} 个项目")


    def add_single_rom():
        try:
            path = filedialog.askopenfilename(
                filetypes=[("ROM Files", "*.nes *.gb *.gba *.sfc *.bin *.cue *.iso *.chd *.pbp *.exe *.md *.z64 *.zip *.7z *.cso *.m3u")]
            )
        except Exception as e:
            messagebox.showerror("错误", f"选择 ROM 文件时发生错误: {e}")
            return
            
        if path:
            platform = selected_platform.get()
            suggested_core_path = suggest_core_by_extension(path, platform)
            suggested_core_name = get_core_name(suggested_core_path, platform)
            
            match = [c for c in core_list if c.startswith(suggested_core_name)]
            if match:
                selected_core.set(match[0])
            
            norm_path = os.path.normpath(path).replace('\\', '/')
            
            rom_list.append({'path': norm_path,
                            'label': Path(path).stem})
            update_lists()
            last_idx = len(rom_list) - 1
            sync_selection_and_refresh(last_idx)

    def add_folder_roms():
        try:
            folder = filedialog.askdirectory()
        except Exception as e:
            messagebox.showerror("错误", f"选择文件夹时发生错误: {e}")
            return
            
        if folder:
            files = [os.path.join(r, f) for r, _, fs in os.walk(folder) for f in fs]
            candidates = filter_rom_files(files)
            if candidates and messagebox.askyesno("确认", f"发现 {len(candidates)} 个 ROM，全部添加？"):
                rom_list.extend(candidates)
                update_lists()
                if rom_list:
                    last_idx = len(rom_list)-1
                    sync_selection_and_refresh(last_idx)

    def clear_list():
        if messagebox.askyesno("确认", "清空所有 ROM？"):
            rom_list.clear()
            update_lists()

    def edit_rom_label():
        sel = rom_detail.curselection()
        if sel:
            idx = sel[0]
            new = simpledialog.askstring("编辑名称", "新名称:", initialvalue=rom_list[idx]['label'])
            if new and new.strip():
                rom_list[idx]['label'] = new.strip()
                update_lists()
                sync_selection_and_refresh(idx)
                
    def delete_rom():
        sel = rom_detail.curselection()
        if sel and messagebox.askyesno("确认", "确定删除该 ROM？"):
            idx_to_delete = sel[0]
            del rom_list[idx_to_delete]
            update_lists()
            new_idx = min(idx_to_delete, len(rom_list) - 1)
            if new_idx >= 0:
                sync_selection_and_refresh(new_idx)

    def edit_rom_path(selection):
        if not selection: return
        idx = selection[0]
        old_path = rom_list[idx]['path']
        
        try:
            new_path = filedialog.askopenfilename(
                title="重新选择 ROM 文件",
                initialdir=os.path.dirname(old_path) if os.path.exists(os.path.dirname(old_path)) else "",
                filetypes=[("ROM Files", "*.nes *.gb *.gba *.sfc *.bin *.cue *.iso *.chd *.pbp *.exe *.md *.z64 *.zip *.7z *.cso *.m3u")]
            )
        except Exception as e:
            messagebox.showerror("错误", f"选择 ROM 文件时发生错误: {e}")
            return
            
        if new_path:
            new_path = os.path.normpath(new_path).replace('\\', '/')
            rom_list[idx]['path'] = new_path
            rom_list[idx]['label'] = Path(new_path).stem 
            
            platform = selected_platform.get()
            new_core_path = suggest_core_by_extension(new_path, platform)
            new_core_name = get_core_name(new_core_path, platform)
            
            match = [c for c in core_list if c.startswith(new_core_name)]
            if match:
                selected_core.set(match[0])
            
            update_lists()
            sync_selection_and_refresh(idx)
                
    # --- 新增跨平台打开文件夹辅助函数 ---
    def open_folder_in_explorer(path):
        """根据当前操作系统打开文件浏览器到指定路径"""
        path = str(path)
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin": # macOS
                subprocess.run(['open', path])
            else: # Linux
                subprocess.run(['xdg-open', path])
        except Exception as e:
            messagebox.showwarning("警告", f"无法自动打开目录。请手动访问: {path}\n错误信息: {e}")

    # --- 修改后的 add_thumbnail 函数 ---
    def add_thumbnail():
        ra_dir = retroarch_dir.get().strip()
        playlist_name_val = playlist_name.get().strip()

        if not playlist_name_val:
            messagebox.showwarning("警告", "请先在右上角设置一个播放列表名称！")
            return

        # 构建目标缩略图根目录
        target_thumb_dir = Path(ra_dir) / "thumbnails" / playlist_name_val if ra_dir else None

        # 情况1：未选择 RetroArch 目录 → 仅提示路径
        if not ra_dir:
            messagebox.showinfo(
                "提示",
                f"您尚未选择 RetroArch 目录。\n"
                f"请手动将缩略图放置在 RetroArch 根目录下的：\n"
                f"thumbnails/{playlist_name_val}/\n"
                f"并在其中创建 Named_Boxarts / Named_Titles / Named_Snaps 子文件夹。"
            )
            return

        # 情况2：已选择目录 → 检查并处理目标目录
        try:
            if target_thumb_dir.exists():
                # 目录存在 → 直接打开
                open_folder_in_explorer(target_thumb_dir)
            else:
                # 目录不存在 → 询问是否创建
                create = messagebox.askyesno(
                    "创建目录",
                    f"缩略图目录不存在：\n{target_thumb_dir}\n\n"
                    f"是否现在创建该目录并打开？\n"
                    f"（会自动创建 Named_Boxarts / Named_Titles / Named_Snaps 子文件夹）"
                )
                if create:
                    # 创建主目录 + 三个标准子文件夹
                    for sub in ["Named_Boxarts", "Named_Titles", "Named_Snaps"]:
                        (target_thumb_dir / sub).mkdir(parents=True, exist_ok=True)
                    messagebox.showinfo("成功", f"已创建目录：\n{target_thumb_dir}")
                    open_folder_in_explorer(target_thumb_dir)
                # else: 用户选“否”，不做任何操作
        except Exception as e:
            messagebox.showerror("错误", f"操作缩略图目录时出错：\n{e}")

    # --- 新增帮助函数：弹出软件说明 ---
    def show_help():
        help_text = (
            "RetroArch 播放列表生成器 使用说明：\n\n"
            "1. 选择 RetroArch 目录：设置 RetroArch 根路径，用于缩略图预览。\n"
            "2. 添加 ROM：单个文件或整个文件夹，支持常见 ROM 格式。\n"
            "3. 编辑名称/路径：双击路径或点击按钮修改 ROM 信息。\n"
            "4. 缩略图模式：选择左侧/右侧缩略图显示偏好（封面、标题等）。\n"
            "5. 核心选择：根据平台和 ROM 类型自动建议核心。\n"
            "6. 保存/加载 LPL：生成或导入播放列表文件。\n"
            "7. 添加缩略图：打开缩略图目录，放置对应图片（文件名匹配 ROM 名称）。\n"
            "8. 复制名称：复制选中 ROM 名称到剪贴板，便于搜索缩略图。\n\n"
            "开源声明：本软件开源，可自行修改，不得商用。请保留原作者署名（@爱折腾的老家伙）。"
        )
        messagebox.showinfo("帮助与说明", help_text)

    # --- 新增复制 ROM 名称到剪贴板函数 ---
    def copy_rom_name():
        sel = rom_detail.curselection()
        if not sel:
            messagebox.showwarning("警告", "请先选中一个 ROM！")
            return
        idx = sel[0]
        if idx >= len(rom_list):
            return
        name = rom_list[idx]['label']
        root.clipboard_clear()
        root.clipboard_append(name)
        messagebox.showinfo("成功", f"已复制 ROM 名称到剪贴板：\n{name}")

    # **事件绑定**
    rom_detail.bind('<<ListboxSelect>>', sync_selection_and_refresh)
    rom_detail.bind('<Double-1>', lambda e: edit_rom_path(rom_detail.curselection()))
    
    # ------------------ 窗口初始化和关闭 ------------------
    root.geometry("1280x800")
    root.resizable(width=False, height=False) 
    
    def on_closing():
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing) 

    # 初始刷新
    on_platform_change() 
    root.mainloop()


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
            messagebox.showerror("依赖错误", "缺少 PIL/Pillow 库。\n请在命令行运行：pip install pillow")
            exit()
        
    try:
        create_gui()
    except Exception as e:
        messagebox.showerror("致命错误", f"程序运行发生致命错误: {e}")