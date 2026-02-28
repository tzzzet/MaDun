#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import font as tkfont
import json, os, re, sys
from datetime import date

# 防止重复打开：用锁文件
_lock_file = os.path.expanduser('~/Desktop/码盾MADUN/.settings.lock')
try:
    if os.path.exists(_lock_file):
        # 检查锁文件里的 PID 是否还在运行
        with open(_lock_file) as _f:
            _old_pid = int(_f.read().strip())
        import signal
        os.kill(_old_pid, 0)  # 进程存在则不抛异常
        # 进程还在，退出
        sys.exit(0)
except (ProcessLookupError, ValueError, OSError):
    pass  # 进程不存在，继续启动

# 写入当前 PID
with open(_lock_file, 'w') as _f:
    _f.write(str(os.getpid()))

import atexit
atexit.register(lambda: os.path.exists(_lock_file) and os.remove(_lock_file))

LOG_FILE    = os.path.expanduser('~/Desktop/码盾MADUN/dataguard_log.txt')
CONFIG_FILE = os.path.expanduser('~/Desktop/码盾MADUN/dataguard_config.json')

C = {
    'bg':      '#0a0a0f', 'surface': '#111118', 'surface2': '#1a1a24',
    'border':  '#2a2a3a', 'accent':  '#00e5a0', 'accent_d': '#0d2e24',
    'danger':  '#ff4d6d', 'danger_d':'#2e0d16',  'dim':     '#2a2a3a',
    'text':    '#e8e8f0', 'muted':   '#6b6b88',
}

root = tk.Tk()
root.title('码盾 MaDun · 设置')

root.geometry('1060x700')
root.minsize(900, 600)
root.configure(bg=C['bg'])

try:
    FH  = tkfont.Font(family='SF Pro Display', size=26, weight='bold')
    FT  = tkfont.Font(family='SF Pro Display', size=20, weight='bold')
    FB2 = tkfont.Font(family='SF Pro Text',    size=14, weight='bold')
    FB  = tkfont.Font(family='SF Pro Text',    size=13)
    FS  = tkfont.Font(family='SF Pro Text',    size=11)
    FN  = tkfont.Font(family='SF Pro Text',    size=13, weight='bold')
    FM  = tkfont.Font(family='Menlo',          size=12)
    FK  = tkfont.Font(family='Menlo',          size=11)
    FST = tkfont.Font(family='Menlo',          size=24)
except:
    FH=FT=tkfont.Font(size=18,weight='bold')
    FB2=FN=tkfont.Font(size=13,weight='bold')
    FB=tkfont.Font(size=12); FS=tkfont.Font(size=10)
    FM=FK=tkfont.Font(size=11); FST=tkfont.Font(size=20)

# ══ 主布局：save_bar 先占底部，outer 填满剩余空间 ══
save_bar = tk.Frame(root, bg=C['surface2'], pady=12, padx=32,
                    highlightthickness=1, highlightbackground=C['border'])
# save_bar 先注册到底部但不显示（用place隐藏在屏幕外）
# 实际显示时才 pack

outer = tk.Frame(root, bg=C['bg'])
# 用 place 代替 pack，这样 save_bar 也用 place 时互不影响
outer.place(x=0, y=0, relwidth=1, relheight=1)

sidebar = tk.Frame(outer, bg=C['surface'], width=220)
sidebar.pack(side='left', fill='y')
sidebar.pack_propagate(False)
tk.Frame(outer, bg=C['border'], width=1).pack(side='left', fill='y')

# 右侧内容区：所有页面叠放，用 tkraise 切换，零闪烁
right = tk.Frame(outer, bg=C['bg'])
right.pack(side='left', fill='both', expand=True)
right.bind('<Configure>', lambda e: [
    p.place(x=0, y=0, width=e.width, height=e.height)
    for p in page_frames.values() if p.winfo_exists()
] if page_frames else None)

# ══ 侧边栏 ══
logo_box = tk.Frame(sidebar, bg=C['surface'], padx=20, pady=20)
logo_box.pack(fill='x')
icon_f = tk.Frame(logo_box, bg=C['accent'], padx=8, pady=6)
icon_f.pack(anchor='w', pady=(0,10))
tk.Label(icon_f, text='🔒', font=tkfont.Font(size=16), bg=C['accent'], fg='#000').pack()
tk.Label(logo_box, text='码盾 MaDun', font=FT, fg=C['text'], bg=C['surface']).pack(anchor='w')
tk.Label(logo_box, text='v1.0.0  ·  设置面板', font=FS, fg=C['muted'], bg=C['surface']).pack(anchor='w', pady=(2,0))
tk.Frame(sidebar, bg=C['border'], height=1).pack(fill='x')

