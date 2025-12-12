# URI 转 Clash 配置工具 (uri2clash)

一款功能强大的代理节点 URI 转换工具，支持将多种协议的代理节点 URI 转换为 Clash 配置文件格式。

## 📋 功能特性

### 🌐 协议支持
- ✅ **hysteria2** - Hysteria2 代理协议
- ✅ **ss** - Shadowsocks 代理协议
- ✅ **ssr** - ShadowsocksR 代理协议
- ✅ **vless** - VLESS 代理协议
- ✅ **vmess** - VMess 代理协议
- ✅ **trojan** - Trojan 代理协议

### 🛠️ 核心功能
- **URI 解析**：智能解析各种协议的代理节点 URI
- **配置生成**：自动生成符合 Clash 格式的完整配置文件
- **节点分组**：根据节点名称自动按国家/地区分组
- **端口检测**：可选的节点端口可达性检测功能
- **重复节点处理**：自动检测并移除重复节点
- **同名节点处理**：为同名不同服务器的节点添加编号后缀
- **多来源支持**：支持从本地文件或远程 URL 加载节点

### 📊 配置生成
- 自动创建按国家/地区分组的代理组
- 包含常用规则配置（流媒体、全球直连、隐私保护等）
- 支持自定义端口和基础配置

## 📦 安装与依赖

### 安装依赖

```bash
# 进入项目目录
cd e:/Work/code/clash_config_tool/uri2clash

# 安装依赖（推荐使用虚拟环境）
pip install -r ../requirements.txt
```

### 所需依赖
- Python 3.7+
- requests - 用于从 URL 加载节点
- pyyaml - 用于生成 YAML 配置文件
- tqdm - 用于显示进度条

## 🚀 使用方法

### 命令行工具 (uri2clash.py)

#### 基本用法

```bash
# 从本地文件加载节点并生成配置
python uri2clash.py --input url_sample.txt --output clash_config.yaml

# 从远程 URL 加载节点并生成配置
python uri2clash.py --url "https://example.com/subscription.txt" --output clash_config.yaml

# 跳过端口检测，保留所有解析成功的节点
python uri2clash.py --input url_sample.txt --output clash_config_all.yaml --skip-port-check
```

#### 参数说明

| 参数 | 描述 | 必选 |
|------|------|------|
| `--input` | 包含 URI 节点的本地文本文件路径 | 是（与 `--url` 二选一） |
| `--url` | 包含 URI 节点的远程 URL 地址 | 是（与 `--input` 二选一） |
| `--output` | 输出的 Clash 配置文件路径，默认：`converted.yaml` | 否 |
| `--skip-port-check` | 跳过端口可达性检测，保留所有解析成功的节点 | 否 |

### GUI 工具 (uri2clash_gui.py)

```bash
# 启动 GUI 界面
python uri2clash_gui.py
```

## 📁 项目结构

```
uri2clash/
├── debug_ssr.py          # SSR 协议调试工具
├── decode_subscription.py # 订阅解码工具
├── download_and_check.py # 下载和检查工具
├── parser.py             # 协议解析核心模块
├── test_conversion.py    # 转换测试脚本
├── test_ssr.py           # SSR 协议测试脚本
├── uri2clash.py          # 命令行主程序
├── uri2clash_gui.py      # GUI 界面程序
└── utils.py              # 工具函数模块
```

## 📖 模块说明

### 核心模块

#### parser.py
协议解析核心模块，支持解析以下协议：
- `parse_hysteria2()` - 解析 Hysteria2 协议 URI
- `parse_ss()` - 解析 Shadowsocks 协议 URI
- `parse_ssr()` - 解析 ShadowsocksR 协议 URI
- `parse_vless()` - 解析 VLESS 协议 URI
- `parse_vmess()` - 解析 VMess 协议 URI
- `parse_trojan()` - 解析 Trojan 协议 URI
- `parse_uri()` - 主入口函数，根据 URI 前缀自动选择解析函数

#### uri2clash.py
命令行主程序，包含：
- 命令行参数解析
- URI 加载（文件或 URL）
- 节点解析和去重
- 端口可达性检测
- Clash 配置生成和保存

#### utils.py
工具函数模块：
- `load_uri_file()` - 从本地文件加载 URI 列表
- `load_uri_from_url()` - 从远程 URL 加载 URI 列表
- `save_yaml()` - 将数据保存为 YAML 格式文件

### 辅助工具

#### decode_subscription.py
订阅解码工具，用于解码各种格式的代理节点订阅。

#### download_and_check.py
下载和检查工具，用于从 URL 下载节点并进行基本检查。

#### debug_ssr.py
SSR 协议调试工具，用于调试 SSR URI 解析问题。

## 📊 测试脚本

### test_conversion.py
节点转换测试脚本，用于验证 URI 解析的正确性。

### test_ssr.py
SSR 协议专用测试脚本，用于测试 SSR URI 解析功能。

## 🛠️ 开发与调试

### 运行测试

```bash
# 运行转换测试
python test_conversion.py

# 运行 SSR 协议测试
python test_ssr.py
```

### 调试 SSR 协议

```bash
python debug_ssr.py <ssr_uri>
```

## 📝 示例

### 转换本地文件

```bash
# 转换本地节点文件
python uri2clash.py --input url_sample.txt --output clash_config.yaml

# 输出结果示例
📥 从文件加载节点: url_sample.txt
🔍 发现 237 个节点
⏭️  跳过重复节点: US_1 | ⬇️ 3.0MB/s (208.87.242.77:35000)
...
🔍 开始检测 237 个节点的端口可达性...
✅ 端口检测完成！有效节点: 134, 移除节点: 103
✅ 已保存 134 个节点到 clash_config.yaml
📋 配置包含: 7 个代理组
```

### 转换远程订阅

```bash
# 转换远程订阅 URL
python uri2clash.py --url "https://example.com/subscription.txt" --output clash_config_from_url.yaml
```

### 跳过端口检测

```bash
# 跳过端口检测，保留所有解析成功的节点
python uri2clash.py --input url_sample.txt --output clash_config_all.yaml --skip-port-check

# 输出结果示例
📥 从文件加载节点: url_sample.txt
🔍 发现 237 个节点
...
⏭️  跳过端口检测，保留所有 237 个解析成功的节点
✅ 已保存 237 个节点到 clash_config_all.yaml
📋 配置包含: 8 个代理组
```

## 🎨 生成的配置结构

生成的 Clash 配置包含以下部分：

1. **基础配置**：端口设置、日志级别、TUN 模式等
2. **代理节点**：所有解析成功的代理节点
3. **代理组**：
   - 🚀 节点选择（主节点选择组）
   - 🇺🇸 美国节点（按国家分组）
   - 🇭🇰 香港节点（按国家分组）
   - 🇯🇵 日本节点（按国家分组）
   - 🌐 其他节点（按国家分组）
   - 📺 流媒体（专用代理组）
   - 🌍 全球直连（专用代理组）
   - 🛡️ 隐私保护（专用代理组）
4. **规则配置**：常用网站和服务的分流规则

## 📋 配置验证

使用项目根目录下的验证工具验证生成的配置文件：

```bash
python ../validate/validate_clash_yaml.py clash_config.yaml
```

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：
- 提交 Issue
- 发送邮件

---

**版本**: v1.0.0
**更新日期**: 2023-12-18
**开发团队**: Clash Config Tool Team
