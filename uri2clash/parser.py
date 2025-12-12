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

    # 解码 base64 编码的认证信息
    try:
        decoded_auth = base64.b64decode(base + '=' * (-len(base) % 4)).decode("utf-8")
        if ':' in decoded_auth:
            cipher, password = decoded_auth.split(':', 1)
        else:
            # 处理旧格式
            cipher = "aes-128-gcm"
            password = decoded_auth
    except Exception:
        # 如果解码失败，使用默认值
        cipher = "aes-128-gcm"
        password = base

    name = urllib.parse.unquote(fragment)
    return {
        "name": name,
        "type": "ss",
        "server": server,
        "port": int(port),
        "cipher": cipher,
        "password": password
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
    
    # 处理没有查询参数的情况
    if "?" in rest:
        hostport, query_fragment = rest.split("?", 1)
        if "#" in query_fragment:
            query, fragment = query_fragment.split("#", 1)
        else:
            query = query_fragment
            fragment = ""
    elif "#" in rest:
        hostport, fragment = rest.split("#", 1)
        query = ""
    else:
        hostport = rest
        query = ""
        fragment = ""

    server, port = hostport.split(":")
    # 移除端口号中可能存在的斜杠字符
    port = port.rstrip('/')
    params = urllib.parse.parse_qs(query)
    name = urllib.parse.unquote(fragment) if fragment else f"{server}:{port}"

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
        "network": params.get("type", ["tcp"])[0],
        "header-type": params.get("headerType", ["none"])[0]
    }

def parse_ssr(uri: str) -> dict:
    """解析ShadowsocksR (ssr://) URI"""
    body = uri[len("ssr://"):]
    
    # 解码base64编码的主体部分
    try:
        # 使用urlsafe_b64decode自动处理URL安全编码和填充
        decoded_body = base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)).decode("utf-8")
    except Exception as e:
        raise ValueError(f"ssr base64 解码失败: {e}")
    
    # 分割URI主体部分
    # 格式：服务器:端口:协议:加密:混淆:密码?参数#备注
    main_part = decoded_body
    query_part = ""
    name = "ssr"
    
    # 处理查询参数和名称
    if "?" in main_part:
        main_part, query_part = main_part.split("?", 1)
        if "#" in query_part:
            query_part, name_part = query_part.split("#", 1)
            name = urllib.parse.unquote(name_part)
    elif "#" in main_part:
        main_part, name_part = main_part.split("#", 1)
        name = urllib.parse.unquote(name_part)
    
    # 分割主要部分
    try:
        server, port, protocol, cipher, obfs, password_part = main_part.split(":", 5)
        
        # 处理密码部分，移除可能的路径分隔符
        if "/" in password_part:
            password_part = password_part.split("/", 1)[0]
    except ValueError:
        raise ValueError(f"ssr URI 格式错误: {decoded_body}")
    
    # 解码密码
    try:
        password = base64.urlsafe_b64decode(password_part + '=' * (-len(password_part) % 4)).decode("utf-8")
    except Exception as e:
        raise ValueError(f"ssr 密码 base64 解码失败: {e}")
    
    # 解析查询参数
    params = urllib.parse.parse_qs(query_part)
    
    return {
        "name": name,
        "type": "ssr",
        "server": server,
        "port": int(port),
        "protocol": protocol,
        "cipher": cipher,
        "obfs": obfs,
        "password": password,
        "obfs-param": params.get("obfsparam", [""])[0],
        "protocol-param": params.get("protoparam", [""])[0],
        "group": params.get("group", [""])[0],
        "udp": True
    }

def parse_uri(uri: str) -> dict:
    if uri.startswith("hysteria2://"):
        return parse_hysteria2(uri)
    elif uri.startswith("ss://"):
        return parse_ss(uri)
    elif uri.startswith("ssr://"):
        return parse_ssr(uri)
    elif uri.startswith("vless://"):
        return parse_vless(uri)
    elif uri.startswith("vmess://"):
        return parse_vmess(uri)
    elif uri.startswith("trojan://"):
        return parse_trojan(uri)
    else:
        raise ValueError(f"Unsupported URI type: {uri}")
