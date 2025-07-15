# -*- coding: utf-8 -*-
"""
Luogu AC Code Downloader GUI
"""

import re
import json
import base64
import pathlib
import threading
import requests
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# ------------------ 业务逻辑（同前，略） ------------------
LANG_EXT = { ... }     # 同上
def extract_fe(html: str) -> dict: ...  # 同上
def download(uid: str, cookies: dict, headers: dict, log, progress): ...  # 同上
# --------------------------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Luogu AC Code Downloader')
        self.geometry('640x480')

        # 下载锁：防止重复点击
        self.download_lock = threading.Lock()

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill='both', expand=True)

        # UID
        ttk.Label(frm, text='UID').grid(row=0, column=0, sticky='w')
        self.uid_var = tk.StringVar(value='xxx')
        ttk.Entry(frm, textvariable=self.uid_var, width=15).grid(row=0, column=1, sticky='w')

        # Cookie 多行
        ttk.Label(frm, text='Cookie（一行一个 key=value）').grid(row=1, column=0, columnspan=2, sticky='w')
        self.cookie_text = tk.Text(frm, height=4, width=60)
        self.cookie_text.grid(row=2, column=0, columnspan=2, pady=5)
        self.cookie_text.insert('1.0', '__client_id=aaa\n_uid=bbb\ngdxidpyhxdE=ccc\nC3VK=ddd')

        # Header 多行
        ttk.Label(frm, text='Header（一行一个 key: value）').grid(row=3, column=0, columnspan=2, sticky='w')
        self.header_text = tk.Text(frm, height=3, width=60)
        self.header_text.grid(row=4, column=0, columnspan=2, pady=5)
        self.header_text.insert('1.0', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0')

        # 进度条
        self.pb = ttk.Progressbar(frm, mode='determinate')
        self.pb.grid(row=5, column=0, columnspan=2, sticky='we', pady=5)

        # 日志区
        ttk.Label(frm, text='日志').grid(row=6, column=0, sticky='w')
        self.log_box = scrolledtext.ScrolledText(frm, height=10, width=70, state='disabled')
        self.log_box.grid(row=7, column=0, columnspan=2, pady=5)

        # 下载按钮
        self.btn = ttk.Button(frm, text='开始下载', command=self.start_download)
        self.btn.grid(row=8, column=0, columnspan=2, pady=10)

    # ------------------ 下载控制 ------------------
    def start_download(self):
        # 加锁，如果锁已被占用说明正在下载
        if not self.download_lock.acquire(blocking=False):
            return

        try:
            uid = self.uid_var.get().strip()
            if not uid:
                raise ValueError('UID 不能为空')
            cookies = dict(line.strip().split('=', 1) for line in self.cookie_text.get('1.0', 'end').strip().splitlines() if line.strip())
            headers = dict(line.strip().split(':', 1) for line in self.header_text.get('1.0', 'end').strip().splitlines() if line.strip())
            headers = {k.strip(): v.strip() for k, v in headers.items()}
        except Exception as e:
            messagebox.showerror('参数错误', str(e))
            self.download_lock.release()
            return

        # UI 置为“下载中”
        self.btn.config(state='disabled', text='下载中…')
        self.log_box.config(state='normal')
        self.log_box.delete('1.0', 'end')
        self.log_box.config(state='disabled')
        self.pb['value'] = 0

        def run():
            try:
                download(uid, cookies, headers, self.log, self.progress)
            except Exception as e:
                self.log(f'错误：{e}\n')
                messagebox.showerror('错误', str(e))
            finally:
                # 恢复按钮
                self.btn.config(state='normal', text='开始下载')
                self.download_lock.release()

        threading.Thread(target=run, daemon=True).start()

    # ------------------ UI 辅助 ------------------
    def log(self, msg):
        self.log_box.config(state='normal')
        self.log_box.insert('end', msg)
        self.log_box.see('end')
        self.log_box.config(state='disabled')
        self.update()

    def progress(self, frac):
        self.pb['value'] = frac * 100
        self.update()

if __name__ == '__main__':
    App().mainloop()