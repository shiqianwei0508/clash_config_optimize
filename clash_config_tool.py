#!/usr/bin/env python3
import argparse
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
from ruamel.yaml.comments import CommentedMap
import glob
import dns.resolver
import geoip2.database
from geoip2.errors import AddressNotFoundError
import ipaddress

from constants import generate_204_url, group_keywords

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(sequence=4, offset=2)


# 解析域名到 IP 地址
def resolve_domain(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        ip = answers[0].to_text() if answers else None
        # print(f"🔍 Resolved {domain} → {ip}")
        return ip
    except Exception as e:
        print(f"❌ Failed to resolve {domain}: {e}")
        return None


# 初始化 GeoIP2 数据库读取器
reader = geoip2.database.Reader("mmdb/GeoLite2-Country.mmdb")


# 获取 IP 地址对应的国家代码
def get_country_code(ip):
    try:
        response = reader.country(ip)
        code = response.country.iso_code
        # print(f"🌍 {ip} → {code}")
        return code if code else "ZZ"
    except AddressNotFoundError:
        print(f"⚠️ IP not found in GeoIP database: {ip}")
        return "ZZ"
    except Exception as e:
        print(f"❌ GeoIP lookup failed for {ip}: {e}")
        return "ZZ"


# 检查地址是否为有效的 IP 地址
def is_ip(address):
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


def detect_country_code(proxy):
    server = proxy.get("server", "")
    ip = server if is_ip(server) else resolve_domain(server)
    return get_country_code(ip) if ip else "ZZ"


def rename_proxies_by_geoip(proxies):
    renamed = []
    country_count = {}
    dropped = 0

    for proxy in proxies:
        server = proxy.get("server", "")
        ip = server if is_ip(server) else resolve_domain(server)

        if not ip:
            print(f"🗑️ Dropping node due to DNS failure: {server}")
            dropped += 1
            continue  # 跳过该节点

        code = get_country_code(ip)
        count = country_count.get(code, 1)
        proxy["name"] = f"{code}_{count:02d}"
        renamed.append(proxy)
        country_count[code] = count + 1

    print(f"📊 Dropped {dropped} node(s) due to DNS resolution failure.")
    return renamed



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


def group_proxy_names_by_geoip(proxies):
    groups = {key: [] for key in group_keywords.keys()}
    for proxy in proxies:
        code = detect_country_code(proxy)
        matched = False
        for group, keywords in group_keywords.items():
            if code.upper() in [k.upper() for k in keywords]:
                groups[group].append(proxy["name"])
                matched = True
                break
        if not matched:
            groups["🧪 其它"].append(proxy["name"])
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
        "url": generate_204_url,
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
                "url": generate_204_url,
                "interval": 300,
                "tolerance": 50,
                "proxies": proxies
            })
            # load-balance 分组（名字加后缀）
            proxy_groups.append({
                "name": f"{group_name}🌀",
                "type": "load-balance",
                "url": generate_204_url,
                "interval": 300,
                "strategy": "consistent-hashing",
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
    all_proxies = []

    for conf in all_configs:
        all_proxies.extend(conf.get("proxies", []))

    base = all_configs[0].copy()
    base["proxies"] = all_proxies
    return base


def rename_proxies(proxies):
    renamed = []
    name_count = {}

    for proxy in proxies:
        name = proxy.get("name", "")
        prefix = name.split(" |")[0] if " |" in name else name
        count = name_count.get(prefix, 1)

        new_name = f"{prefix} | #{count}"
        proxy["name"] = new_name
        renamed.append(proxy)

        name_count[prefix] = count + 1

    return renamed


def dedupe_proxies(proxies, output_file="duplicates.txt"):
    seen = set()
    deduped = []
    duplicates = []

    for proxy in proxies:
        proxy_type = proxy.get("type")
        proxy_port = proxy.get("port")
        proxy_server = proxy.get("server")
        proxy_network = proxy.get("network")

        # 使用不同的去重键
        # if proxy_type == "trojan":
        #     key = (proxy.get("sni"), proxy_port, proxy_type)
        # else:
        #     key = (proxy.get("server"), proxy_port, proxy_type)
        key = (proxy_type, proxy_server, proxy_port, proxy_network)

        if key not in seen:
            seen.add(key)
            deduped.append(proxy)
        else:
            duplicates.append(proxy)

    # 写入重复项到文件
    if duplicates:
        with open(output_file, "w", encoding="utf-8") as f:
            # f.write(f"🔁 共合并重复节点：{len(duplicates)} 个\n")
            print(f"🔁 共合并重复节点：{len(duplicates)} 个\n")
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

    # 更细致地去重（非仅靠 name）
    proxies = dedupe_proxies(config.get("proxies", []))

    # ✅ 重命名所有节点，避免 name 冲突
    # proxies = rename_proxies(proxies)
    proxies = rename_proxies_by_geoip(proxies)

    config["proxies"] = proxies

    if not proxies:
        print("⚠️ proxies 字段为空")
        return

    # 覆盖基础配置
    override_base_config(config)

    grouped = group_proxy_names(proxies, group_keywords)
    # grouped = group_proxy_names_by_geoip(proxies)

    config["proxy-groups"] = build_proxy_groups(grouped)

    # newconfig 参数值处理
    save_yaml(config, args.newconfig)

    print(f"\n✅ 配置生成成功：{args.newconfig}")
    print(f"📦 分组数：{len(config['proxy-groups'])}")
    for g in config["proxy-groups"]:
        print(f"   - {g['name']}: {len(g.get('proxies', []))} 个节点")


if __name__ == "__main__":
    main()
