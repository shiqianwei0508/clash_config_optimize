#!/usr/bin/env python3
import argparse
# import os
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
from ruamel.yaml.comments import CommentedMap
from collections import OrderedDict
import glob

# ✅ 分组关键词配置
group_keywords = {
    "🇭🇰 香港": ["HK", "Hong Kong", "HKG", "香港"],
    "🇯🇵 日本": ["JP", "Japan", "Tokyo", "日本"],
    "🇰🇷 韩国": ["KR", "Korea", "韩国"],
    "🇺🇸 美国": ["US", "United States", "美国", "美國", "CA", "Canada", "加拿大"],
    "🇸🇬 新加坡": ["SG", "Singapore", "新加坡"],
    "🇨🇳 中国": ["CN", "China", "中国"],
    "🇪🇺 欧洲": ["EU", "Europe", "欧洲", "DE", "GB", "FR"],
    "🚀 TG代理": ["t.me", "TG", "Telegram", "tg"],
    "📦 Other": ["Other"],
    "🧪 其它": []
}

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(sequence=4, offset=2)


def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.load(f)


def save_yaml(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)


def match_keywords(name, keywords):
    return any(k.lower() in name.lower() for k in keywords)


def group_proxy_names(proxies, keyword_config):
    groups = {key: [] for key in keyword_config.keys()}
    for proxy in proxies:
        name = proxy.get("name", "")
        matched = False
        for group, keywords in keyword_config.items():
            if match_keywords(name, keywords):
                groups[group].append(name)
                matched = True
                break
        if not matched:
            groups["🧪 其它"].append(name)
    return groups


def build_proxy_groups(groups):
    proxy_groups = []

    # 分组选择入口
    proxies_for_entry = [DoubleQuotedScalarString("♻️ 自动选择")]

    for group_name, proxy_names in groups.items():
        if proxy_names:
            proxies_for_entry.append(DoubleQuotedScalarString(group_name))  # url-test 分组
            proxies_for_entry.append(DoubleQuotedScalarString(f"{group_name}🌀"))  # load-balance 分组

    proxy_groups.append({
        "name": "🚀 节点选择",
        "type": "select",
        "proxies": proxies_for_entry
    })

    # 自动选择分组
    all_proxy_names = [name for proxy_list in groups.values() for name in proxy_list]
    proxy_groups.append({
        "name": "♻️ 自动选择",
        "type": "url-test",
        "url": "http://edge.microsoft.com/captiveportal/generate_204",
        "interval": 300,
        "tolerance": 50,
        "proxies": [DoubleQuotedScalarString(name) for name in all_proxy_names]
    })

    # 🌎 地域分组 + 🌐 均衡分组
    for group_name, proxy_names in groups.items():
        if proxy_names:
            proxies = [DoubleQuotedScalarString(name) for name in proxy_names]
            # url-test 分组
            proxy_groups.append({
                "name": f"{group_name}",
                "type": "url-test",
                "url": "http://edge.microsoft.com/captiveportal/generate_204",
                "interval": 300,
                "tolerance": 50,
                "proxies": proxies
            })
            # load-balance 分组（名字加后缀）
            proxy_groups.append({
                "name": f"{group_name}🌀",
                "type": "load-balance",
                "strategy": "round-robin",
                "proxies": proxies
            })

    # 服务入口分组
    services = ["🌍 国外媒体", "Ⓜ️ 微软服务", "🍎 苹果服务", "📲 电报信息"]

    full_refs = [DoubleQuotedScalarString("🚀 节点选择")]
    for group_name, proxy_names in groups.items():
        if proxy_names:
            full_refs.append(DoubleQuotedScalarString(group_name))  # url-test 分组
            full_refs.append(DoubleQuotedScalarString(f"{group_name}🌀"))  # load-balance 分组

    for service in services:
        proxy_groups.append({
            "name": service,
            "type": "select",
            "proxies": full_refs
        })

    # 固定分组
    fixed = [
        ("🎯 全球直连", ["DIRECT", "🚀 节点选择", "♻️ 自动选择"]),
        ("🛑 全球拦截", ["REJECT", "DIRECT"]),
        ("🍃 应用净化", ["REJECT", "DIRECT"]),
        ("🐟 漏网之鱼", ["🚀 节点选择", "🎯 全球直连", "♻️ 自动选择"])
    ]
    for name, proxies in fixed:
        proxy_groups.append({
            "name": name,
            "type": "select",
            "proxies": [DoubleQuotedScalarString(p) for p in proxies]
        })

    return proxy_groups


def override_base_config(config):
    config.pop("mixed-port", None)
    ordered_fields = CommentedMap()
    ordered_fields["port"] = 7890
    ordered_fields["socks-port"] = 7891
    ordered_fields["allow-lan"] = True

    for key in list(ordered_fields.keys()):
        if key in config:
            config.pop(key)

    for k, v in reversed(list(ordered_fields.items())):
        config.insert(0, k, v)

    print("🔧 已重排基础字段：port → socks-port → allow-lan，移除 mixed-port")


def merge_proxies(config_paths):
    all_configs = [load_yaml(p) for p in config_paths]
    proxy_dict = OrderedDict()
    for conf in all_configs:
        for proxy in conf.get("proxies", []):
            name = proxy.get("name")
            if name and name not in proxy_dict:
                proxy_dict[name] = proxy
    base = all_configs[0].copy()
    base["proxies"] = list(proxy_dict.values())
    return base


def dedupe_proxies(proxies, output_file="duplicates.txt"):
    seen = set()
    deduped = []
    duplicates = []

    for proxy in proxies:
        proxy_type = proxy.get("type")
        port = proxy.get("port")

        # 使用不同的去重键
        if proxy_type == "trojan":
            key = (proxy.get("sni"), port, proxy_type)
        else:
            key = (proxy.get("server"), port, proxy_type)

        if key not in seen:
            seen.add(key)
            deduped.append(proxy)
        else:
            duplicates.append(proxy)

    # 写入重复项到文件
    if duplicates:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"🔁 共合并重复节点：{len(duplicates)} 个\n")
            f.write("📋 重复节点如下：\n")
            for dup in duplicates:
                f.write(f"  - {dup}\n")

    return deduped


def main():
    parser = argparse.ArgumentParser(description="🛠️ Clash YAML 多文件合并优化工具")
    parser.add_argument("--clashconfig", nargs="+", required=True, help="多个原始配置路径")
    parser.add_argument("--newconfig", default="config.yaml", help="输出配置路径（默认：config.yaml）")
    args = parser.parse_args()

    # clashconfig 参数值处理
    raw_paths = args.clashconfig
    expanded_paths = []

    for pattern in raw_paths:
        matched = glob.glob(pattern)
        if not matched:
            print(f"❌ 未匹配到文件：{pattern}")
            return
        expanded_paths.extend(matched)

    config = merge_proxies(expanded_paths)

    # 处理 proxies 字段
    proxies = dedupe_proxies(config.get("proxies", []))
    config["proxies"] = proxies

    if not proxies:
        print("⚠️ proxies 字段为空")
        return

    # 覆盖基础配置
    override_base_config(config)

    grouped = group_proxy_names(proxies, group_keywords)
    config["proxy-groups"] = build_proxy_groups(grouped)

    # newconfig 参数值处理
    save_yaml(config, args.newconfig)

    print(f"\n✅ 配置生成成功：{args.newconfig}")
    print(f"📦 分组数：{len(config['proxy-groups'])}")
    for g in config["proxy-groups"]:
        print(f"   - {g['name']}: {len(g.get('proxies', []))} 个节点")


if __name__ == "__main__":
    main()