nav_area = tk.Frame(sidebar, bg=C['surface'], padx=10, pady=14)
nav_area.pack(fill='x')

current_page = [None]
nav_btns = {}
page_frames = {}

def update_nav():
    pid = current_page[0]
    for k,(f,i,l) in nav_btns.items():
        if k == pid:
            f.config(bg=C['accent_d']); i.config(bg=C['accent_d'],fg=C['accent']); l.config(bg=C['accent_d'],fg=C['accent'])
        else:
            f.config(bg=C['surface']); i.config(bg=C['surface'],fg=C['muted']); l.config(bg=C['surface'],fg=C['muted'])

def show_page(pid):
    if current_page[0] == pid:
        return
    current_page[0] = pid
    if pid in page_frames:
        page_frames[pid].tkraise()
    update_nav()

def nav_btn(icon, label, pid):
    f = tk.Frame(nav_area, bg=C['surface'], cursor='hand2')
    f.pack(fill='x', pady=1)
    i = tk.Label(f, text=icon, font=tkfont.Font(size=13), bg=C['surface'], fg=C['muted'], width=2, padx=4, pady=7)
    i.pack(side='left')
    l = tk.Label(f, text=label, font=FN, bg=C['surface'], fg=C['muted'], pady=7)
    l.pack(side='left')
    def on_click(e=None): show_page(pid)
    def on_enter(e):
        if current_page[0] != pid:
            f.config(bg=C['surface2']); i.config(bg=C['surface2']); l.config(bg=C['surface2'])
    def on_leave(e):
        if current_page[0] != pid:
            f.config(bg=C['surface']); i.config(bg=C['surface']); l.config(bg=C['surface'])
    for w in (f,i,l):
        w.bind('<Button-1>', on_click)
        w.bind('<Enter>', on_enter)
        w.bind('<Leave>', on_leave)
    nav_btns[pid] = (f,i,l)

nav_btn('⚙', '基本设置',   'settings')
nav_btn('✅', '白名单管理', 'whitelist')
nav_btn('🔍', '识别规则',   'rules')
nav_btn('📋', '拦截日志',   'log')

tk.Frame(sidebar, bg=C['border'], height=1).pack(fill='x', pady=(8,0))
sc = tk.Frame(sidebar, bg=C['surface2'], padx=14, pady=14)
sc.pack(fill='x', padx=10, pady=10)
sr = tk.Frame(sc, bg=C['surface2']); sr.pack(fill='x')
tk.Label(sr, text='运行状态', font=FS, fg=C['muted'], bg=C['surface2']).pack(side='left')
dot_c = tk.Canvas(sr, width=10, height=10, bg=C['surface2'], highlightthickness=0)
dot_c.create_oval(1,1,9,9, fill=C['accent'], outline='')
dot_c.pack(side='right')
stat_n = tk.Label(sc, text='0', font=FST, fg=C['accent'], bg=C['surface2'])
stat_n.pack(anchor='w', pady=(6,2))
tk.Label(sc, text='今日已拦截次数', font=FS, fg=C['muted'], bg=C['surface2']).pack(anchor='w')

def update_stat():
    try:
        today = date.today().strftime('%Y-%m-%d')
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE,'r',encoding='utf-8') as f:
                n = sum(1 for l in f if '次拦截' in l and today in l)
            stat_n.config(text=str(n))
    except: pass
    root.after(5000, update_stat)
update_stat()

# ══ 工具函数 ══
def make_scroll(parent):
    c = tk.Canvas(parent, bg=C['bg'], highlightthickness=0)
    sb = tk.Scrollbar(parent, orient='vertical', command=c.yview)
    f = tk.Frame(c, bg=C['bg'])
    f.bind('<Configure>', lambda e: c.configure(scrollregion=c.bbox('all')))
    c.create_window((0,0), window=f, anchor='nw')
    c.configure(yscrollcommand=sb.set)
    c.pack(side='left', fill='both', expand=True)
    sb.pack(side='right', fill='y')
    def scroll(e):
        if e.delta:
            d = -1 if e.delta > 0 else 1
        else:
            d = -1 if e.num == 4 else 1
        c.yview_scroll(d, 'units')
    def bind_tree(w):
        w.bind('<MouseWheel>', scroll)
        for ch in w.winfo_children(): bind_tree(ch)
    c.bind('<MouseWheel>', scroll)
    f.bind('<Map>', lambda e: root.after(100, lambda: bind_tree(f)))
    return f

