#!/usr/bin/env python3
import argparse
from ruamel.yaml import YAML
from collections import defaultdict

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.load(f)

def save_yaml(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

def detect_duplicates(proxies):
    endpoint_map = defaultdict(list)
    for i, proxy in enumerate(proxies):
        server = proxy.get("server")
        port = proxy.get("port")
        type_ = proxy.get("type")
        if server is not None and port is not None and type_ is not None:
            key = f"{server}:{port}:{type_}"
            endpoint_map[key].append(i)
    return {key: idxs for key, idxs in endpoint_map.items() if len(idxs) > 1}

# def dedupe_proxies(proxies):
#     seen = set()
#     deduped = []
#     for proxy in proxies:
#         server = proxy.get("server")
#         port = proxy.get("port")
#         type_ = proxy.get("type")
#         if server is not None and port is not None and type_ is not None:
#             key = f"{server}:{port}:{type_}"
#             if key in seen:
#                 continue
#             seen.add(key)
#         deduped.append(proxy)
#     return deduped

def main():
    parser = argparse.ArgumentParser(description="🔍 Clash 配置重复节点检测与去重工具（按 server:port:type）")
    parser.add_argument("--config", required=True, help="Clash YAML 配置路径")
    # parser.add_argument("--dedupe", action="store_true", help="启用去重并覆盖原文件")
    args = parser.parse_args()

    try:
        config = load_yaml(args.config)
    except Exception as e:
        print(f"❌ 加载 YAML 失败: {e}")
        return

    proxies = config.get("proxies", [])
    if not proxies:
        print("⚠️ proxies 字段不存在或为空")
        return

    duplicates = detect_duplicates(proxies)
    if not duplicates:
        print("✅ 未发现重复 server:port:type 节点")
    else:
        print(f"⚠️ 发现 {len(duplicates)} 个重复 server:port:type 节点：")
        for key, idxs in duplicates.items():
            print(f"   - '{key}' 出现了 {len(idxs)} 次，位置索引：{idxs}")

        # if args.dedupe:
        #     print("✂️ 正在去重并更新配置文件...")
        #     config["proxies"] = dedupe_proxies(proxies)
        #     save_yaml(config, args.config)
        #     print(f"✅ 已去重并保存到原文件：{args.config}")

if __name__ == "__main__":
    main()
