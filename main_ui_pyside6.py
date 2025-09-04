import os
import sys

# PySide6 核心组件：窗口、布局、控件
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QListWidget,
    QVBoxLayout, QHBoxLayout, QFileDialog, QLineEdit, QMessageBox, QCheckBox
)

# PySide6 核心模块：线程、信号、定时器、动画
from PySide6.QtCore import (
    Qt, QThread, QObject, Signal, QTimer
)

# PySide6 图形模块 (用于加载 GIF)
from PySide6.QtGui import QMovie

# Clash 优化器核心模块
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


def get_default_output_path():
    """
    获取默认输出路径：
    - 优先使用当前用户桌面
    - 如果桌面不存在，则使用当前程序所在目录
    """
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    if os.path.exists(desktop_path):
        return os.path.join(desktop_path, "config.yaml")
    else:
        # 当前程序所在目录（支持打包后的 exe）
        base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
        return os.path.join(base_dir, "config.yaml")


class OptimizerWorker(QObject):
    """
    后台优化任务执行器（运行在子线程中）

    参数:
        config_paths: List[str] - 输入的多个 YAML 配置文件路径
        output_path: str - 输出合并后的配置文件路径
        no_trojan: bool - 是否移除 trojan 类型节点

    信号:
        finished - 优化任务成功完成
        error(str) - 优化任务失败，附带错误信息
    """
    finished = Signal()
    error = Signal(str)

    def __init__(self, config_paths, output_path, no_trojan):
        super().__init__()
        self.config_paths = config_paths
        self.output_path = output_path
        self.no_trojan = no_trojan

    def run(self):
        """
        执行优化任务：
        - 加载并合并配置
        - 去重、筛选、重命名代理
        - 构建 proxy-groups
        - 添加白名单规则
        - 保存结果并打印摘要
        """
        try:
            configs = [load_yaml(p) for p in self.config_paths]
            base_config = merge_configs(configs)

            resolver = ProxyResolver()
            geoip = GeoIPClassifier("mmdb/GeoLite2-Country.mmdb")
            manager = ProxyManager(resolver, geoip)

            proxies = manager.dedupe(base_config.get("proxies", []))
            if self.no_trojan:
                proxies = manager.filter_by_type(proxies, "trojan")
            proxies = manager.rename_by_geoip(proxies)
            base_config["proxies"] = proxies

            builder = ConfigBuilder(proxies, manager.group_by_keywords(proxies, group_keywords))
            builder.override_base_config(base_config)
            base_config["proxy-groups"] = builder.build_proxy_groups()

            existing_rules = base_config.get("rules", [])
            whitelist_rules = generate_whitelist_rules(whitelist_domains)
            base_config["rules"] = merge_rules(existing_rules, whitelist_rules)

            save_yaml(base_config, self.output_path)
            print_summary(base_config)

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class ClashOptimizerUI(QWidget):
    """
    主窗口类：Clash YAML 优化工具的图形界面
    - 支持多文件选择、输出路径设置
    - 可选移除 trojan 节点
    - 显示加载动画
    - 异步执行优化任务 + 超时控制
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛠️ Clash YAML 优化工具")
        self.setMinimumSize(600, 400)

        self.config_paths = []  # 用户选择的配置文件路径列表

        self.output_path = get_default_output_path()  # 默认输出路径

        self.buttons = []  # 所有需要统一禁用/启用的按钮

        self.init_ui()  # 初始化界面布局

    def init_ui(self):
        """
        初始化界面布局与控件：
        - 文件选择按钮与列表
        - 输出路径输入框与浏览按钮
        - trojan 筛选复选框
        - 执行按钮与加载动画
        """
        layout = QVBoxLayout()

        # 配置文件选择
        layout.addWidget(QLabel("选择多个 Clash 配置文件："))
        add_button = QPushButton("📂 添加配置文件")
        add_button.clicked.connect(self.select_files)
        layout.addWidget(add_button)
        self.buttons.append(add_button)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # 输出路径设置
        layout.addWidget(QLabel("输出配置路径："))
        output_layout = QHBoxLayout()
        self.output_input = QLineEdit(self.output_path)
        browse_button = QPushButton("📁 浏览")
        browse_button.clicked.connect(self.select_output_path)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(browse_button)
        layout.addLayout(output_layout)
        self.buttons.append(browse_button)

        # trojan 筛选选项
        self.no_trojan_checkbox = QCheckBox("移除 trojan 类型节点")
        layout.addWidget(self.no_trojan_checkbox)

        # 执行按钮
        run_button = QPushButton("🚀 执行优化")
        run_button.clicked.connect(self.run_optimizer)
        layout.addWidget(run_button)
        self.buttons.append(run_button)

        self.setLayout(layout)

        # ✅ 漂浮式加载动画（不参与布局）
        self.loading_label = QLabel(self)
        self.loading_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.loading_label.setStyleSheet("background: transparent;")
        self.loading_movie = QMovie("static/pic/loading.gif")
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setFixedSize(120, 120)  # 根据 GIF 尺寸调整
        self.loading_label.hide()

        # ✅ 居中定位函数
        def center_loading():
            w, h = self.loading_label.width(), self.loading_label.height()
            x = (self.width() - w) // 2
            y = (self.height() - h) // 2
            self.loading_label.move(x, y)

        # ✅ 在窗口大小变化时自动居中
        self.resizeEvent = lambda event: center_loading()
        center_loading()

    def select_files(self):
        """
        弹出文件选择对话框，添加 YAML 文件到列表
        """
        files, _ = QFileDialog.getOpenFileNames(self, "选择配置文件", "", "YAML Files (*.yaml *.yml)")
        for f in files:
            if f not in self.config_paths:
                self.config_paths.append(f)
                self.file_list.addItem(f)

    def select_output_path(self):
        """
        弹出保存文件对话框，设置输出路径
        """
        path, _ = QFileDialog.getSaveFileName(self, "选择输出配置文件", "config.yaml", "YAML Files (*.yaml *.yml)")
        if path:
            self.output_path = path
            self.output_input.setText(path)

    def on_optimizer_finished(self):
        """
        优化任务完成时的回调：
        - 停止动画
        - 恢复按钮
        - 停止计时器
        - 弹出提示框
        """
        self.loading_movie.stop()
        self.loading_label.hide()

        for btn in self.buttons:
            btn.setEnabled(True)

        self.timeout_timer.stop()

        QMessageBox.information(self, "完成", f"配置已保存到 {self.output_input.text()}")
        self.close()

    def on_optimizer_error(self, msg):
        """
        优化任务失败时的回调：
        - 停止动画
        - 恢复按钮
        - 停止计时器
        - 弹出错误提示
        """
        self.loading_movie.stop()
        self.loading_label.hide()

        for btn in self.buttons:
            btn.setEnabled(True)

        self.timeout_timer.stop()

        QMessageBox.critical(self, "执行失败", msg)

    def on_optimizer_timeout(self):
        """
        优化任务超时处理：
        - 停止动画
        - 恢复按钮
        - 弹出超时提示
        - 强制终止线程
        """
        self.loading_movie.stop()
        self.loading_label.hide()
        for btn in self.buttons:
            btn.setEnabled(True)

        QMessageBox.critical(self, "超时", "优化任务超过 300 秒未完成，已自动终止")
        self.thread.quit()
        self.thread.wait()

    def run_optimizer(self):
        """
        启动优化任务：
        - 检查输入
        - 禁用按钮 + 显示动画
        - 创建线程与工作器
        - 绑定信号槽
        - 启动线程
        - 启动超时计时器
        """
        if not self.config_paths:
            QMessageBox.critical(self, "错误", "请至少选择一个配置文件")
            return

        for btn in self.buttons:
            btn.setEnabled(False)
        self.loading_label.show()
        self.loading_label.raise_()  # 提升层级，确保在最上层
        self.loading_movie.start()
        QApplication.processEvents()

        self.thread = QThread()
        self.worker = OptimizerWorker(
            self.config_paths,
            self.output_input.text(),
            self.no_trojan_checkbox.isChecked()
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_optimizer_finished)
        self.worker.error.connect(self.on_optimizer_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # 启动线程
        self.thread.start()

        # ✅ 启动超时计时器（300秒）
        self.timeout_timer = QTimer(self)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self.on_optimizer_timeout)
        self.timeout_timer.start(300_000)  # 300秒


if __name__ == "__main__":
    """
    程序入口：
    - 创建 QApplication 实例
    - 初始化并显示主窗口
    - 启动事件循环
    """
    app = QApplication(sys.argv)
    window = ClashOptimizerUI()
    window.show()
    sys.exit(app.exec())
