#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash配置验证工具 - GUI版本
支持通过URL或本地文件路径验证Clash YAML配置文件
"""

import sys
import os
import threading
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox,
    QProgressBar, QGroupBox, QRadioButton
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont, QIcon, QColor, QTextCursor

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入现有的验证功能
from validate_clash_yaml import validate_clash_yaml


class WorkerSignals(QObject):
    """工作线程信号类"""
    progress = Signal(int)
    log = Signal(str)
    finished = Signal(bool)
    error = Signal(str)


class ValidateWorker(threading.Thread):
    """验证工作线程"""
    
    def __init__(self, input_source, is_url=False):
        super().__init__()
        self.input_source = input_source
        self.is_url = is_url
        self.signals = WorkerSignals()
        self.running = True
    
    def run(self):
        try:
            self.signals.progress.emit(0)
            
            # 处理输入源
            yaml_path = self.input_source
            
            if self.is_url:
                # 从URL下载文件
                self.signals.log.emit(f"[🔍] 正在从URL下载配置文件: {self.input_source}")
                yaml_path = self._download_from_url(self.input_source)
                self.signals.progress.emit(50)
            
            # 重定向标准输出到日志
            old_stdout = sys.stdout
            sys.stdout = CapturingStringIO()
            
            try:
                # 执行验证
                self.signals.log.emit(f"[🔍] 开始验证配置文件: {yaml_path}")
                result = validate_clash_yaml(yaml_path)
                
                # 获取日志内容
                logs = sys.stdout.getvalue()
                for line in logs.split('\n'):
                    if line.strip():
                        self.signals.log.emit(line.strip())
                
                self.signals.progress.emit(100)
                self.signals.finished.emit(result)
            finally:
                # 恢复标准输出
                sys.stdout = old_stdout
                
                # 如果是临时下载的文件，清理它
                if self.is_url and yaml_path != self.input_source:
                    try:
                        os.remove(yaml_path)
                    except:
                        pass
        
        except Exception as e:
            self.signals.error.emit(f"[❌] 执行出错: {str(e)}")
            self.signals.finished.emit(False)
    
    def _download_from_url(self, url):
        """从URL下载文件"""
        try:
            # 发送请求
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 保存到临时文件
            temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_downloaded_config.yaml")
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            return temp_path
        except Exception as e:
            raise Exception(f"下载文件失败: {str(e)}")
    
    def stop(self):
        """停止工作线程"""
        self.running = False
        self.join(timeout=5)


class CapturingStringIO:
    """捕获标准输出的字符串IO类"""
    
    def __init__(self):
        self.content = []
    
    def write(self, text):
        self.content.append(text)
    
    def getvalue(self):
        return ''.join(self.content)
    
    def flush(self):
        pass


class ValidateClashYamlGUI(QMainWindow):
    """Clash配置验证工具GUI类"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题和大小
        self.setWindowTitle("Clash配置验证工具")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置字体
        font = QFont()
        font.setFamily("SimHei")
        font.setPointSize(10)
        self.setFont(font)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 文件输入标签页
        self.file_tab = QWidget()
        self.setup_file_tab()
        self.tab_widget.addTab(self.file_tab, "本地文件")
        
        # URL输入标签页
        self.url_tab = QWidget()
        self.setup_url_tab()
        self.tab_widget.addTab(self.url_tab, "URL地址")
        
        # 日志显示区域
        log_group = QGroupBox("验证日志")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.WidgetWidth)
        self.log_text.setStyleSheet("background-color: #f5f5f5; font-family: Consolas, monospace;")
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group, 1)
        
        # 底部控件
        bottom_layout = QHBoxLayout()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        bottom_layout.addWidget(self.progress_bar, 1)
        
        # 验证按钮
        self.validate_button = QPushButton("开始验证")
        self.validate_button.setFixedSize(100, 30)
        self.validate_button.clicked.connect(self.on_validate_clicked)
        bottom_layout.addWidget(self.validate_button)
        
        # 清除按钮
        self.clear_button = QPushButton("清除日志")
        self.clear_button.setFixedSize(100, 30)
        self.clear_button.clicked.connect(self.on_clear_clicked)
        bottom_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(bottom_layout)
    
    def setup_file_tab(self):
        """设置文件输入标签页"""
        layout = QVBoxLayout(self.file_tab)
        
        file_group = QGroupBox("选择Clash配置文件")
        file_group_layout = QHBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Clash YAML配置文件路径")
        file_group_layout.addWidget(self.file_path_edit, 1)
        
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.on_browse_clicked)
        file_group_layout.addWidget(browse_button)
        
        file_group.setLayout(file_group_layout)
        layout.addWidget(file_group)
        
        # 添加一些说明文本
        info_label = QLabel("提示：选择本地的Clash配置文件（.yaml或.yml格式）进行验证")
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info_label)
    
    def setup_url_tab(self):
        """设置URL输入标签页"""
        layout = QVBoxLayout(self.url_tab)
        
        url_group = QGroupBox("输入配置文件URL")
        url_group_layout = QVBoxLayout()
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://example.com/config.yaml")
        url_group_layout.addWidget(self.url_edit)
        
        url_group.setLayout(url_group_layout)
        layout.addWidget(url_group)
        
        # 添加一些说明文本
        info_label = QLabel("提示：输入Clash配置文件的URL地址，系统将自动下载并验证")
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info_label)
    
    def on_browse_clicked(self):
        """浏览文件按钮点击事件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Clash配置文件", "", "YAML Files (*.yaml *.yml);;All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def on_validate_clicked(self):
        """开始验证按钮点击事件"""
        # 检查当前选中的标签页
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # 本地文件
            input_source = self.file_path_edit.text().strip()
            if not input_source:
                QMessageBox.warning(self, "警告", "请选择Clash配置文件")
                return
            if not os.path.exists(input_source):
                QMessageBox.warning(self, "警告", "文件不存在，请检查路径")
                return
            is_url = False
        else:  # URL
            input_source = self.url_edit.text().strip()
            if not input_source:
                QMessageBox.warning(self, "警告", "请输入配置文件URL")
                return
            if not input_source.startswith(('http://', 'https://')):
                QMessageBox.warning(self, "警告", "请输入有效的URL地址")
                return
            is_url = True
        
        # 清空日志
        self.log_text.clear()
        
        # 禁用按钮
        self.validate_button.setEnabled(False)
        self.validate_button.setText("验证中...")
        
        # 启动工作线程
        self.worker = ValidateWorker(input_source, is_url)
        self.worker.signals.log.connect(self.append_log)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.finished.connect(self.on_validation_finished)
        self.worker.signals.error.connect(self.show_error)
        self.worker.start()
    
    def append_log(self, text):
        """追加日志到文本区域"""
        # 根据日志级别设置不同的颜色
        color = "#000000"  # 默认黑色
        if "❌" in text:
            color = "#FF0000"  # 红色错误
        elif "⚠️" in text:
            color = "#FF8C00"  # 橙色警告
        elif "✅" in text:
            color = "#008000"  # 绿色成功
        elif "🔍" in text or "📊" in text or "📋" in text or "🔧" in text:
            color = "#0000CD"  # 蓝色信息
        
        # 使用HTML格式插入带颜色的文本
        self.log_text.append(f'<span style="color: {color};">{text}</span>')
        
        # 自动滚动到底部
        self.log_text.moveCursor(QTextCursor.End)
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def on_validation_finished(self, success):
        """验证完成回调"""
        # 恢复按钮状态
        self.validate_button.setEnabled(True)
        self.validate_button.setText("开始验证")
        
        # 显示结果
        if success:
            QMessageBox.information(self, "成功", "配置文件验证通过！")
        else:
            QMessageBox.warning(self, "失败", "配置文件验证失败，请查看日志详情")
    
    def show_error(self, message):
        """显示错误消息"""
        self.append_log(message)
        # 恢复按钮状态
        self.validate_button.setEnabled(True)
        self.validate_button.setText("开始验证")
    
    def on_clear_clicked(self):
        """清除日志按钮点击事件"""
        self.log_text.clear()
        self.progress_bar.setValue(0)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 确保工作线程已停止
        if self.worker and self.worker.is_alive():
            self.worker.stop()
        event.accept()


if __name__ == "__main__":
    # 设置中文字体支持
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 启动主窗口
    window = ValidateClashYamlGUI()
    window.show()
    
    sys.exit(app.exec())
