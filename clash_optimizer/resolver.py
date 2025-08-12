import dns.resolver

class ProxyResolver:
    def resolve(self, domain: str) -> str | None:
        try:
            answers = dns.resolver.resolve(domain, 'A')
            ip = answers[0].to_text() if answers else None
            return ip
        except Exception as e:
            print(f"❌ Failed to resolve {domain}: {e}")
            return None
