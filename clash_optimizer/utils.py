from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(sequence=4, offset=2)

def load_yaml(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.load(f)

def save_yaml(data: dict, path: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

def merge_configs(configs: list[dict]) -> dict:
    all_proxies = []
    for conf in configs:
        all_proxies.extend(conf.get("proxies", []))
    base = configs[0].copy()
    base["proxies"] = all_proxies
    return base

def print_summary(config: dict) -> None:
    print(f"\n✅ 配置生成成功")
    print(f"📦 分组数：{len(config['proxy-groups'])}")
    for g in config["proxy-groups"]:
        print(f"   - {g['name']}: {len(g.get('proxies', []))} 个节点")


def generate_whitelist_rules(domains: list[str]) -> list[str]:
    return [f"DOMAIN-SUFFIX,{domain},🎯 全球直连" for domain in domains]

def merge_rules(existing: list[str], extra: list[str]) -> list[str]:
    combined = existing + extra
    # 去重并保持顺序
    seen = set()
    deduped = []
    for rule in combined:
        if rule not in seen:
            seen.add(rule)
            deduped.append(rule)
    return deduped

