import urllib.parse
import base64
import json

def parse_hysteria2(uri: str) -> dict:
    body = uri[len("hysteria2://"):]
    userinfo, rest = body.split("@", 1)
    hostport, query_fragment = rest.split("?", 1)
    query, fragment = query_fragment.split("#", 1)

    server, port = hostport.split(":")
    # 移除端口号中可能存在的斜杠字符
    port = port.rstrip('/')
    params = urllib.parse.parse_qs(query)
    name = urllib.parse.unquote(fragment)

    return {
        "name": name,
        "type": "hysteria2",
        "server": server,
        "port": int(port),
        "auth-str": userinfo,
        "sni": params.get("sni", [""])[0],
        "skip-cert-verify": params.get("insecure", ["0"])[0] == "1"
    }

def parse_ss(uri: str) -> dict:
    body = uri[len("ss://"):]
    base, rest = body.split("@", 1)
    serverport, fragment = rest.split("#", 1)
    server, port = serverport.split(":")
    # 移除端口号中可能存在的斜杠字符
    port = port.rstrip('/')

    name = urllib.parse.unquote(fragment)
    return {
        "name": name,
        "type": "ss",
        "server": server,
        "port": int(port),
        "cipher": "aes-128-gcm",
        "password": "REDACTED"
    }

def parse_vless(uri: str) -> dict:
    body = uri[len("vless://"):]
    userinfo, rest = body.split("@", 1)
    hostport, query_fragment = rest.split("?", 1)
    query, fragment = query_fragment.split("#", 1)

    server, port = hostport.split(":")
    # 移除端口号中可能存在的斜杠字符
    port = port.rstrip('/')
    params = urllib.parse.parse_qs(query)
    name = urllib.parse.unquote(fragment)

    return {
        "name": name,
        "type": "vless",
        "server": server,
        "port": int(port),
        "uuid": userinfo,
        "security": params.get("security", ["auto"])[0],
        "encryption": params.get("encryption", ["none"])[0],
        "flow": params.get("flow", [""])[0],
        "sni": params.get("sni", [""])[0],
        "fp": params.get("fp", [""])[0],
        "pbk": params.get("pbk", [""])[0],
        "network": params.get("type", ["tcp"])[0],
        "header": params.get("headerType", ["none"])[0]
    }

def parse_vmess(uri: str) -> dict:
    body = uri[len("vmess://"):]
    try:
        decoded = base64.b64decode(body + '=' * (-len(body) % 4)).decode("utf-8")
        data = json.loads(decoded)
    except Exception as e:
        raise ValueError(f"vmess base64 解码失败: {e}")

    return {
        "name": data.get("ps", "vmess"),
        "type": "vmess",
        "server": data["add"],
        "port": int(data["port"]),
        "uuid": data["id"],
        "alterId": int(data.get("aid", 0)),
        "cipher": "auto",
        "network": data.get("net", "tcp"),
        "tls": bool(data.get("tls", "")),
        "host": data.get("host", ""),
        "path": data.get("path", ""),
        "sni": data.get("sni", ""),
        "udp": True
    }

def parse_trojan(uri: str) -> dict:
    body = uri[len("trojan://"):]
    userinfo, rest = body.split("@", 1)
    hostport, query_fragment = rest.split("?", 1)
    query, fragment = query_fragment.split("#", 1)

    server, port = hostport.split(":")
    # 移除端口号中可能存在的斜杠字符
    port = port.rstrip('/')
    params = urllib.parse.parse_qs(query)
    name = urllib.parse.unquote(fragment)

    return {
        "name": name,
        "type": "trojan",
        "server": server,
        "port": int(port),
        "password": userinfo,
        "security": params.get("security", ["tls"])[0],
        "sni": params.get("sni", [""])[0],
        "fp": params.get("fp", [""])[0],
        "skip-cert-verify": params.get("allowInsecure", ["0"])[0] == "1",
        "type-tcp": params.get("type", ["tcp"])[0],
        "header-type": params.get("headerType", ["none"])[0]
    }

def parse_uri(uri: str) -> dict:
    if uri.startswith("hysteria2://"):
        return parse_hysteria2(uri)
    elif uri.startswith("ss://"):
        return parse_ss(uri)
    elif uri.startswith("vless://"):
        return parse_vless(uri)
    elif uri.startswith("vmess://"):
        return parse_vmess(uri)
    elif uri.startswith("trojan://"):
        return parse_trojan(uri)
    else:
        raise ValueError(f"Unsupported URI type: {uri}")
