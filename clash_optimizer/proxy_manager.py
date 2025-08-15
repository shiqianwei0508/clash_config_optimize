import ipaddress


class ProxyManager:
    def __init__(self, resolver, geoip):
        self.resolver = resolver
        self.geoip = geoip

    def is_ip(self, address: str) -> bool:
        try:
            ipaddress.ip_address(address)
            return True
        except ValueError:
            return False

    def detect_country_code(self, proxy: dict) -> str:
        server = proxy.get("server", "")
        ip = server if self.is_ip(server) else self.resolver.resolve(server)
        return self.geoip.get_country_code(ip) if ip else "ZZ"

    def rename_by_geoip(self, proxies: list[dict]) -> list[dict]:
        renamed = []
        country_count = {}
        dropped = 0

        for proxy in proxies:
            server = proxy.get("server", "")
            ip = server if self.is_ip(server) else self.resolver.resolve(server)

            if not ip:
                print(f"🗑️ Dropping node due to DNS failure: {server}")
                dropped += 1
                continue

            code = self.geoip.get_country_code(ip)
            count = country_count.get(code, 1)
            proxy["name"] = f"{code}_{count:02d}"
            renamed.append(proxy)
            country_count[code] = count + 1

        print(f"📊 Dropped {dropped} node(s) due to DNS resolution failure.")
        return renamed

    def dedupe(self, proxies: list[dict], output_file="duplicates.txt") -> list[dict]:
        seen = set()
        deduped = []
        duplicates = []

        for proxy in proxies:
            key = (
                proxy.get("type"),
                proxy.get("server"),
                proxy.get("port"),
                proxy.get("network"),
                proxy.get("servername", "")
            )

            if key not in seen:
                seen.add(key)
                deduped.append(proxy)
            else:
                duplicates.append(proxy)

        if duplicates:
            with open(output_file, "w", encoding="utf-8") as f:
                print(f"🔁 共合并重复节点：{len(duplicates)} 个\n")
                f.write("📋 重复节点如下：\n")
                for dup in duplicates:
                    f.write(f"  - {dup}\n")

        return deduped

    def group_by_keywords(self, proxies: list[dict], keyword_config: dict) -> dict:
        groups = {key: [] for key in keyword_config.keys()}
        for proxy in proxies:
            name = proxy.get("name", "")
            matched = False
            for group, keywords in keyword_config.items():
                if any(k.lower() in name.lower() for k in keywords):
                    groups[group].append(name)
                    matched = True
                    break
            if not matched:
                groups["🧪 其它"].append(name)
        return groups

    def filter_by_type(self, proxies: list[dict], exclude_type: str) -> list[dict]:
        filtered = [p for p in proxies if p.get("type") != exclude_type]
        removed = len(proxies) - len(filtered)
        print(f"🧹 移除 {exclude_type} 节点：{removed} 个")
        return filtered
