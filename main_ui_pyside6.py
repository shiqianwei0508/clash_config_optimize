from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QListWidget,
    QVBoxLayout, QHBoxLayout, QFileDialog, QLineEdit, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
import sys
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QLabel


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

from PySide6.QtCore import QThread
from PySide6.QtCore import QObject, Signal
from PySide6.QtCore import QTimer
class OptimizerWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, config_paths, output_path, no_trojan):
        super().__init__()
        self.config_paths = config_paths
        self.output_path = output_path
        self.no_trojan = no_trojan

    def run(self):
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛠️ Clash YAML 优化工具")
        self.setMinimumSize(600, 400)

        self.config_paths = []
        self.output_path = "config.yaml"

        self.buttons = []  # ✅ 初始化按钮列表

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("选择多个 Clash 配置文件："))
        add_button = QPushButton("📂 添加配置文件")
        add_button.clicked.connect(self.select_files)
        layout.addWidget(add_button)
        self.buttons.append(add_button)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        layout.addWidget(QLabel("输出配置路径："))
        output_layout = QHBoxLayout()
        self.output_input = QLineEdit(self.output_path)
        browse_button = QPushButton("📁 浏览")
        browse_button.clicked.connect(self.select_output_path)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(browse_button)
        layout.addLayout(output_layout)
        self.buttons.append(browse_button)

        self.no_trojan_checkbox = QCheckBox("移除 trojan 类型节点")
        layout.addWidget(self.no_trojan_checkbox)

        run_button = QPushButton("🚀 执行优化")
        run_button.clicked.connect(self.run_optimizer)
        layout.addWidget(run_button)
        self.buttons.append(run_button)

        self.setLayout(layout)

        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_movie = QMovie("static/pic/loading.gif")
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择配置文件", "", "YAML Files (*.yaml *.yml)")
        for f in files:
            if f not in self.config_paths:
                self.config_paths.append(f)
                self.file_list.addItem(f)

    def select_output_path(self):
        path, _ = QFileDialog.getSaveFileName(self, "选择输出配置文件", "config.yaml", "YAML Files (*.yaml *.yml)")
        if path:
            self.output_path = path
            self.output_input.setText(path)

    def on_optimizer_finished(self):
        self.loading_movie.stop()
        self.loading_label.hide()

        # ✅ 恢复按钮
        for btn in self.buttons:
            btn.setEnabled(True)

        # ✅ 停止超时计时器
        self.timeout_timer.stop()

        QMessageBox.information(self, "完成", f"配置已保存到 {self.output_input.text()}")
        self.close()

    def on_optimizer_error(self, msg):
        self.loading_movie.stop()
        self.loading_label.hide()

        # ✅ 恢复按钮
        for btn in self.buttons:
            btn.setEnabled(True)

        # ✅ 停止超时计时器
        self.timeout_timer.stop()

        QMessageBox.critical(self, "执行失败", msg)

    def on_optimizer_timeout(self):
        self.loading_movie.stop()
        self.loading_label.hide()
        for btn in self.buttons:
            btn.setEnabled(True)

        QMessageBox.critical(self, "超时", "优化任务超过 300 秒未完成，已自动终止")
        self.thread.quit()
        self.thread.wait()

    def run_optimizer(self):
        if not self.config_paths:
            QMessageBox.critical(self, "错误", "请至少选择一个配置文件")
            return

        # 禁用按钮 + 显示动画
        for btn in self.buttons:
            btn.setEnabled(False)
        self.loading_label.show()
        self.loading_movie.start()
        QApplication.processEvents()

        # 启动线程
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

        self.thread.start()

        # ✅ 启动超时计时器（300秒）
        self.timeout_timer = QTimer(self)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self.on_optimizer_timeout)
        self.timeout_timer.start(300_000)  # 300秒


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClashOptimizerUI()
    window.show()
    sys.exit(app.exec())
