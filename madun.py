#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
码盾 MaDun - 剪贴板隐私守卫 v1.3
新增:菜单栏图标 + 双击自动打开设置界面
"""

import time
import re
import subprocess
import json
import math
import os
import threading
import rumps
from datetime import datetime

# ──────────────────────────────────────────────
# 路径配置（兼容打包后的 App）
# ──────────────────────────────────────────────
import sys

def get_base_dir():
    """
    打包后 PyInstaller 会把文件解压到 sys._MEIPASS 
    直接运行时用脚本所在目录.
    """
    if getattr(sys, 'frozen', False):
        # 打包后：资源文件在 sys._MEIPASS
        return sys._MEIPASS
    # 直接运行：用脚本所在目录
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR      = get_base_dir()
CONFIG_FILE   = os.path.join(os.path.expanduser('~/Desktop/码盾MADUN'), 'dataguard_config.json')
# 日志固定写到用户桌面的码盾MADUN文件夹 确保用户能找到
_log_dir = os.path.expanduser('~/Desktop/码盾MADUN')
os.makedirs(_log_dir, exist_ok=True)
LOG_FILE = os.path.join(_log_dir, 'dataguard_log.txt')
SETTINGS_FILE = os.path.join(BASE_DIR, 'dataguard_settings.html')

UNDO_WINDOW       = 30
RE_SANITIZE_DELAY = 5

# ──────────────────────────────────────────────
# 默认配置
# ──────────────────────────────────────────────
DEFAULT_CONFIG = {
    "trusted_apps": [
        "com.microsoft.VSCode",
        "com.apple.dt.Xcode",
        "com.jetbrains.intellij",
        "com.sublimetext.4",
        "com.googlecode.iterm2",
        "com.apple.Terminal",
    ],
    "dangerous_apps": [
        "com.google.Chrome",
        "com.apple.Safari",
        "com.tencent.xinWeChat",
        "com.tinyspeck.slackmacgap",
        "com.openai.chat",
    ],
    "rules": [
        ["sk-[a-zA-Z0-9]{32,}",               "OpenAI 密钥"],
        ["sk-proj-[a-zA-Z0-9\\-_]{32,}",      "OpenAI 项目密钥"],
        ["(AKIA|AGPA|AROA|ASIA)[A-Z0-9]{16}", "AWS 访问密钥"],
        ["gh[pousr]_[a-zA-Z0-9]{36,}",        "GitHub Token"],
        ["xox[baprs]-[a-zA-Z0-9\\-]{10,}",   "Slack Token"],
        ["AIza[0-9A-Za-z\\-_]{35}",           "Google API 密钥"],
        ["\\bSecret_[a-zA-Z0-9_]+",           "私有函数标识"],
        ["\\b_internal_[a-zA-Z0-9_]+",        "内部函数标识"],
    ]
}

# ──────────────────────────────────────────────
# 撤销管理器
# ──────────────────────────────────────────────
class UndoManager:
    def __init__(self):
        self.lock             = threading.Lock()
        self.original         = None
        self.timer            = None
        self.resanitize_timer = None
        self.rules            = []
        self.last_content_ref = [None]

    def save(self, original_text, rules, last_content_ref):
        with self.lock:
            if self.timer:
                self.timer.cancel()
            if self.resanitize_timer:
                self.resanitize_timer.cancel()
            self.original         = original_text
            self.rules            = rules
            self.last_content_ref = last_content_ref
            self.timer = threading.Timer(UNDO_WINDOW, self._expire)
            self.timer.daemon = True
            self.timer.start()

    def _expire(self):
        with self.lock:
            self.original = None
        log('🗑️  撤销窗口已过期 原始内容已从内存清除')

    def undo(self):
        with self.lock:
            if not self.original:
                return False
            set_clipboard(self.original)
            self.last_content_ref[0] = self.original
            if self.timer:
                self.timer.cancel()
            original_copy = self.original
            self.original = None
            self.resanitize_timer = threading.Timer(
                RE_SANITIZE_DELAY, self._re_sanitize, args=[original_copy]
            )
            self.resanitize_timer.daemon = True
            self.resanitize_timer.start()
            return True

    def _re_sanitize(self, original_text):
        current = get_clipboard()
        if current.strip() == original_text.strip():
            cleaned, secret_type = sanitize(original_text, self.rules)
            if cleaned:
                set_clipboard(cleaned)
                self.last_content_ref[0] = cleaned
                log(f'🔄 撤销后用户未粘贴 已重新净化 | {secret_type}')
                send_notification('🔒 码盾 已重新净化', f'{secret_type} 仍在剪贴板 已再次自动净化')

# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────
def get_clipboard():
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True, timeout=2)
        return result.stdout
    except Exception:
        return ''

def set_clipboard(text):
    try:
        subprocess.run(['pbcopy'], input=text, text=True, timeout=2)
    except Exception:
        pass

def get_frontmost_app():
    script = '''
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        return bundle identifier of frontApp
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=3)
        return result.stdout.strip()
    except Exception:
        return ''

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{timestamp}] {message}'
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass

def send_notification(title, message):
    script = f'display notification "{message}" with title "{title}" sound name "Purr"'
    try:
        subprocess.run(['osascript', '-e', script], timeout=3)
    except Exception:
        pass

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CONFIG

FAKE_HINTS = ['xxxx', 'your', 'example', 'test', 'fake', 'dummy',
              'placeholder', 'YOUR_', 'REPLACE', '示例', '替换']

def is_placeholder(text):
    return any(h.lower() in text.lower() for h in FAKE_HINTS)

def calculate_entropy(s):
    if not s:
        return 0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    entropy = 0
    for count in freq.values():
        p = count / len(s)
        entropy -= p * math.log2(p)
    return entropy

def sanitize(text, rules):
    for pattern, name in rules:
        try:
            matches = re.findall(pattern, text)
        except re.error:
            continue
        if not matches:
            continue
        real_matches = []
        for match in matches:
            matched_str = match if isinstance(match, str) else (match[0] if match else '')
            if not matched_str or is_placeholder(matched_str):
                continue
            if '函数' not in name and '标识' not in name:
                if calculate_entropy(matched_str) < 3.2:
                    continue
            real_matches.append(matched_str)
        if real_matches:
            cleaned = text
            for m in real_matches:
                cleaned = cleaned.replace(m, f'[{name}·已脱敏]')
            return cleaned, name
    return None, None

def show_undo_dialog(secret_type, undo_manager, on_close=None):
    def _dialog():
        script = f'''
        tell application "System Events"
            activate
            set result to display dialog "码盾检测到 {secret_type} 剪贴板已自动净化。\\n\\n如需恢复原始内容 请在 {UNDO_WINDOW} 秒内点击【撤销净化】。" ¬
                buttons {{"忽略", "撤销净化"}} ¬
                default button "忽略" ¬
                with title "🔒 码盾 MaDun" ¬
                giving up after {UNDO_WINDOW}
            return button returned of result
        end tell
        '''
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True, text=True, timeout=UNDO_WINDOW + 5
            )
            if result.stdout.strip() == '撤销净化':
                success = undo_manager.undo()
                if success:
                    log('↩️  用户撤销净化 原始内容已恢复')
                    send_notification('↩️ 码盾 已撤销', f'原始内容已恢复 请在 {RE_SANITIZE_DELAY} 秒内完成粘贴')
                else:
                    send_notification('⚠️ 码盾', '撤销窗口已过期 无法恢复')
        except Exception:
            pass
        finally:
            # 弹窗关闭后才释放锁
            if on_close:
                on_close()
    threading.Thread(target=_dialog, daemon=True).start()

_settings_proc = [None]  # 记录设置窗口进程

def _find_python():
    """找到一个带 tkinter 的 Python 解释器，优先 pythonw（不显示 Dock 图标）"""
    if not getattr(sys, 'frozen', False):
        # 直接运行时：用 pythonw（同目录）或自身
        pythonw = sys.executable.replace('python3', 'pythonw').replace('python', 'pythonw')
        if os.path.exists(pythonw):
            return pythonw
        return sys.executable

    # 打包后：找带 tkinter 的 python3
    candidates = []
    # 先从 which/PATH 找
    try:
        r = subprocess.run(['which', 'python3'], capture_output=True, text=True)
        which = r.stdout.strip()
        if which:
            candidates.append(which)
    except Exception:
        pass
    # Python.framework（官网安装包）
    import glob
    for p in sorted(glob.glob('/Library/Frameworks/Python.framework/Versions/*/bin/python3'), reverse=True):
        candidates.append(p)
    # Homebrew
    candidates += [
        '/opt/homebrew/bin/python3',
        '/usr/local/bin/python3',
        os.path.expanduser('~/.pyenv/shims/python3'),
        os.path.expanduser('~/anaconda3/bin/python3'),
        os.path.expanduser('~/miniconda3/bin/python3'),
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                r = subprocess.run([p, '-c', 'import tkinter'], capture_output=True, timeout=3)
                if r.returncode == 0:
                    # 优先用同目录的 pythonw，避免 Dock 显示 Python 图标
                    import glob as _glob
                    pw = p.replace('python3', 'pythonw').replace('python', 'pythonw')
                    # 避免把 pythonw 变成 pythonww
                    pw = pw.replace('pythonww', 'pythonw')
                    if os.path.exists(pw):
                        return pw
                    # Python.framework 里找 pythonw
                    ver_dir = os.path.dirname(p)
                    for pw2 in _glob.glob(os.path.join(ver_dir, 'pythonw*')):
                        return pw2
                    return p
            except Exception:
                continue
    return None

def open_settings():
    """用独立子进程打开设置窗口，防止重复打开"""
    if _settings_proc[0] is not None and _settings_proc[0].poll() is None:
        log('设置窗口已在运行')
        return

    src = os.path.join(BASE_DIR, 'settings_window.py')
    dest = os.path.join(os.path.expanduser('~/Desktop/码盾MADUN'), '_settings_window.py')

    try:
        import shutil
        if os.path.exists(src):
            shutil.copy2(src, dest)
        if not os.path.exists(dest):
            send_notification('⚠️ 码盾', '找不到设置窗口文件')
            return

        python = _find_python()
        if not python:
            send_notification('⚠️ 码盾', '找不到可用的 Python，请确认已安装 Python 3')
            log('打开设置失败: 找不到带 tkinter 的 Python')
            return

        if getattr(sys, 'frozen', False):
            # 打包后：用独立的「码盾设置.app」，有码盾图标
            # 路径：dist/码盾设置.app 和 dist/码盾MaDun.app 同目录
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
            settings_app = os.path.join(app_dir, '码盾设置.app')
            if os.path.exists(settings_app):
                log(f'打包模式，使用设置App: {settings_app}')
                def _run():
                    p = subprocess.Popen(['open', '-n', settings_app])
                    p.wait()
                threading.Thread(target=_run, daemon=True).start()
                return
            log(f'找不到设置App: {settings_app}，降级使用 Python')

        log(f'使用 Python: {python}')

        def _run():
            _settings_proc[0] = subprocess.Popen([python, dest])
            _settings_proc[0].wait()
        threading.Thread(target=_run, daemon=True).start()
    except Exception as e:
        log(f'打开设置失败: {e}')


# ──────────────────────────────────────────────
# 菜单栏 App
# ──────────────────────────────────────────────
class MaDunApp(rumps.App):
    def __init__(self):
        super().__init__(name='码盾 MaDun', title='🔒', quit_button=None)

        self.guardian_enabled = True
        self.intercepting = False  # 防重复拦截标志
        self.intercept_count  = self._count_today_intercepts()
        self.undo_manager     = UndoManager()
        self.last_content     = [get_clipboard()]
        self.config           = load_config()
        self.config_mtime     = os.path.getmtime(CONFIG_FILE) if os.path.exists(CONFIG_FILE) else 0

        # 菜单项
        self.status_item    = rumps.MenuItem('状态：守护中 ✅')
        self.count_item     = rumps.MenuItem(f'今日拦截：{self.intercept_count} 次')
        self.toggle_item    = rumps.MenuItem('⏸  暂停守护', callback=self.toggle_guardian)
        self.startup_item   = rumps.MenuItem('🚀  开机自启：已开启', callback=self.toggle_startup)
        self.settings_item  = rumps.MenuItem('⚙️  打开设置', callback=self.open_settings_clicked)
        self.log_item       = rumps.MenuItem('📋  查看日志', callback=self.open_log_clicked)
        self.quit_item      = rumps.MenuItem('退出码盾', callback=self.quit_app)

        self.menu = [
            self.status_item,
            self.count_item,
            None,
            self.settings_item,
            self.log_item,
            None,
            self.toggle_item,
            self.startup_item,
            None,
            self.quit_item,
        ]

        # 监听下载目录 自动同步配置文件
        threading.Thread(target=self.watch_downloads, daemon=True).start()

        # 注册开机自启
        self.register_login_item()

        # 启动后台监控线程
        threading.Thread(target=self.guardian_loop, daemon=True).start()

    def _count_today_intercepts(self):
        """从日志文件统计今日拦截次数"""
        try:
            from datetime import date
            today = date.today().strftime('%Y-%m-%d')
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    return sum(1 for l in f if '次拦截' in l and today in l)
        except Exception:
            pass
        return 0

    def export_log_json(self):
        """把拦截日志解析成 JSON 写到码盾MADUN文件夹 供设置界面读取"""
        try:
            import json as _json, re as _re
            entries = []
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '次拦截' not in line:
                            continue
                        time_m = _re.search(r'\[(\d{4}-\d{2}-\d{2} (\d{2}:\d{2}:\d{2}))\]', line)
                        type_m = _re.search(r'类型:([^|\n]+)', line) or _re.search(r'拦截\s*\|\s*([^|]+?)\s*\|', line)
                        app_m  = _re.search(r'来源[:：]\s*(\S+)', line) or _re.search(r'\|\s*(com\.\S+)\s*$', line)
                        risk_m = _re.search(r'(🔴 高危出口|🟡 普通应用)', line)
                        if time_m:
                            entries.append({
                                'time': time_m.group(2),
                                'type': type_m.group(1).strip() if type_m else '未知类型',
                                'detail': '已自动净化并替换为脱敏标记',
                                'app': app_m.group(1).strip() if app_m else '未知来源',
                                'risk': risk_m.group(1) if risk_m else '🟡 普通应用',
                            })
            # 写到桌面码盾MADUN文件夹（可写）
            json_path = os.path.join(os.path.expanduser('~/Desktop/码盾MADUN'), 'dataguard_log.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                _json.dump(entries, f, ensure_ascii=False)
        except Exception as e:
            log(f'日志导出失败: {e}')

    def _reset_intercepting(self):
        self.intercepting = False

    def watch_downloads(self):
        """监听下载目录 发现新的 dataguard_config*.json 自动同步"""
        import shutil
        import glob
        downloads_dir = os.path.expanduser('~/Downloads')
        last_synced = {}  # 记录已同步的文件和时间

        while True:
            try:
                # 匹配所有 dataguard_config*.json 文件
                pattern = os.path.join(downloads_dir, 'dataguard_config*.json')
                files = glob.glob(pattern)

                for f in files:
                    mtime = os.path.getmtime(f)
                    # 只处理新文件（5分钟内下载的 且未同步过）
                    import time as _time
                    if _time.time() - mtime < 300 and last_synced.get(f) != mtime:
                        last_synced[f] = mtime
                        shutil.copy2(f, CONFIG_FILE)
                        log(f'✅ 检测到新配置文件 {os.path.basename(f)} 已自动同步')
                        send_notification('✅ 码盾 配置已更新', '设置已自动同步并立即生效！')
            except Exception as e:
                pass
            time.sleep(1)

    def register_login_item(self):
        """注册开机自启(仅在打包后的 App 中生效)"""
        if not getattr(sys, 'frozen', False):
            return  # 直接运行 python3 时不注册
        try:
            # 从 sys.executable 往上找 直到找到 .app 结尾的路径
            path = os.path.dirname(sys.executable)
            app_path = None
            for _ in range(6):
                if path.endswith('.app'):
                    app_path = path
                    break
                path = os.path.dirname(path)
            
            log(f'App路径：{app_path}')
            if not app_path or not app_path.endswith('.app'):
                log(f'⚠️  找不到.app路径 跳过注册')
                return
            script = f'''
            tell application "System Events"
                set appPath to "{app_path}"
                set alreadyAdded to false
                repeat with loginItem in (every login item)
                    if path of loginItem is appPath then
                        set alreadyAdded to true
                        exit repeat
                    end if
                end repeat
                if not alreadyAdded then
                    make new login item at end with properties {{path:appPath, hidden:true}}
                    return "added"
                else
                    return "exists"
                end if
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], timeout=5, capture_output=True, text=True)
            status = result.stdout.strip()
            if status == 'added':
                log('✅ 已自动注册开机自启')
            elif status == 'exists':
                log('ℹ️  开机自启已存在 无需重复注册')
            else:
                log(f'⚠️  注册结果未知：{result.stderr}')
        except Exception as e:
            log(f'⚠️  开机自启注册失败：{e}')

    def guardian_loop(self):
        while True:
            try:
                # 热重载配置
                if os.path.exists(CONFIG_FILE):
                    mtime = os.path.getmtime(CONFIG_FILE)
                    if mtime != self.config_mtime:
                        self.config_mtime = mtime
                        self.config = load_config()
                        # 同步开关状态
                        if not self.config.get('guardian_enabled', True):
                            self.guardian_enabled = False
                            self.status_item.title = '状态：已暂停 ⏸'
                            self.title = '🔓'
                        else:
                            self.guardian_enabled = True
                            self.status_item.title = '状态：守护中 ✅'
                            self.title = '🔒'
                        log('🔄 配置热重载完成')

                if not self.guardian_enabled:
                    time.sleep(0.5)
                    continue

                current = get_clipboard()
                if current == self.last_content[0] or not current.strip():
                    time.sleep(0.5)
                    continue

                self.last_content[0] = current

                trusted_apps = self.config.get('trusted_apps', DEFAULT_CONFIG['trusted_apps'])
                front_app = get_frontmost_app()
                if front_app in trusted_apps:
                    time.sleep(0.5)
                    continue

                rules = self.config.get('rules', DEFAULT_CONFIG['rules'])
                cleaned, secret_type = sanitize(current, rules)

                if cleaned and not self.intercepting:
                    self.intercepting = True
                    # 立即更新 last_content 为净化后内容 防止循环重复检测
                    self.last_content[0] = cleaned
                    self.undo_manager.save(current, rules, self.last_content)
                    set_clipboard(cleaned)
                    self.intercept_count += 1

                    dangerous_apps = self.config.get('dangerous_apps', DEFAULT_CONFIG['dangerous_apps'])
                    risk_tag = '🔴 高危出口' if front_app in dangerous_apps else '🟡 普通应用'
                    app_label = front_app if front_app else '未知应用'
                    log(f'⚠️  第{self.intercept_count}次拦截 | 类型:{secret_type} | {risk_tag} | 来源:{app_label}')

                    # 更新菜单栏拦截次数
                    self.count_item.title = f'今日拦截：{self.intercept_count} 次'

                    # 导出日志 JSON 供设置界面读取
                    self.export_log_json()

                    show_undo_dialog(secret_type, self.undo_manager, on_close=self._reset_intercepting)

            except Exception as e:
                log(f'[错误] {e}')

            time.sleep(0.5)

    def open_settings_clicked(self, _):
        open_settings()

    def open_log_clicked(self, _):
        """用 rumps 原生窗口显示拦截日志"""
        import re as _re
        entries = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '次拦截' not in line:
                        continue
                    time_m = _re.search(r'\[(\d{4}-\d{2}-\d{2} (\d{2}:\d{2}:\d{2}))\]', line)
                    type_m = _re.search(r'类型:([^|\n]+)', line)
                    app_m  = _re.search(r'来源[:：]\s*(\S+)', line)
                    risk_m = _re.search(r'(🔴 高危出口|🟡 普通应用)', line)
                    if time_m:
                        t = time_m.group(2)
                        typ = type_m.group(1).strip() if type_m else '未知'
                        app = app_m.group(1).strip() if app_m else '未知'
                        risk = '🔴' if risk_m and '高危' in risk_m.group(1) else '🟡'
                        entries.append(f'{risk} {t}  {typ}  ({app})')

        if entries:
            # 显示最近20条
            recent = entries[-20:]
            recent.reverse()
            msg = f'最近 {len(recent)} 条拦截记录（共 {len(entries)} 条）：\n\n' + '\n'.join(recent)
        else:
            msg = '暂无拦截记录'

        rumps.alert(title='📋 码盾 拦截日志', message=msg, ok='关闭')

    def toggle_guardian(self, sender):
        self.guardian_enabled = not self.guardian_enabled
        if self.guardian_enabled:
            sender.title          = '⏸  暂停守护'
            self.status_item.title = '状态：守护中 ✅'
            self.title            = '🔒'
            log('▶️  守护已恢复')
        else:
            sender.title          = '▶️  恢复守护'
            self.status_item.title = '状态：已暂停 ⏸'
            self.title            = '🔓'
            log('⏸  守护已暂停')

    def toggle_startup(self, sender):
        """开关开机自启"""
        if not getattr(sys, 'frozen', False):
            send_notification('码盾', '请使用打包后的 App 来管理开机自启')
            return
        try:
            path = os.path.dirname(sys.executable)
            app_path = None
            for _ in range(6):
                if path.endswith('.app'):
                    app_path = path
                    break
                path = os.path.dirname(path)
            if not app_path:
                return
            if '开启' in sender.title:
                # 关闭开机自启
                script = f'''
                tell application "System Events"
                    set loginItems to every login item
                    repeat with loginItem in loginItems
                        if path of loginItem is "{app_path}" then
                            delete loginItem
                        end if
                    end repeat
                end tell
                '''
                subprocess.run(['osascript', '-e', script], timeout=5, capture_output=True)
                sender.title = '🚀  开机自启：已关闭'
                log('⏹  已关闭开机自启')
            else:
                # 开启开机自启
                script = f'''
                tell application "System Events"
                    make new login item at end with properties {{path:"{app_path}", hidden:true}}
                end tell
                '''
                subprocess.run(['osascript', '-e', script], timeout=5, capture_output=True)
                sender.title = '🚀  开机自启：已开启'
                log('✅  已开启开机自启')
        except Exception as e:
            log(f'开机自启切换失败：{e}')

    def quit_app(self, _):
        log(f'👋 码盾 已退出 本次共拦截 {self.intercept_count} 次')
        rumps.quit_application()


if __name__ == '__main__':
    MaDunApp().run()
