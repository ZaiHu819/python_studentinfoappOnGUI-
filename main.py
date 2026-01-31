# src/main.py
"""
程序入口：初始化 data 文件夹与必要文件，启动 GUI
"""
import os
import tkinter as tk
from gui import App
from data_manager import DataManager

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # project root (class_manager)
DATA_DIR = os.path.join(BASE_DIR, "data")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def main():
    ensure_data_dir()
    dm = DataManager(data_dir=DATA_DIR)
    dm.ensure_initialized()  # 创建 students.xlsx 与 credentials.json（若不存在）
    root = tk.Tk()
    root.title("班级人员管理系统")
    # 设置窗口最小尺寸，跨平台友好
    root.geometry("900x600")
    app = App(root, data_manager=dm)
    root.mainloop()

if __name__ == "__main__":
    main()