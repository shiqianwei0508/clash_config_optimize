#!/usr/bin/env python3
"""
🔗 URI 节点转 Clash YAML 工具 - PySide6 GUI 界面
"""
import sys
import os
import threading
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QFileDialog, QRadioButton,
    QButtonGroup, QGroupBox, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

# 添加项目根目录到路径，确保能导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uri2clash.parser import parse_uri
from uri2clash.utils import load_uri_file, load_uri_from_url, save_yaml

def generate_clash_config(proxies):
    """生成完整的Clash配置"""
    # 按国家分组节点
    country_proxies = {
        '🇺🇸': [],  # 美国
        '🇭🇰': [],  # 香港
        '🇯🇵': [],  # 日本
        'other': []  # 其他国家
    }
    
    # 识别节点国家
    for proxy in proxies:
        name = proxy['name']
        # 检查名称中是否包含国家标识
        if '🇺🇸' in name or 'US' in name:
            country_proxies['🇺🇸'].append(name)
        elif '🇭🇰' in name or 'HK' in name:
            country_proxies['🇭🇰'].append(name)
        elif '🇯🇵' in name or 'JP' in name:
            country_proxies['🇯🇵'].append(name)
        else:
            country_proxies['other'].append(name)
    
    # 构建完整配置
    config = {
        # 基础配置
        'mixed-port': 7890,
        'allow-lan': False,
        'bind-address': '127.0.0.1',
        'socks-port': 7891,
        'redir-port': 7892,
        'mode': 'Rule',
        'log-level': 'info',
        'unified-delay': True,
        'tun': {
            'enable': False
        },
        
        # 代理节点
        'proxies': proxies,
        
        # 代理组配置
        'proxy-groups': [
            {
                'name': '🚀 节点选择',
                'type': 'select',
                'proxies': ['DIRECT', '🇺🇸 美国节点', '🇭🇰 香港节点', '🇯🇵 日本节点', '🌐 其他节点']
            },
            {
                'name': '🇺🇸 美国节点',
                'type': 'select',
                'proxies': ['DIRECT'] + country_proxies['🇺🇸']
            },
            {
                'name': '🇭🇰 香港节点',
                'type': 'select',
                'proxies': ['DIRECT'] + country_proxies['🇭🇰']
            },
            {
                'name': '🇯🇵 日本节点',
                'type': 'select',
                'proxies': ['DIRECT'] + country_proxies['🇯🇵']
            },
            {
                'name': '🌐 其他节点',
                'type': 'select',
                'proxies': ['DIRECT'] + country_proxies['other']
            },
            {
                'name': '📺 流媒体',
                'type': 'select',
                'proxies': ['DIRECT', '🇺🇸 美国节点']
            },
            {
                'name': '🌍 全球直连',
                'type': 'select',
                'proxies': ['DIRECT', '🚀 节点选择']
            },
            {
                'name': '🛡️ 隐私保护',
                'type': 'select',
                'proxies': ['DIRECT', '🚀 节点选择']
            }
        ],
        
        # 规则配置
        'rules': [
            # Telegram相关规则
            'DOMAIN-SUFFIX,telegram.org,🚀 节点选择',
            'DOMAIN-SUFFIX,t.me,🚀 节点选择',
            'DOMAIN-SUFFIX,telegram.me,🚀 节点选择',
            'DOMAIN-SUFFIX,tdesktop.com,🚀 节点选择',
            # 流媒体相关规则
            'DOMAIN-SUFFIX,youtube.com,📺 流媒体',
            'DOMAIN-SUFFIX,netflix.com,📺 流媒体',
            'DOMAIN-SUFFIX,disneyplus.com,📺 流媒体',
            'DOMAIN-SUFFIX,hbo.com,📺 流媒体',
            'DOMAIN-SUFFIX,spotify.com,📺 流媒体',
            # 国内应用规则
            'DOMAIN-SUFFIX,bilibili.com,DIRECT',
            'DOMAIN-SUFFIX,netease.com,DIRECT',
            'DOMAIN-SUFFIX,163.com,DIRECT',
            'DOMAIN-SUFFIX,qq.com,DIRECT',
            'DOMAIN-SUFFIX,weixin.qq.com,DIRECT',
            'DOMAIN-SUFFIX,weibo.com,DIRECT',
            'DOMAIN-SUFFIX,baidu.com,DIRECT',
            # 国内IP规则
            'GEOIP,CN,DIRECT',
            # 其他规则
            'DOMAIN-KEYWORD,tiktok,🚀 节点选择',
            # 默认规则
            'MATCH,🚀 节点选择'
        ]
    }
    
    return config