def section(parent, title=None):
    box = tk.Frame(parent, bg=C['surface'], highlightthickness=1, highlightbackground=C['border'])
    box.pack(fill='x', pady=(0,16))
    if title:
        th = tk.Frame(box, bg=C['surface'], padx=20, pady=14); th.pack(fill='x')
        tk.Label(th, text=title.upper(), font=tkfont.Font(size=10,weight='bold'),
                 fg=C['muted'], bg=C['surface']).pack(side='left')
        tk.Frame(box, bg=C['border'], height=1).pack(fill='x')
    return box

def page_hdr(parent, title, sub):
    h = tk.Frame(parent, bg=C['bg']); h.pack(fill='x', padx=48, pady=(32,24))
    tk.Label(h, text=title, font=FH, fg=C['text'], bg=C['bg']).pack(anchor='w')
    tk.Label(h, text=sub, font=FB, fg=C['muted'], bg=C['bg']).pack(anchor='w', pady=(4,0))

_toggle_vars = {}   # cfg_key -> (BooleanVar, draw_func)

def toggle_row(parent, label, desc, cfg_key=None, default=True):
    row = tk.Frame(parent, bg=C['surface'], padx=20, pady=14)
    row.pack(fill='x')
    tk.Frame(parent, bg=C['border'], height=1).pack(fill='x')
    info = tk.Frame(row, bg=C['surface']); info.pack(side='left', fill='x', expand=True)
    tk.Label(info, text=label, font=FB2, fg=C['text'], bg=C['surface']).pack(anchor='w')
    tk.Label(info, text=desc, font=FS, fg=C['muted'], bg=C['surface']).pack(anchor='w', pady=2)
    # 从配置文件读取初始值
    if cfg_key:
        default = cfg.get(cfg_key, default)
    var = tk.BooleanVar(value=default)
    W, H = 50, 28
    tc = tk.Canvas(row, width=W, height=H, bg=C['surface'], highlightthickness=0, cursor='hand2')
    tc.pack(side='right', padx=4)
    def draw(*_):
        v = var.get(); bg = C['accent'] if v else C['dim']; r = H//2
        tc.delete('all')
        tc.create_oval(0,0,H,H,fill=bg,outline='')
        tc.create_oval(W-H,0,W,H,fill=bg,outline='')
        tc.create_rectangle(r,0,W-r,H,fill=bg,outline='')
        p=3; kx = W-H+p if v else p
        tc.create_oval(kx,p,kx+H-p*2,H-p,fill='white',outline='')
    def click(e=None): var.set(not var.get()); draw(); mark_changed()
    tc.bind('<Button-1>', click); info.bind('<Button-1>', click); row.bind('<Button-1>', click)
    row.bind('<Enter>', lambda e: row.config(bg=C['surface2']))
    row.bind('<Leave>', lambda e: row.config(bg=C['surface']))
    draw()
    if cfg_key:
        _toggle_vars[cfg_key] = (var, draw)
    return var

def render_tags(frame, items, is_danger, rm_cb):
    for w in frame.winfo_children(): w.destroy()
    if not items:
        tk.Label(frame, text='暂无', font=FS, fg=C['muted'], bg=C['surface']).pack(anchor='w', pady=4)
        return
    bc = C['danger'] if is_danger else C['accent']
    bgc = C['danger_d'] if is_danger else C['accent_d']
    row = None
    for idx, item in enumerate(items):
        if idx % 3 == 0:
            row = tk.Frame(frame, bg=C['surface']); row.pack(anchor='w', fill='x')
        tf = tk.Frame(row, bg=bgc, highlightthickness=1, highlightbackground=bc)
        tf.pack(side='left', padx=(0,6), pady=3)
        tk.Label(tf, text=item, font=FK, fg=bc, bg=bgc, padx=10, pady=5).pack(side='left')
        xb = tk.Label(tf, text='×', font=FK, fg=C['muted'], bg=bgc, padx=6, pady=5, cursor='hand2')
        xb.pack(side='left')
        xb.bind('<Button-1>', lambda e,i=item: (rm_cb(i), mark_changed()))
        xb.bind('<Enter>', lambda e,x=xb: x.config(fg=C['danger']))
        xb.bind('<Leave>', lambda e,x=xb: x.config(fg=C['muted']))

