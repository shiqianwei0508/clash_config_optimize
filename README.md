# 🛠️ Clash YAML 多文件合并优化工具

一个用于合并多个 Clash 配置文件、去重代理节点、智能分组并生成优化后的 YAML 配置的 Python 工具。支持节点重命名、地域分组、服务入口构建，适用于 Clash、Clash.Meta 等客户端。

---

## 🚀 功能特性

- ✅ 支持多个 YAML 文件合并为一个配置
- ✅ 基于 `(server, port, type)` 或 `(sni, port, type)` 去重代理节点
- ✅ 自动重命名节点，避免 name 冲突
- ✅ 按国家/地区关键词智能分组
- ✅ 构建 `select`, `url-test`, `load-balance` 等多种分组类型
- ✅ 自动生成服务入口分组（如 Telegram、Apple、Microsoft）
- ✅ 输出重复节点到 `duplicates.txt` 文件
- ✅ 可配置输出路径，默认生成 `config.yaml`

---

## 📦 安装依赖

```bash
pip install ruamel.yaml
```

---

## 📂 使用方法

```bash
python clash_config_tool.py --clashconfig <配置文件1.yaml> <配置文件2.yaml> ... --newconfig <输出文件路径>
```

### ✅ 示例命令

```bash
python clash_config_tool.py --clashconfig configs/08*.yaml configs/09*.yaml --newconfig merged.yaml
```

> 支持通配符匹配，自动展开多个文件。

---

## 🧾 参数说明

| 参数名         | 类型       | 说明 |
|----------------|------------|------|
| `--clashconfig` | `list[str]` | 一个或多个原始 Clash 配置文件路径，支持通配符 |
| `--newconfig`   | `str`       | 输出配置文件路径，默认为 `config.yaml` |

---

## 🧠 去重逻辑说明

- 对非 `trojan` 节点：使用 `(server, port, type)` 去重
- 对 `trojan` 节点：使用 `(sni, port, type)` 去重
- 所有重复节点将写入 `duplicates.txt` 文件，供人工审查

---

## 🧩 节点重命名策略

将所有节点按前缀进行编号，避免 name 冲突：

```yaml
🇺🇸US_1 | #1
🇺🇸US_1 | #2
```

---

## 🌍 分组关键词配置

内置地域关键词自动分组：

```python
group_keywords = {
  "🇭🇰 香港": ["HK", "Hong Kong", "HKG", "香港"],
  "🇯🇵 日本": ["JP", "Japan", "Tokyo", "日本"],
  ...
}
```

---

## 📐 输出结构说明

生成的配置包含以下分组：

- `🚀 节点选择`：入口选择分组
- `♻️ 自动选择`：测速自动选择分组
- `🇺🇸 美国`, `🇯🇵 日本` 等地域分组（`url-test` + `load-balance`）
- `🌍 国外媒体`, `Ⓜ️ 微软服务` 等服务入口分组
- `🎯 全球直连`, `🛑 全球拦截` 等固定策略分组

---

## 📄 输出文件示例

- `merged.yaml`：合并后的 Clash 配置文件
- `duplicates.txt`：被识别为重复的节点列表

---

## 🧪 推荐使用场景

- 多个 Clash 配置文件合并优化
- 节点去重与重命名
- 自动构建分组与服务入口
- 适配 Clash.Meta、Clash Verge 等高级客户端

---

## 📬 联系与反馈

如需定制功能或报告问题，请提交 Issue 或联系维护者。

