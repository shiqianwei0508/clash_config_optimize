from ruamel.yaml.scalarstring import DoubleQuotedScalarString
from ruamel.yaml.comments import CommentedMap
from clash_optimizer.constants import generate_204_url


class ConfigBuilder:
    def __init__(self, proxies: list[dict], groups: dict):
        self.proxies = proxies
        self.groups = groups

    def override_base_config(self, config: dict) -> None:
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

    def build_proxy_groups(self) -> list[dict]:
        proxy_groups = []
        proxies_for_entry = [DoubleQuotedScalarString("♻️ 自动选择")]

        for group_name, proxy_names in self.groups.items():
            if proxy_names:
                proxies_for_entry.append(DoubleQuotedScalarString(group_name))
                proxies_for_entry.append(DoubleQuotedScalarString(f"{group_name}🌀"))

        proxy_groups.append({
            "name": "🚀 节点选择",
            "type": "select",
            "proxies": proxies_for_entry
        })

        all_proxy_names = [name for proxy_list in self.groups.values() for name in proxy_list]
        proxy_groups.append({
            "name": "♻️ 自动选择",
            "type": "url-test",
            "url": generate_204_url,
            "interval": 300,
            "tolerance": 50,
            "proxies": [DoubleQuotedScalarString(name) for name in all_proxy_names]
        })

        for group_name, proxy_names in self.groups.items():
            if proxy_names:
                proxies = [DoubleQuotedScalarString(name) for name in proxy_names]
                proxy_groups.append({
                    "name": group_name,
                    "type": "url-test",
                    "url": generate_204_url,
                    "interval": 300,
                    "tolerance": 50,
                    "proxies": proxies
                })
                proxy_groups.append({
                    "name": f"{group_name}🌀",
                    "type": "load-balance",
                    "url": generate_204_url,
                    "interval": 300,
                    "strategy": "consistent-hashing",
                    "proxies": proxies
                })

        services = ["🌍 国外媒体", "Ⓜ️ 微软服务", "🍎 苹果服务", "📲 电报信息"]
        full_refs = [DoubleQuotedScalarString("🚀 节点选择")]
        for group_name, proxy_names in self.groups.items():
            if proxy_names:
                full_refs.append(DoubleQuotedScalarString(group_name))
                full_refs.append(DoubleQuotedScalarString(f"{group_name}🌀"))

        for service in services:
            proxy_groups.append({
                "name": service,
                "type": "select",
                "proxies": full_refs
            })

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