# ══ 保存栏 ══
save_lbl = tk.Label(save_bar, text='有未保存的更改', font=FB, fg=C['muted'], bg=C['surface2'])
save_lbl.pack(side='left')
_changed = [False]

def _show_save_bar():
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    bh = 56  # save_bar 高度
    save_bar.place(x=0, y=h - bh, width=w, height=bh)
    save_bar.lift()
    # 让 outer 底部留出空间
    outer.place(x=0, y=0, width=w, height=h - bh)

def _hide_save_bar():
    save_bar.place_forget()
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    outer.place(x=0, y=0, width=w, height=h)

def mark_changed():
    if not _changed[0]:
        _changed[0] = True
        _show_save_bar()

# 窗口大小变化时同步更新布局
def _on_resize(e):
    if _changed[0]:
        _show_save_bar()
    else:
        w = root.winfo_width()
        h = root.winfo_height()
        outer.place(x=0, y=0, width=w, height=h)
root.bind('<Configure>', _on_resize)

def load_cfg():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE,'r',encoding='utf-8') as f: return json.load(f)
    except: pass
    return {'trusted_apps':[],'dangerous_apps':[],'rules':[]}

cfg = load_cfg()
trusted_list   = list(cfg.get('trusted_apps',[]))
dangerous_list = list(cfg.get('dangerous_apps',[]))
rules_list     = list(cfg.get('rules',[]))

# 保存原始状态用于放弃
_orig_trusted   = list(trusted_list)
_orig_dangerous = list(dangerous_list)
_orig_rules     = list(rules_list)
_orig_toggles   = {}   # 在页面创建后初始化

def save():
    try:
        new = {'trusted_apps':list(trusted_list),'dangerous_apps':list(dangerous_list),'rules':list(rules_list)}
        for k,(v,_) in _toggle_vars.items():
            new[k] = v.get()
        with open(CONFIG_FILE,'w',encoding='utf-8') as f: json.dump(new,f,ensure_ascii=False,indent=2)
        # 更新原始状态
        _orig_trusted.clear(); _orig_trusted.extend(trusted_list)
        _orig_dangerous.clear(); _orig_dangerous.extend(dangerous_list)
        _orig_rules.clear(); _orig_rules.extend(rules_list)
        for k,(v,_) in _toggle_vars.items():
            _orig_toggles[k] = v.get()
        _changed[0] = False
        # 明显的成功反馈
        save_lbl.config(text='✅  已保存并立即生效！', fg=C['accent'])
        save_bar.config(bg='#0d2e24')
        save_lbl.config(bg='#0d2e24')
        def _after_save():
            _hide_save_bar()
            save_bar.config(bg=C['surface2'])
            save_lbl.config(bg=C['surface2'], text='有未保存的更改', fg=C['muted'])
        root.after(2000, _after_save)
    except Exception as e:
        save_lbl.config(text=f'保存失败：{e}', fg=C['danger'])

def discard():
    global trusted_list, dangerous_list, rules_list
    # 恢复列表
    trusted_list.clear(); trusted_list.extend(_orig_trusted)
    dangerous_list.clear(); dangerous_list.extend(_orig_dangerous)
    rules_list.clear(); rules_list.extend(_orig_rules)
    # 恢复开关到上次保存的状态
    for k,(var,draw) in _toggle_vars.items():
        var.set(_orig_toggles.get(k, var.get()))
        draw()
    _changed[0] = False
    _hide_save_bar()
    # 立即重新渲染所有标签区域
    for refresh in _tag_refreshers:
        refresh()
    render_rules()

tk.Button(save_bar,text='放弃更改',font=FB,bg=C['surface'],fg=C['muted'],relief='flat',
          padx=14,pady=7,cursor='hand2',
          command=discard).pack(side='right',padx=(6,0))
tk.Button(save_bar,text='保存更改',font=FB,bg=C['accent'],fg='#000',relief='flat',
          padx=14,pady=7,cursor='hand2',command=save).pack(side='right')

