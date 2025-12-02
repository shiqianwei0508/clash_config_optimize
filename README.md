# 🛠️ Clash YAML 多文件合并优化工具

一个用于合并多个 Clash 配置文件、自动重命名节点、按国家分组、去重、规则增强的 Python 工具。支持 GeoIP 分类、白名单规则插入、协议过滤等高级功能。

---

## 🚀 功能特性

- ✅ 合并多个 Clash YAML 配置文件
- ✅ 自动去重代理节点（支持多维度去重）
- ✅ 按 GeoIP 国家代码重命名节点（如 `US_01`, `JP_02`）
- ✅ 按国家或关键词分组生成 `proxy-groups`
- ✅ 自动插入白名单域名规则到 `rules` 字段顶部
- ✅ 支持移除 trojan 类型节点（`--no-trojan`）
- ✅ 保留原有规则并自动去重
- ✅ 提供图形界面（Tkinter 和 PySide6 两个版本）
- ✅ 支持 URI 节点转 Clash YAML 格式
- ✅ 提供配置文件验证工具
- ✅ 支持文本清洗功能

---

## 📦 安装依赖

```bash
pip install ruamel.yaml dnspython geoip2 pyside6
```

GeoIP 数据库请放置于：

```
mmdb/GeoLite2-Country.mmdb
```

你可以从 MaxMind 官网下载免费版本。

---

## 📂 使用方式

### 1. 命令行工具

```bash
python main.py \
  --clashconfig configs/*.yaml \
  --newconfig merged.yaml \
  --no-trojan
```

### 参数说明：

| 参数             | 说明                                       |
|------------------|--------------------------------------------|
| `--clashconfig`  | 输入的多个配置文件路径（支持通配符）       |
| `--newconfig`    | 输出的合并配置文件路径（默认：`config.yaml`） |
| `--no-trojan`    | 移除所有 `trojan` 类型节点（可选）         |

### 2. 图形界面

#### Tkinter 版本
```bash
python main_ui.py
```

#### PySide6 版本（推荐，功能更丰富）
```bash
python main_ui_pyside6.py
```

### 3. URI 转 Clash YAML

#### 基本功能
- 支持从文件或URL获取节点列表
- 自动处理重复节点名称（同名不同服务器时添加编号后缀）
- 支持Hysteria2、Trojan、Vless、VMess等多种协议
- 自动生成完整的Clash配置（含代理组、规则）
- 规则使用无需额外数据库的格式（避免"rule set not found"错误）
- 双界面支持：提供命令行和 PySide6 GUI 两种使用方式

#### 使用方法

##### 命令行模式

```bash
# 从文件生成配置
python uri2clash/uri2clash.py --input uris.txt --output converted.yaml

# 从URL生成配置
python uri2clash/uri2clash.py --url "https://example.com/nodes.txt" --output subscription.yaml
```

##### GUI 图形界面模式

```bash
python uri2clash_gui.py
```

**GUI 功能特点**：
- 直观的输入选择（文件/URL）
- 便捷的文件浏览选择
- 实时转换日志显示
- 进度条实时反馈
- 友好的操作提示
- 支持转换结果通知

#### 参数说明

| 参数             | 说明                                       |
|------------------|--------------------------------------------|
| `--input`        | 包含 URI 节点的文本文件路径（与--url二选一）|
| `--url`          | 包含 URI 节点的 URL 地址（与--input二选一）|
| `--output`       | 输出的 Clash YAML 文件路径（默认：converted.yaml） |

#### 支持的协议
- ✅ Hysteria2
- ✅ Trojan
- ✅ Vless
- ✅ VMess
- ✅ Shadowsocks

#### 生成的配置内容

1. **基础配置**：
   - 混合端口：7890
   - SOCKS端口：7891
   - Redir端口：7892
   - 规则模式：Rule

