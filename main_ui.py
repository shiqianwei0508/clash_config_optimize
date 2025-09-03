import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Checkbutton
import os

from clash_optimizer.resolver import ProxyResolver
from clash_optimizer.geoip import GeoIPClassifier
from clash_optimizer.proxy_manager import ProxyManager
from clash_optimizer.config_builder import ConfigBuilder
from clash_optimizer.utils import (
    load_yaml,
    save_yaml,
    print_summary,
    merge_configs,
    generate_whitelist_rules,
    merge_rules
)
from clash_optimizer.constants import group_keywords, whitelist_domains


class ClashOptimizerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🛠️ Clash YAML 优化工具")
        self.root.geometry("600x400")

        self.config_paths = []
        self.output_path = tk.StringVar(value="config.yaml")
        self.no_trojan = tk.BooleanVar(value=False)

        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="选择多个 Clash 配置文件：").pack(pady=5)
        tk.Button(self.root, text="📂 添加配置文件", command=self.select_files).pack()

        self.file_listbox = tk.Listbox(self.root, height=6)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=10)

        # tk.Label(self.root, text="输出配置路径：").pack(pady=5)
        # tk.Entry(self.root, textvariable=self.output_path, width=50).pack()

        tk.Label(self.root, text="输出配置路径：").pack(pady=5)

        frame = tk.Frame(self.root)
        frame.pack()

        tk.Entry(frame, textvariable=self.output_path, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="📁 浏览", command=self.select_output_path).pack(side=tk.LEFT)

        Checkbutton(self.root, text="移除 trojan 类型节点", variable=self.no_trojan).pack(pady=5)

        tk.Button(self.root, text="🚀 执行优化", command=self.run_optimizer).pack(pady=10)

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("YAML files", "*.yaml *.yml")])
        for f in files:
            if f not in self.config_paths:
                self.config_paths.append(f)
                self.file_listbox.insert(tk.END, f)

    def select_output_path(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml *.yml")],
            initialfile="config.yaml",
            title="选择输出配置文件"
        )
        if path:
            self.output_path.set(path)

    def run_optimizer(self):
        if not self.config_paths:
            messagebox.showerror("错误", "请至少选择一个配置文件")
            return

        try:
            configs = [load_yaml(p) for p in self.config_paths]
            base_config = merge_configs(configs)

            resolver = ProxyResolver()
            geoip = GeoIPClassifier("mmdb/GeoLite2-Country.mmdb")
            manager = ProxyManager(resolver, geoip)

            proxies = manager.dedupe(base_config.get("proxies", []))
            if self.no_trojan.get():
                proxies = manager.filter_by_type(proxies, "trojan")
            proxies = manager.rename_by_geoip(proxies)
            base_config["proxies"] = proxies

            builder = ConfigBuilder(proxies, manager.group_by_keywords(proxies, group_keywords))
            builder.override_base_config(base_config)
            base_config["proxy-groups"] = builder.build_proxy_groups()

            existing_rules = base_config.get("rules", [])
            whitelist_rules = generate_whitelist_rules(whitelist_domains)
            base_config["rules"] = merge_rules(existing_rules, whitelist_rules)

            save_yaml(base_config, self.output_path.get())
            print_summary(base_config)

            messagebox.showinfo("完成", f"配置已保存到 {self.output_path.get()}")

        except Exception as e:
            messagebox.showerror("执行失败", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ClashOptimizerUI(root)
    root.mainloop()