# ══════════════════════════════
# Page: 基本设置
# ══════════════════════════════
p_s = tk.Frame(right, bg=C['bg'])
page_frames['settings'] = p_s
sp = make_scroll(p_s)
page_hdr(sp, '基本设置', '控制 码盾 的核心行为')
s1w = tk.Frame(sp, bg=C['bg'], padx=48); s1w.pack(fill='x')
s1 = section(s1w, '守护开关')
toggle_row(s1,'启用剪贴板守护','开启后，码盾 将实时监控剪贴板中的敏感信息',cfg_key='guardian_enabled',default=True)
toggle_row(s1,'弹出系统通知','每次拦截后在屏幕右上角显示通知',cfg_key='notify_enabled',default=True)
toggle_row(s1,'记录拦截日志','将拦截记录保存到 dataguard_log.txt',cfg_key='log_enabled',default=True)
toggle_row(s1,'信息熵过滤','自动过滤 sk-xxxx 等示例占位符，减少误报',cfg_key='noise_filter',default=True)
s2 = section(s1w, '检测灵敏度')
toggle_row(s2,'高灵敏度模式','降低熵值门槛，捕获更多可疑内容（可能增加误报）',cfg_key='high_sensitivity',default=False)
toggle_row(s2,'上下文语义分析','检测密钥周围是否有 "example"、"test" 等提示词',cfg_key='context_analysis',default=True)

# ══════════════════════════════
# Page: 白名单
# ══════════════════════════════
p_w = tk.Frame(right, bg=C['bg'])
page_frames['whitelist'] = p_w
wp = make_scroll(p_w)
page_hdr(wp, '白名单管理', '白名单内的应用复制内容不会被拦截')
ww = tk.Frame(wp, bg=C['bg'], padx=48); ww.pack(fill='x')

_tag_refreshers = []  # 收集所有标签区域的刷新函数

def make_tag_section(parent, title, items, is_danger):
    s = section(parent, title)
    tf_wrap = tk.Frame(s, bg=C['surface'], padx=20, pady=12); tf_wrap.pack(fill='x')
    tf = tk.Frame(tf_wrap, bg=C['surface']); tf.pack(fill='x', pady=(0,8))
    ph = 'com.apple.example' if not is_danger else 'com.google.Chrome'
    def rm(item):
        if item in items:
            items.remove(item)
        render_tags(tf, items, is_danger, rm)
        mark_changed()
    def refresh():
        render_tags(tf, items, is_danger, rm)
    _tag_refreshers.append(refresh)
    render_tags(tf, items, is_danger, rm)
    add_row = tk.Frame(s, bg=C['surface']); add_row.pack(fill='x', padx=20, pady=(4,16))
    e = tk.Entry(add_row, font=FM, bg=C['surface2'], fg=C['text'], insertbackground=C['text'],
                 relief='flat', highlightthickness=1, highlightbackground=C['border'])
    e.pack(side='left', fill='x', expand=True, ipady=8, padx=(0,8))
    e.insert(0, ph)
    e.bind('<FocusIn>', lambda ev: e.select_range(0,'end'))
    bc = C['danger'] if is_danger else C['accent']
    def add(ev=None):
        v = e.get().strip()
        if v and v not in items and v != ph:
            items.append(v); render_tags(tf, items, is_danger, rm)
            e.delete(0,'end'); e.insert(0, ph); mark_changed()
    tk.Button(add_row, text='+ 添加', font=FB, bg=bc, fg='#000' if not is_danger else '#fff',
              relief='flat', padx=12, pady=6, cursor='hand2', command=add).pack(side='left')
    e.bind('<Return>', add)

make_tag_section(ww, '白名单应用', trusted_list, False)
make_tag_section(ww, '高危出口（会升级警告级别）', dangerous_list, True)

# ══════════════════════════════
# Page: 识别规则
# ══════════════════════════════
p_r = tk.Frame(right, bg=C['bg'])
page_frames['rules'] = p_r
rp = make_scroll(p_r)
page_hdr(rp, '识别规则', '定义码盾检测和拦截的内容模式')
rw = tk.Frame(rp, bg=C['bg'], padx=48); rw.pack(fill='x')
s_rules = section(rw, '当前规则')
ri = tk.Frame(s_rules, bg=C['surface']); ri.pack(fill='x', padx=20, pady=8)

