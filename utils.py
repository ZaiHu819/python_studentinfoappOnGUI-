# src/utils.py
"""
通用工具函数
"""
def safe_str(x):
    return "" if x is None else str(x)