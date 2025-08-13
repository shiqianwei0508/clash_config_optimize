#!/usr/bin/env python3
import argparse
import glob
from clash_optimizer.resolver import ProxyResolver
from clash_optimizer.geoip import GeoIPClassifier
from clash_optimizer.proxy_manager import ProxyManager
from clash_optimizer.config_builder import ConfigBuilder
from clash_optimizer.utils import load_yaml, save_yaml, print_summary, merge_configs, generate_whitelist_rules, merge_rules
from clash_optimizer.constants import group_keywords, whitelist_domains


def parse_args():
    parser = argparse.ArgumentParser(description="🛠️ Clash YAML 多文件合并优化工具")
    parser.add_argument("--clashconfig", nargs="+", required=True, help="多个原始配置路径")
    parser.add_argument("--newconfig", default="config.yaml", help="输出配置路径（默认：config.yaml）")
    return parser.parse_args()


def expand_glob_patterns(patterns):
    expanded = []
    for pattern in patterns:
        matched = glob.glob(pattern)
        if not matched:
            print(f"❌ 未匹配到文件：{pattern}")
            continue
        expanded.extend(matched)
    return expanded


def main():
    args = parse_args()
    paths = expand_glob_patterns(args.clashconfig)
    configs = [load_yaml(p) for p in paths]
    base_config = merge_configs(configs)

    resolver = ProxyResolver()
    geoip = GeoIPClassifier("mmdb/GeoLite2-Country.mmdb")
    manager = ProxyManager(resolver, geoip)

    proxies = manager.dedupe(base_config.get("proxies", []))
    proxies = manager.rename_by_geoip(proxies)
    base_config["proxies"] = proxies

    builder = ConfigBuilder(proxies, manager.group_by_keywords(proxies, group_keywords))
    builder.override_base_config(base_config)
    base_config["proxy-groups"] = builder.build_proxy_groups()

    # 合并并去重 rules
    existing_rules = base_config.get("rules", [])
    whitelist_rules = generate_whitelist_rules(whitelist_domains)
    base_config["rules"] = merge_rules(existing_rules, whitelist_rules)

    save_yaml(base_config, args.newconfig)
    print_summary(base_config)


if __name__ == "__main__":
    main()