def render_rules():
    for w in ri.winfo_children(): w.destroy()
    if not rules_list:
        tk.Label(ri, text='暂无规则', font=FS, fg=C['muted'], bg=C['surface']).pack(pady=12); return
    for idx, r in enumerate(rules_list):
        name = r[1] if len(r)>1 else r[0]
        row = tk.Frame(ri, bg=C['surface'], pady=10); row.pack(fill='x')
        tk.Frame(ri, bg=C['border'], height=1).pack(fill='x')
        tk.Label(row, text=str(idx+1).zfill(2), font=FM, fg=C['dim'], bg=C['surface'], width=3).pack(side='left')
        tk.Label(row, text=name, font=FB2, fg=C['text'], bg=C['surface']).pack(side='left', padx=12)
        patt = r[0][:50]+('…' if len(r[0])>50 else '')
        tk.Label(row, text=patt, font=FK, fg=C['muted'], bg=C['surface']).pack(side='left')
        xb = tk.Label(row, text='✕', font=FB, fg=C['muted'], bg=C['surface'], cursor='hand2')
        xb.pack(side='right', padx=8)
        xb.bind('<Button-1>', lambda e,i=idx: (rules_list.pop(i), render_rules(), mark_changed()))
        xb.bind('<Enter>', lambda e,x=xb: x.config(fg=C['danger']))
        xb.bind('<Leave>', lambda e,x=xb: x.config(fg=C['muted']))
render_rules()

# ══════════════════════════════
# Page: 拦截日志
# ══════════════════════════════
p_l = tk.Frame(right, bg=C['bg'])
page_frames['log'] = p_l

log_top = tk.Frame(p_l, bg=C['bg']); log_top.pack(fill='x', padx=48, pady=(32,12))
tr = tk.Frame(log_top, bg=C['bg']); tr.pack(fill='x')
tk.Label(tr, text='拦截日志', font=FH, fg=C['text'], bg=C['bg']).pack(side='left')
cnt_lbl = tk.Label(tr, text='', font=FS, fg=C['muted'], bg=C['bg'])
cnt_lbl.pack(side='right', pady=10)
tk.Label(log_top, text='码盾本次运行的拦截记录', font=FB, fg=C['muted'], bg=C['bg']).pack(anchor='w', pady=(4,0))

hdr = tk.Frame(p_l, bg=C['surface'], padx=24, pady=12,
               highlightthickness=1, highlightbackground=C['border'])
hdr.pack(fill='x', padx=48)
tk.Label(hdr,text='时间',font=tkfont.Font(size=10,weight='bold'),fg=C['muted'],bg=C['surface'],width=10,anchor='w').pack(side='left')
tk.Label(hdr,text='类型',font=tkfont.Font(size=10,weight='bold'),fg=C['muted'],bg=C['surface'],width=14,anchor='w').pack(side='left',padx=8)
tk.Label(hdr,text='来源应用',font=tkfont.Font(size=10,weight='bold'),fg=C['muted'],bg=C['surface'],anchor='w').pack(side='left',fill='x',expand=True)
tk.Label(hdr,text='风险等级',font=tkfont.Font(size=10,weight='bold'),fg=C['muted'],bg=C['surface'],width=12,anchor='e').pack(side='right')

log_wrap = tk.Frame(p_l, bg=C['bg']); log_wrap.pack(fill='both', expand=True, padx=48)
log_cv = tk.Canvas(log_wrap, bg=C['bg'], highlightthickness=0)
log_sb = tk.Scrollbar(log_wrap, orient='vertical', command=log_cv.yview)
log_body = tk.Frame(log_cv, bg=C['bg'])
log_body.bind('<Configure>', lambda e: log_cv.configure(scrollregion=log_cv.bbox('all')))
log_cv.create_window((0,0), window=log_body, anchor='nw')
log_cv.configure(yscrollcommand=log_sb.set)
log_cv.pack(side='left', fill='both', expand=True)
log_sb.pack(side='right', fill='y')

def log_scroll(e):
    if e.delta:
        d = -1 if e.delta > 0 else 1
    else:
        d = -1 if e.num == 4 else 1
    log_cv.yview_scroll(d, 'units')
def bind_log(w):
    w.bind('<MouseWheel>', log_scroll)
    for ch in w.winfo_children(): bind_log(ch)
log_cv.bind('<MouseWheel>', log_scroll)

