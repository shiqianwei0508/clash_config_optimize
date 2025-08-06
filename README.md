
# 🛠️ Clash Config Optimizer

**clash_config_tool.py** 是一个用于优化 Clash 配置文件的 Python 工具，支持多个 YAML 文件合并、节点分组自动识别、基础字段重排、去重代理、生成标准 Proxy-Groups 等功能。

---

## ✨ 功能特色

- ✅ 支持多个 YAML 配置文件合并（只保留第一个文件的基础字段）
- 🔧 自动设置 port / socks-port / allow-lan 字段顺序
- 🚀 节点分组自动识别（按国家、服务关键词匹配）
- ♻️ 自动生成 `proxy-groups`（支持自动选择、分国家区域测速分组）
- 📦 保留 YAML 注释与原始格式（使用 `ruamel.yaml`）

---

## 📦 安装依赖

请先安装 `ruamel.yaml`：

```bash
pip install ruamel.yaml
```

---

## 🚀 命令使用方法

```bash
python clash_config_tool.py \
  --clashconfig config1.yaml config2.yaml config3.yaml \
  --newconfig optimized.yaml
```

| 参数            | 说明                          |
|-----------------|-------------------------------|
| `--clashconfig` | 一个或多个待合并的 YAML 文件 |
| `--newconfig`   | 输出的新 YAML 文件路径       |

---

## 🧩 节点自动分组逻辑

节点根据以下关键字自动分组（按优先匹配）：

| 分组名      | 匹配关键字（包含但不限于）                     |
|-------------|------------------------------------------------|
| 🇭🇰 香港     | HK, Hong Kong, HKG, 香港                       |
| 🇯🇵 日本     | JP, Japan, Tokyo, 日本                         |
| 🇰🇷 韩国     | KR, Korea, 韩国                                |
| 🇺🇸 美国     | US, United States, CA, Canada, 美国, 加拿大    |
| 🇸🇬 新加坡   | SG, Singapore, 新加坡                         |
| 🇨🇳 中国     | CN, China, 中国                                |
| 🇪🇺 欧洲     | EU, Europe, DE, GB, FR, 欧洲                   |
| 🚀 TG代理    | TG, Telegram, t.me                            |
| 📦 其他      | Other                                          |
| 🧪 其它      | 未匹配任何关键词的节点                        |

---

## 📄 Proxy-Groups 自动生成结构

示例结构：

```yaml
proxy-groups:
  - name: 🚀 节点选择
    type: select
    proxies:
      - ♻️ 自动选择
      - 🇭🇰 香港
      - 🇯🇵 日本
      ...

  - name: ♻️ 自动选择
    type: url-test
    proxies:
      - 节点1
      - 节点2
      ...

  - name: 🇭🇰 香港
    type: url-test
    proxies:
      - 节点HK1
      - 节点HK2

  - name: 🌍 国外媒体
    type: select
    proxies:
      - 🚀 节点选择
      - 🇭🇰 香港
      - 🇯🇵 日本
      ...

  - name: 🎯 全球直连
    type: select
    proxies:
      - DIRECT
      - 🚀 节点选择
      - ♻️ 自动选择
```

---

## 🔧 配置字段优化说明

自动设置字段顺序（如存在）：

```yaml
port: 7890
socks-port: 7891
allow-lan: true
```

并删除：

```yaml
mixed-port: (如果存在则移除)
```

---

## ✅ 输出验证提示

运行结束后将输出如下信息：

```
✅ 配置生成成功：optimized.yaml
📦 分组数：12
   - 🚀 节点选择: 10 个节点
   - ♻️ 自动选择: 50 个节点
   ...
```

---

## 📄 许可证

本工具可自由修改与使用，适用于 Clash 配置优化自动化场景。