2. **代理组**：
   - 🚀 节点选择（默认使用）
   - 🇺🇸 美国节点
   - 🇭🇰 香港节点
   - 🇯🇵 日本节点
   - 🌐 其他节点
   - 📺 流媒体（适配YouTube/Netflix等）
   - 🌍 全球直连
   - 🛡️ 隐私保护

3. **规则**：
   - Telegram相关域名规则
   - 流媒体平台规则
   - 国内应用直连规则
   - 国内IP直连规则
   - 完整的默认规则链

### 4. 配置文件验证

```bash
python validate_clash_yaml.py config.yaml
```

### 5. 文本清洗工具

```bash
python txt_cleaner.py input.txt output.txt
```

### 6. 重复节点检测

```bash
python detect_duplicate_proxies.py --config config.yaml
```

---

## 🧩 白名单规则插入

你可以在 `clash_optimizer/constants.py` 中配置白名单域名：

```python
whitelist_domains = [
    "gbim.vip",
    "corp.local",
    "internal.net"
]
```

这些域名将自动生成如下规则并插入到配置顶部：

```yaml
rules:
  - DOMAIN-SUFFIX,gbim.vip,🎯 全球直连
  - DOMAIN-SUFFIX,corp.local,🎯 全球直连
```

---

## 📁 项目结构与文件说明

### 根目录文件

| 文件名 | 说明 |
|--------|------|
| `main.py` | 主命令行入口，用于合并多个 Clash 配置文件、优化节点 |
| `main_ui.py` | Tkinter 图形界面版本，提供基本的配置合并功能 |
| `main_ui_pyside6.py` | PySide6 图形界面版本，功能更丰富，支持加载动画、异步执行等 |
| `build_ui_pyside6.py` | PySide6 UI 打包脚本，用于生成可执行文件 |
| `clash_config_tool.py` | 旧版的 Clash 配置合并工具 |
| `detect_duplicate_proxies.py` | 检测配置文件中重复的代理节点 |
| `txt_cleaner.py` | 中文 TXT 文本清洗工具，替换标点、删除乱码等 |
| `validate_clash_yaml.py` | 验证 Clash YAML 配置文件的语法和关键字段 |

### clash_optimizer 模块

| 文件名 | 说明 |
|--------|------|
| `config_builder.py` | 构建 proxy-groups 的模块，支持多种分组类型 |
| `constants.py` | 常量定义，包括分组关键词、白名单域名、204 检测 URL 等 |
| `geoip.py` | GeoIP 分类模块，根据 IP 获取国家代码 |
| `proxy_manager.py` | 代理节点管理模块，包括去重、重命名、按关键词分组、类型过滤等功能 |
| `resolver.py` | 域名解析模块，将域名解析为 IP 地址 |
| `utils.py` | 通用工具函数，包括 YAML 加载/保存、规则合并、摘要打印等 |

### uri2clash 模块

| 文件名 | 说明 |
|--------|------|
| `uri2clash/parser.py` | URI 解析模块，支持 hysteria2、ss、vless、vmess、trojan 等协议 |
| `uri2clash/uri2clash.py` | URI 转 Clash YAML 的主脚本，支持从文件/URL获取节点，自动生成完整配置 |
| `uri2clash/utils.py` | URI 工具函数，包括加载 URI 文件、从URL下载节点、保存 YAML 等 |
| `uri2clash_gui.py` | PySide6 GUI 界面，提供可视化操作，支持文件/URL输入，实时日志和进度反馈 |

### 静态资源

| 路径 | 说明 |
|------|------|
| `static/pic/loading.gif` | 图形界面中使用的加载动画 GIF |
| `mmdb/` | GeoIP 数据库目录 |

---

## 📝 详细文件功能说明

### 1. 主程序文件

#### `main.py`
- 命令行工具的主入口
- 支持多文件合并、去重、重命名、分组等核心功能
- 支持移除特定类型节点
- 自动生成 proxy-groups
- 合并并去重规则

