# src/gui.py
"""
GUI 模块：包含登录页、首页、学生信息页、学生列表页、统计页
使用面向对象组织页面，便于维护与扩展
"""
import tkinter as tk
from tkinter import ttk, messagebox
from utils import safe_str

class App:
    def __init__(self, root, data_manager):
        self.root = root
        self.dm = data_manager
        self.current_user = None
        self._setup_styles()
        self._build_frames()
        self.show_login()

    def _setup_styles(self):
        style = ttk.Style()
        # 使用系统主题并做少量美化
        style.theme_use("clam")
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=4)

    def _build_frames(self):
        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        # 不同页面的 frame
        self.frames = {}
        for F in (LoginPage, HomePage, StudentInfoPage, StudentListPage, StatsPage, ChangePasswordPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def show_login(self):
        self.show_frame("LoginPage")

    def login_success(self, username):
        self.current_user = username
        self.show_frame("HomePage")

    def logout(self):
        self.current_user = None
        self.show_login()

# ---------------- 页面实现 ----------------
class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build()

    def _build(self):
        ttk.Label(self, text="班级人员管理系统", font=("Helvetica", 18)).pack(pady=20)
        frm = ttk.Frame(self)
        frm.pack(pady=10)
        ttk.Label(frm, text="用户名:").grid(row=0, column=0, sticky="e")
        self.username = tk.StringVar()
        ttk.Entry(frm, textvariable=self.username).grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(frm, text="密码:").grid(row=1, column=0, sticky="e")
        self.password = tk.StringVar()
        ttk.Entry(frm, textvariable=self.password, show="*").grid(row=1, column=1, padx=6, pady=6)
        btn = ttk.Button(self, text="登录", command=self._on_login)
        btn.pack(pady=10)

    def _on_login(self):
        u = self.username.get().strip()
        p = self.password.get().strip()
        if self.controller.dm.validate_login(u, p):
            self.controller.login_success(u)
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build()

    def _build(self):
        top = ttk.Frame(self)
        top.pack(fill="x", pady=8)
        ttk.Label(top, text="系统首页", font=("Helvetica", 16)).pack(side="left", padx=10)
        ttk.Button(top, text="登出", command=self.controller.logout).pack(side="right", padx=10)
        # 功能菜单
        menu = ttk.Frame(self)
        menu.pack(pady=20)
        ttk.Button(menu, text="显示学生信息（单个/筛选）", width=30, command=lambda: self.controller.show_frame("StudentInfoPage")).grid(row=0, column=0, padx=10, pady=6)
        ttk.Button(menu, text="学生列表（显示所有）", width=30, command=lambda: self.controller.show_frame("StudentListPage")).grid(row=1, column=0, padx=10, pady=6)
        ttk.Button(menu, text="统计信息（按性别）", width=30, command=lambda: self.controller.show_frame("StatsPage")).grid(row=2, column=0, padx=10, pady=6)
        ttk.Button(menu, text="修改账户密码", width=30, command=lambda: self.controller.show_frame("ChangePasswordPage")).grid(row=3, column=0, padx=10, pady=6)

class StudentInfoPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=6)
        ttk.Label(header, text="学生信息查询", font=("Helvetica", 14)).pack(side="left", padx=10)
        ttk.Button(header, text="返回首页", command=lambda: self.controller.show_frame("HomePage")).pack(side="right", padx=10)
        # 查询条件
        cond = ttk.Frame(self)
        cond.pack(pady=8, padx=10, fill="x")
        ttk.Label(cond, text="学号:").grid(row=0, column=0, sticky="e")
        self.e_id = tk.StringVar()
        ttk.Entry(cond, textvariable=self.e_id).grid(row=0, column=1, padx=6)
        ttk.Label(cond, text="姓名:").grid(row=0, column=2, sticky="e")
        self.e_name = tk.StringVar()
        ttk.Entry(cond, textvariable=self.e_name).grid(row=0, column=3, padx=6)
        ttk.Label(cond, text="性别:").grid(row=1, column=0, sticky="e")
        self.gender = tk.StringVar(value="全部")
        ttk.Combobox(cond, textvariable=self.gender, values=["全部", "男", "女"], state="readonly").grid(row=1, column=1, padx=6)
        ttk.Label(cond, text="班级:").grid(row=1, column=2, sticky="e")
        # 动态获取班级选项
        classes = ["全部"] + sorted({s["班级"] for s in self.controller.dm.load_all_students()})
        self.class_name = tk.StringVar(value="全部")
        ttk.Combobox(cond, textvariable=self.class_name, values=classes, state="readonly").grid(row=1, column=3, padx=6)
        ttk.Button(cond, text="查询", command=self.on_search).grid(row=2, column=0, columnspan=4, pady=8)
        # 结果显示
        cols = ("学号", "姓名", "性别", "班级")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150, anchor="center")
        self.tree.pack(padx=10, pady=6, fill="both", expand=True)

    def on_search(self):
        sid = self.e_id.get().strip()
        name = self.e_name.get().strip()
        gender = self.gender.get()
        cls = self.class_name.get()
        results = self.controller.dm.find_students(student_id=sid or None, name=name or None, gender=gender, class_name=cls)
        # 清空 tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in results:
            self.tree.insert("", "end", values=(safe_str(r["学号"]), safe_str(r["姓名"]), safe_str(r["性别"]), safe_str(r["班级"])))

class StudentListPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=6)
        ttk.Label(header, text="学生列表（所有）", font=("Helvetica", 14)).pack(side="left", padx=10)
        ttk.Button(header, text="刷新", command=self.load_all).pack(side="right", padx=6)
        ttk.Button(header, text="返回首页", command=lambda: self.controller.show_frame("HomePage")).pack(side="right", padx=6)
        cols = ("学号", "姓名", "性别", "班级")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=180, anchor="center")
        self.tree.pack(padx=10, pady=6, fill="both", expand=True)
        self.load_all()

    def load_all(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        all_students = self.controller.dm.load_all_students()
        for s in all_students:
            self.tree.insert("", "end", values=(safe_str(s["学号"]), safe_str(s["姓名"]), safe_str(s["性别"]), safe_str(s["班级"])))

class StatsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=6)
        ttk.Label(header, text="统计信息（按性别）", font=("Helvetica", 14)).pack(side="left", padx=10)
        ttk.Button(header, text="导出统计到文件", command=self.export_stats).pack(side="right", padx=6)
        ttk.Button(header, text="返回首页", command=lambda: self.controller.show_frame("HomePage")).pack(side="right", padx=6)
        # 统计表格
        cols = ("性别", "人数", "比例")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=200, anchor="center")
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.load_stats()

    def load_stats(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        stats = self.controller.dm.stats_by_gender()
        for s in stats:
            self.tree.insert("", "end", values=(s["性别"], s["人数"], s["比例"]))

    def export_stats(self):
        stats = self.controller.dm.stats_by_gender()
        path = self.controller.dm.export_stats(stats)
        messagebox.showinfo("导出成功", f"统计文件已导出到：\n{path}")

class ChangePasswordPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=6)
        ttk.Label(header, text="修改账户密码", font=("Helvetica", 14)).pack(side="left", padx=10)
        ttk.Button(header, text="返回首页", command=lambda: self.controller.show_frame("HomePage")).pack(side="right", padx=6)
        frm = ttk.Frame(self)
        frm.pack(pady=20)
        ttk.Label(frm, text="新用户名:").grid(row=0, column=0, sticky="e")
        self.new_user = tk.StringVar()
        ttk.Entry(frm, textvariable=self.new_user).grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(frm, text="新密码:").grid(row=1, column=0, sticky="e")
        self.new_pwd = tk.StringVar()
        ttk.Entry(frm, textvariable=self.new_pwd, show="*").grid(row=1, column=1, padx=6, pady=6)
        ttk.Button(frm, text="保存", command=self.on_save).grid(row=2, column=0, columnspan=2, pady=10)

    def on_save(self):
        u = self.new_user.get().strip()
        p = self.new_pwd.get().strip()
        if not u or not p:
            messagebox.showwarning("输入错误", "用户名和密码不能为空")
            return
        self.controller.dm.change_password(u, p)
        messagebox.showinfo("成功", "账户信息已更新，请使用新账户登录")
        self.controller.logout()