class ConversionThread(QThread):
    """转换线程，用于在后台执行转换任务"""
    log_signal = Signal(str)  # 日志信号
    progress_signal = Signal(int)  # 进度信号
    finished_signal = Signal(bool, str)  # 完成信号
    
    def __init__(self, input_type, input_source, output_path):
        super().__init__()
        self.input_type = input_type
        self.input_source = input_source
        self.output_path = output_path
    
    def run(self):
        """执行转换任务"""
        try:
            self.log_signal.emit("🔄 开始转换任务...")
            
            # 加载URI列表
            if self.input_type == "file":
                self.log_signal.emit(f"📥 从文件加载节点: {self.input_source}")
                uris = load_uri_file(self.input_source)
            else:
                self.log_signal.emit(f"📥 从URL加载节点: {self.input_source}")
                uris = load_uri_from_url(self.input_source)
            
            self.log_signal.emit(f"🔍 发现 {len(uris)} 个节点")
            
            proxies = []
            name_counts = {}
            name_server_map = {}
            
            total = len(uris)
            for i, uri in enumerate(uris):
                # 更新进度
                progress = int((i + 1) / total * 100)
                self.progress_signal.emit(progress)
                
                try:
                    proxy = parse_uri(uri)
                    original_name = proxy['name']
                    server = proxy['server']
                    port = proxy['port']
                    server_port = f"{server}:{port}"
                    
                    # 构建唯一标识键
                    unique_key = f"{original_name}#{server_port}"
                    
                    # 检查是否已经存在相同名称和相同服务器端口的节点
                    if unique_key in name_server_map:
                        # 完全相同的节点，跳过
                        self.log_signal.emit(f"⏭️  跳过重复节点: {original_name} ({server_port})")
                        continue
                    
                    # 检查是否存在相同名称但不同服务器端口的节点
                    if original_name in name_counts:
                        # 同名不同服务器，添加编号后缀
                        name_counts[original_name] += 1
                        new_name = f"{original_name} ({name_counts[original_name]})"
                        proxy['name'] = new_name
                        self.log_signal.emit(f"📝 重命名节点: {original_name} -> {new_name} ({server_port})")
                    else:
                        # 新名称，初始化计数
                        name_counts[original_name] = 1
                    
                    # 记录节点信息
                    name_server_map[unique_key] = True
                    proxies.append(proxy)
                except Exception as e:
                    self.log_signal.emit(f"❌ 跳过无效 URI: {uri}\n   原因: {e}")
            
            # 生成完整的Clash配置
            self.log_signal.emit("📋 生成Clash配置...")
            config = generate_clash_config(proxies)
            
            # 保存配置文件
            self.log_signal.emit(f"💾 保存配置到: {self.output_path}")
            save_yaml(config, self.output_path)
            
            self.log_signal.emit(f"✅ 转换完成！")
            self.log_signal.emit(f"📊 结果统计:")
            self.log_signal.emit(f"   - 原始节点数: {len(uris)}")
            self.log_signal.emit(f"   - 转换后节点数: {len(proxies)}")
            self.log_signal.emit(f"   - 代理组数量: {len(config['proxy-groups'])}")
            self.log_signal.emit(f"   - 规则数量: {len(config['rules'])}")
            
            self.finished_signal.emit(True, f"转换成功！已保存 {len(proxies)} 个节点到 {self.output_path}")
            
        except Exception as e:
            error_msg = f"转换失败: {str(e)}"
            self.log_signal.emit(f"❌ {error_msg}")
            self.finished_signal.emit(False, error_msg)

