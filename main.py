import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
from hanime_xf_info import get_hanime_xfyg_info
from download_nfo_img import sc_nfo_jpg
from download_move import db_get_lfid, download_html
import os
import threading

class GUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hanime1里番下载器")
        self.root.geometry("730x485")
        # 锁定窗口大小（宽、高都不能改变）
        self.root.resizable(False, False)

        # 创建输入组件
        root.columnconfigure((0,1,2,3), weight=1) 
        self.ny_var = tk.StringVar(value="202504")
        ttk.Label(root, text="输入年月（如202504）:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.ny_var).grid(row=0, column=1, padx=10, pady=5)

        # 创建功能按钮
        
        ttk.Button(root, text="获取里番信息", command=self.start_get_info).grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ttk.Button(root, text="生成NFO和图片", command=self.start_gen_nfo).grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ttk.Button(root, text="下载里番", command=self.start_download).grid(row=1, column=2, padx=10, pady=5, sticky="ew")
        ttk.Button(root, text="退出", command=root.quit).grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        # 创建输出文本框
        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)
        self.output_area.grid(row=2, column=0, columnspan=4, padx=10, pady=10)
        self.output_area.insert(tk.END, "欢迎使用hanime1里番下载器\n")
        
        # 重定向标准输出到文本框
        sys.stdout = self

    def write(self, text):
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)

    def start_get_info(self):
        threading.Thread(target=self.get_info, daemon=True).start()

    def get_info(self):
        ny = self.ny_var.get()
        print("#" * 40)
        get_hanime_xfyg_info(ny)

    def start_gen_nfo(self):
        threading.Thread(target=self.gen_nfo, daemon=True).start()

    def gen_nfo(self):
        ny = self.ny_var.get()
        print("#" * 40)
        if not os.path.exists(ny):
            os.mkdir(ny)
            print(f"目录 '{ny}' 已创建。")
        else:
            print(f"目录 '{ny}' 已存在。")
        sc_nfo_jpg(ny)
        print(f"已完成图片下载和NFO生成")

    def start_download(self):
        threading.Thread(target=self.download, daemon=True).start()

    def download(self):
        ny = self.ny_var.get()
        print("#" * 40)
        if not os.path.exists(ny):
            os.mkdir(ny)
            print(f"目录 '{ny}' 已创建。")
        else:
            print(f"目录 '{ny}' 已存在。")
        lf_data = db_get_lfid(ny)
        if lf_data:
            for row in lf_data:
                LF_ID = row[0]
                LF_NAME_CN = row[1]
                print(LF_ID, LF_NAME_CN)
                download_html(LF_ID, ny)
        print(f"已完成里番下载")

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    
    root.mainloop()



