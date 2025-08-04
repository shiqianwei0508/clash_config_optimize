# 🛠️ Clash Config Tool

**clash_config_tool.py** 是一个用于自动优化 Clash YAML 配置文件的 Python 工具。它支持节点自动分组、生成 Proxy-Groups、替换端口设置、重排序配置字段，并保留 YAML 注释结构。

---

## ✨ 功能特点

- ✅ 自动识别节点名称，按国家/服务分类分组
- ♻️ 生成自动测速分组 (`url-test`)
- 🚀 创建统一入口分组 (`select`)
- 🎯 添加常用固定策略分组（如「全球直连」「电报服务」等）
- 🔧 端口配置替换为：`port: 7890` / `socks-port: 7891`
- 📎 删除 `mixed-port` 并重排字段顺序
- 💬 保留原配置文件注释与格式（基于 `ruamel.yaml`）

---

## 📦 安装依赖

本工具基于 [`ruamel.yaml`](https://pypi.org/project/ruamel.yaml/) 实现 YAML 读写操作：

```bash
pip install ruamel.yaml
```

---

## 🚀 使用方法

```bash
python clash_config_tool.py \
  --clashconfig clash.yaml \
  --newconfig clash_optimized.yaml
```

参数说明：

| 参数            | 说明                          |
|-----------------|-------------------------------|
| `--clashconfig` | 原始 Clash 配置文件路径       |
| `--newconfig`   | 输出优化后的配置文件路径      |

执行后将在终端输出分组生成统计，并保存新配置文件到指定路径。

---

## 🧠 节点自动分组逻辑

工具通过关键字匹配将节点分为多个分组，当前内置支持如下国家与服务类型：

| 分组名              | 匹配关键字示例                              |
|---------------------|---------------------------------------------|
| 🇭🇰 HONGKONG         | HK, Hong Kong, HKG, 香港                    |
| 🇯🇵 JAPAN            | JP, Japan, Tokyo, 日本                      |
| 🇰🇷 KOREA            | KR, Korea, 韩国                             |
| 🇺🇸 USA              | US, United States, CA, Canada, 美国, 加拿大 |
| 🇸🇬 SINGAPORE        | SG, Singapore, 新加坡                      |
| 🇨🇳 CHINA            | CN, China, 中国                             |
| 🇪🇺 EUROPE           | EU, Europe, DE, GB, FR, 欧洲                |
| 🚀 TG_PROXY          | TG, Telegram, t.me                          |
| 📦 OTHER / 🧪 MISC    | 无匹配关键词时默认分组                     |

---

## 📁 输出 Proxy-Groups 示例

自动生成的 Proxy-Groups 包含：

- ♻️ 自动选择（全部节点测速）
- 🚀 节点选择（包含所有地域分组）
- 各国分组（如 🇯🇵 JAPAN-group）
- 固定策略分组（🎯 全球直连、🛑 拦截等）
- 服务入口（🌍 国外媒体、Ⓜ️ 微软服务、📲 电报信息）

---

## 🛠️ 配置文件字段优化

该工具会自动设置以下字段，替换原配置中的 `mixed-port`：

```yaml
port: 7890
socks-port: 7891
allow-lan: true
```

上述字段将按顺序插入 YAML 顶部，确保规范性和可读性。