class Uri2ClashUI(QMainWindow):
    """URI转Clash YAML工具的主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        # 设置窗口基本属性
        self.setWindowTitle("🔗 URI 节点转 Clash YAML 工具")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 设置字体
        font = QFont("Microsoft YaHei", 9)
        QApplication.setFont(font)
        
        # 1. 输入选择区域
        input_group = QGroupBox("📥 输入设置")
        input_layout = QVBoxLayout()
        
        # 输入类型选择（文件/URL）
        type_layout = QHBoxLayout()
        self.file_radio = QRadioButton("📁 从文件加载")
        self.url_radio = QRadioButton("🌐 从URL加载")
        self.type_group = QButtonGroup()
        self.type_group.addButton(self.file_radio)
        self.type_group.addButton(self.url_radio)
        self.file_radio.setChecked(True)  # 默认选择文件
        
        type_layout.addWidget(self.file_radio)
        type_layout.addWidget(self.url_radio)
        type_layout.addStretch()
        
        # 文件输入区域
        self.file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("选择包含URI节点的文本文件")
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.browse_file)
        
        self.file_layout.addWidget(self.file_path_edit)
        self.file_layout.addWidget(self.browse_btn)
        
        # URL输入区域
        self.url_layout = QHBoxLayout()
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("输入包含URI节点的URL地址")
        self.url_layout.addWidget(self.url_edit)
        
        # 连接信号
        self.file_radio.toggled.connect(self.toggle_input_mode)
        
        input_layout.addLayout(type_layout)
        input_layout.addLayout(self.file_layout)
        input_layout.addLayout(self.url_layout)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # 2. 输出设置区域
        output_group = QGroupBox("💾 输出设置")
        output_layout = QHBoxLayout()
        
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("输出YAML文件路径")
        self.output_path_edit.setText("converted.yaml")  # 默认输出路径
        self.output_browse_btn = QPushButton("浏览...")
        self.output_browse_btn.clicked.connect(self.browse_output)
        
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(self.output_browse_btn)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # 3. 转换按钮
        btn_layout = QHBoxLayout()
        self.convert_btn = QPushButton("🚀 开始转换")
        self.convert_btn.setFixedHeight(40)
        self.convert_btn.clicked.connect(self.start_conversion)
        
        self.clear_log_btn = QPushButton("🗑️ 清空日志")
        self.clear_log_btn.clicked.connect(self.clear_log)
        
        btn_layout.addWidget(self.convert_btn)
        btn_layout.addWidget(self.clear_log_btn)
        main_layout.addLayout(btn_layout)
        
        # 4. 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 5. 日志显示区域
        log_group = QGroupBox("📋 转换日志")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #f5f5f5; font-family: 'Consolas', 'Monaco', monospace;")
        
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group, 1)  # 占据剩余空间
        
        # 6. 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
        
        # 初始隐藏URL输入区域
        self.toggle_input_mode()
        
        # 添加欢迎信息
        self.log_text.append("🎉 欢迎使用 URI 节点转 Clash YAML 工具")
        self.log_text.append("📝 支持的协议: VMess, VLESS, Trojan, Shadowsocks, Hysteria2")
        self.log_text.append("💡 选择输入方式，设置输出路径，点击'开始转换'按钮")
        self.log_text.append("=" * 80)
    
    def toggle_input_mode(self):
        """切换输入模式（文件/URL）"""
        is_file_mode = self.file_radio.isChecked()
        self.file_path_edit.setEnabled(is_file_mode)
        self.browse_btn.setEnabled(is_file_mode)
        self.url_edit.setEnabled(not is_file_mode)
    
    def browse_file(self):
        """浏览选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择URI节点文件", ".", "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def browse_output(self):
        """浏览选择输出文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存Clash配置", ".", "YAML文件 (*.yaml *.yml);;所有文件 (*.*)"
        )
        if file_path:
            self.output_path_edit.setText(file_path)
    
    def start_conversion(self):
        """开始转换"""
        # 验证输入
        if self.file_radio.isChecked():
            input_source = self.file_path_edit.text().strip()
            if not input_source:
                QMessageBox.warning(self, "警告", "请选择输入文件！")
                return
            if not os.path.exists(input_source):
                QMessageBox.warning(self, "警告", "输入文件不存在！")
                return
            input_type = "file"
        else:
            input_source = self.url_edit.text().strip()
            if not input_source:
                QMessageBox.warning(self, "警告", "请输入URL地址！")
                return
            if not (input_source.startswith("http://") or input_source.startswith("https://")):
                QMessageBox.warning(self, "警告", "请输入有效的URL地址（以http://或https://开头）！")
                return
            input_type = "url"
        
        # 验证输出路径
        output_path = self.output_path_edit.text().strip()
        if not output_path:
            QMessageBox.warning(self, "警告", "请设置输出文件路径！")
            return
        
        # 禁用按钮，防止重复点击
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("转换中...")
        
        # 创建转换线程
        self.conversion_thread = ConversionThread(input_type, input_source, output_path)
        self.conversion_thread.log_signal.connect(self.append_log)
        self.conversion_thread.progress_signal.connect(self.update_progress)
        self.conversion_thread.finished_signal.connect(self.on_conversion_finished)
        self.conversion_thread.start()
    
    def append_log(self, message):
        """添加日志信息"""
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.moveCursor(self.log_text.textCursor().End)
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def on_conversion_finished(self, success, message):
        """转换完成处理"""
        # 恢复按钮状态
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_bar.showMessage("转换成功")
            QMessageBox.information(self, "成功", message)
        else:
            self.status_bar.showMessage("转换失败")
            QMessageBox.critical(self, "错误", message)
    
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.append_log("📝 日志已清空")
        self.append_log("=" * 80)

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 创建并显示主窗口
    window = Uri2ClashUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