#### `main_ui.py`
- 基于 Tkinter 的图形界面
- 支持选择多个配置文件
- 支持设置输出路径
- 支持移除 trojan 节点选项
- 提供简单的执行反馈

#### `main_ui_pyside6.py`
- 基于 PySide6 的图形界面（推荐）
- 支持多文件选择和输出路径设置
- 提供加载动画效果
- 异步执行优化任务，避免界面卡顿
- 支持 300 秒超时自动终止
- 更现代化的 UI 设计

### 2. 核心模块

#### `clash_optimizer/config_builder.py`
- 构建 proxy-groups 的核心模块
- 生成多种类型的 proxy-group：
  - 节点选择（select 类型）
  - 自动选择（url-test 类型）
  - 按国家分组（url-test 类型）
  - 负载均衡分组（load-balance 类型）
  - 服务分组（如国外媒体、微软服务等）

#### `clash_optimizer/constants.py`
- 定义分组关键词配置
- 定义白名单域名
- 定义 204 检测 URL

#### `clash_optimizer/geoip.py`
- GeoIP 分类功能
- 使用 MaxMind GeoLite2 数据库
- 根据 IP 地址获取国家代码

#### `clash_optimizer/proxy_manager.py`
- 代理节点管理功能
- 支持多维度去重
- 按 GeoIP 重命名节点
- 按关键词分组
- 支持按类型过滤节点

#### `clash_optimizer/resolver.py`
- 域名解析功能
- 使用 dnspython 库
- 将域名解析为 IP 地址

#### `clash_optimizer/utils.py`
- 通用工具函数
- YAML 文件加载和保存
- 规则合并和去重
- 白名单规则生成
- 配置摘要打印

### 3. 辅助工具

#### `uri2clash/uri2clash.py`
- URI 节点转 Clash YAML 的核心脚本
- 支持从本地文件或远程URL获取节点列表
- 自动处理重复节点名称（同名不同服务器时添加编号后缀）
- 支持多种协议：hysteria2、trojan、ss、vless、vmess
- 自动生成完整的Clash配置：
  - 基础设置（混合端口、SOCKS端口等）
  - 智能代理组（按国家分组、流媒体分组等）
  - 无需额外数据库的规则配置
- 批量转换功能，支持处理大量节点

#### `uri2clash_gui.py`
- PySide6 图形界面脚本，提供可视化 URI 转 Clash 配置操作
- 支持两种输入方式：本地文件和远程 URL
- 提供文件浏览选择功能，方便用户选择输入和输出文件
- 实时显示转换日志，包含节点发现、重复处理、配置生成等信息
- 进度条实时反馈转换进度，让用户了解当前转换状态
- 转换完成后提供友好的结果通知，支持打开输出文件
- 现代化的 UI 设计，操作直观便捷

#### `validate_clash_yaml.py`
- 验证 Clash 配置文件的语法
- 检查关键字段是否齐全（proxies, proxy-groups, rules）
- 提供详细的错误信息

#### `txt_cleaner.py`
- 中文文本清洗工具
- 替换英文标点为中文标点
- 删除乱码短行
- 支持多种编码格式

#### `detect_duplicate_proxies.py`
- 检测配置文件中重复的代理节点
- 按 server:port:type 维度去重
- 输出重复节点信息

### 4. 打包脚本

#### `build_ui_pyside6.py`
- 使用 Nuitka 打包 PySide6 UI 为可执行文件
- 支持资源文件打包（loading.gif）
- 支持 GeoIP 数据库打包

---

## 🎨 图形界面功能

### PySide6 版本特性
- ✅ 现代化的 UI 设计
- ✅ 支持多文件选择
- ✅ 输出路径自定义
- ✅ 移除 trojan 节点选项
- ✅ 加载动画效果
- ✅ 异步执行，避免界面卡顿
- ✅ 300 秒超时自动终止
- ✅ 详细的执行结果提示

---

## 📜 License

MIT License

---

