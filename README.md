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

---

## 📦 安装依赖

```bash
pip install ruamel.yaml dnspython geoip2
```

GeoIP 数据库请放置于：

```
mmdb/GeoLite2-Country.mmdb
```

你可以从 MaxMind 官网下载免费版本。

---

## 📂 使用方式

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

---

## 🧩 白名单规则插入

你可以在 `constants.py` 中配置白名单域名：

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

## 🧠 项目结构

```
clash_optimizer/
├── main.py                  # CLI 入口
├── resolver.py              # 域名解析
├── geoip.py                 # GeoIP 查询
├── proxy_manager.py         # 节点管理（去重、重命名、过滤）
├── config_builder.py        # 构建 proxy-groups
├── utils.py                 # 通用工具函数
├── constants.py             # 常量配置（关键词、白名单等）
└── mmdb/                    # GeoIP 数据库
```

---

## 📜 License

MIT License

---