_last_log_len = [-1]
def refresh_log():
    try:
        entries = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE,'r',encoding='utf-8') as f:
                for line in f:
                    if '次拦截' not in line: continue
                    tm=re.search(r'\[(\d{4}-\d{2}-\d{2} (\d{2}:\d{2}:\d{2}))\]',line)
                    ty=re.search(r'类型:([^|\n]+)',line)
                    ap=re.search(r'来源[:：]\s*(\S+)',line)
                    ri=re.search(r'(🔴 高危出口|🟡 普通应用)',line)
                    if tm: entries.append({
                        'time':tm.group(2),'type':ty.group(1).strip() if ty else '未知',
                        'app':ap.group(1).strip() if ap else '未知',
                        'high':bool(ri and '高危' in ri.group(1)),
                        'risk':ri.group(1) if ri else '🟡 普通应用'
                    })
        if len(entries) != _last_log_len[0]:
            _last_log_len[0] = len(entries)
            for w in log_body.winfo_children(): w.destroy()
            cnt_lbl.config(text=f'共 {len(entries)} 条记录  ·  最新在上')
            for en in reversed(entries[-200:]):
                rb = C['danger_d'] if en['high'] else C['surface']
                rbl= C['danger']   if en['high'] else C['border']
                row = tk.Frame(log_body,bg=rb,padx=24,pady=12,
                               highlightthickness=1,highlightbackground=rbl)
                row.pack(fill='x',pady=1)
                tk.Label(row,text=en['time'],font=FM,fg=C['muted'],bg=rb,width=10,anchor='w').pack(side='left')
                tbg=C['danger_d'] if en['high'] else C['accent_d']
                tfg=C['danger']   if en['high'] else C['accent']
                tf=tk.Frame(row,bg=tbg,highlightthickness=1,highlightbackground=tfg)
                tf.pack(side='left',padx=8)
                tk.Label(tf,text=en['type'],font=FK,fg=tfg,bg=tbg,padx=8,pady=3).pack()
                tk.Label(row,text=en['app'],font=FM,fg=C['text'],bg=rb).pack(side='left',fill='x',expand=True)
                tk.Label(row,text=en['risk'],font=FS,
                         fg=C['danger'] if en['high'] else C['accent'],
                         bg=rb,width=14,anchor='e').pack(side='right')
            if not entries:
                ef=tk.Frame(log_body,bg=C['surface'],padx=24,pady=40,
                            highlightthickness=1,highlightbackground=C['border'])
                ef.pack(fill='x',pady=1)
                tk.Label(ef,text='暂无拦截记录',font=FB2,fg=C['muted'],bg=C['surface']).pack()
                tk.Label(ef,text='当 码盾 拦截到敏感内容时，记录会出现在这里',
                         font=FS,fg=C['dim'],bg=C['surface']).pack(pady=(4,0))
            bind_log(log_body)
    except: pass
    root.after(3000, refresh_log)

refresh_log()

btn_row = tk.Frame(p_l, bg=C['bg'], padx=48, pady=8); btn_row.pack(fill='x')
tk.Button(btn_row,text='🔄  刷新',font=FB,bg=C['surface2'],fg=C['muted'],relief='flat',
          padx=14,pady=7,cursor='hand2',command=refresh_log).pack(side='right',padx=(8,0))
tk.Button(btn_row,text='🗑  清空日志',font=FB,bg=C['surface2'],fg=C['muted'],relief='flat',
          padx=14,pady=7,cursor='hand2',
          command=lambda:(open(LOG_FILE,'w').close() if os.path.exists(LOG_FILE) else None,
                          _last_log_len.__setitem__(0,-1), refresh_log())).pack(side='right')

# ══ 初始化：所有页面叠放，显示日志页 ══
def init_pages():
    # outer 用 place 撑满
    rw = root.winfo_width() or 1060
    rh = root.winfo_height() or 700
    outer.place(x=0, y=0, width=rw, height=rh)
    # 页面叠放
    w = right.winfo_width() or 840
    h = right.winfo_height() or 700
    for p in page_frames.values():
        p.place(x=0, y=0, width=w, height=h)
    # 记录开关初始状态
    for k,(v,_) in _toggle_vars.items():
        _orig_toggles[k] = v.get()
    current_page[0] = 'log'
    page_frames['log'].tkraise()
    update_nav()

root.after(50, init_pages)

root.mainloop()
