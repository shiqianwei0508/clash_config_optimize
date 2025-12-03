import sys
from ruamel.yaml import YAML
from ruamel.yaml.constructor import ConstructorError

REQUIRED_FIELDS = ['proxies', 'proxy-groups', 'rules']

# 不同代理类型的必填字段
PROXY_TYPE_REQUIRED_FIELDS = {
    'vmess': ['name', 'type', 'server', 'port', 'uuid'],
    'vless': ['name', 'type', 'server', 'port', 'uuid'],
    'trojan': ['name', 'type', 'server', 'port', 'password'],
    'ss': ['name', 'type', 'server', 'port', 'cipher', 'password'],
    'hysteria2': ['name', 'type', 'server', 'port', 'auth-str']
}

# 不同代理类型的可选字段
PROXY_TYPE_OPTIONAL_FIELDS = {
    'vmess': ['alterId', 'cipher', 'network', 'tls', 'host', 'path', 'sni', 'udp'],
    'vless': ['security', 'encryption', 'flow', 'sni', 'fp', 'pbk', 'network', 'header'],
    'trojan': ['security', 'sni', 'fp', 'skip-cert-verify', 'type-tcp', 'header-type'],
    'ss': ['plugin', 'plugin-opts'],
    'hysteria2': ['sni', 'skip-cert-verify', 'alpn', 'auth-str', 'obfs', 'obfs-password', 'upmbps', 'downmbps']
}

def validate_proxies(proxies):
    """验证代理节点列表"""
    if not isinstance(proxies, list):
        print("[❌ 配置错误] proxies 必须是列表类型。")
        return False
    
    if not proxies:
        print("[⚠️ 警告] proxies 列表为空。")
    
    valid_count = 0
    invalid_count = 0
    unknown_type_count = 0
    
    for idx, proxy in enumerate(proxies):
        if not isinstance(proxy, dict):
            print(f"[❌ 代理节点错误] 第{idx+1}个代理节点不是字典类型。")
            invalid_count += 1
            continue
        
        if 'name' not in proxy:
            print(f"[❌ 代理节点错误] 第{idx+1}个代理节点缺少 'name' 字段。")
            invalid_count += 1
            continue
        
        proxy_name = proxy.get('name', f"第{idx+1}个节点")
        
        if 'type' not in proxy:
            print(f"[❌ 代理节点错误] {proxy_name} 缺少 'type' 字段。")
            invalid_count += 1
            continue
        
        proxy_type = proxy['type']
        
        # 验证代理类型
        if proxy_type not in PROXY_TYPE_REQUIRED_FIELDS:
            print(f"[⚠️ 未知代理类型] {proxy_name}: {proxy_type} (跳过详细验证)")
            unknown_type_count += 1
            continue
        
        # 检查必填字段
        missing_required = [field for field in PROXY_TYPE_REQUIRED_FIELDS[proxy_type] if field not in proxy]
        if missing_required:
            print(f"[❌ 代理节点错误] {proxy_name} 缺少必填字段: {', '.join(missing_required)}")
            invalid_count += 1
            continue
        
        # 验证服务器和端口格式
        if not isinstance(proxy.get('server'), str) or not proxy['server']:
            print(f"[❌ 代理节点错误] {proxy_name} 的 'server' 字段必须是非空字符串。")
            invalid_count += 1
            continue
        
        port = proxy.get('port')
        if not isinstance(port, int) or port <= 0 or port > 65535:
            print(f"[❌ 代理节点错误] {proxy_name} 的 'port' 字段必须是 1-65535 之间的整数。")
            invalid_count += 1
            continue
        
        # 检查未知字段（仅警告）
        all_valid_fields = PROXY_TYPE_REQUIRED_FIELDS[proxy_type] + PROXY_TYPE_OPTIONAL_FIELDS[proxy_type]
        unknown_fields = [field for field in proxy if field not in all_valid_fields]
        if unknown_fields:
            print(f"[⚠️ 未知字段] {proxy_name}: {', '.join(unknown_fields)}")
        
        valid_count += 1
    
    print(f"\n[📊 代理节点统计]")
    print(f"  有效节点数: {valid_count}")
    print(f"  无效节点数: {invalid_count}")
    print(f"  未知类型节点数: {unknown_type_count}")
    
    return invalid_count == 0

def validate_proxy_groups(proxy_groups):
    """验证代理组配置"""
    if not isinstance(proxy_groups, list):
        print("[❌ 配置错误] proxy-groups 必须是列表类型。")
        return False
    
    if not proxy_groups:
        print("[⚠️ 警告] proxy-groups 列表为空。")
        return True
    
    for idx, group in enumerate(proxy_groups):
        if not isinstance(group, dict):
            print(f"[❌ 代理组错误] 第{idx+1}个代理组不是字典类型。")
            return False
        
        required = ['name', 'type', 'proxies']
        missing = [field for field in required if field not in group]
        if missing:
            group_name = group.get('name', f"第{idx+1}个代理组")
            print(f"[❌ 代理组错误] {group_name} 缺少必填字段: {', '.join(missing)}")
            return False
        
        if not isinstance(group['proxies'], list):
            group_name = group['name']
            print(f"[❌ 代理组错误] {group_name} 的 'proxies' 必须是列表类型。")
            return False
    
    print(f"[✅ 代理组验证成功] 共有 {len(proxy_groups)} 个代理组")
    return True

def validate_rules(rules):
    """验证规则配置"""
    if not isinstance(rules, list):
        print("[❌ 配置错误] rules 必须是列表类型。")
        return False
    
    if not rules:
        print("[⚠️ 警告] rules 列表为空。")
        return True
    
    valid_rule_types = ['DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'IP-CIDR', 'IP-CIDR6', 
                      'SRC-IP-CIDR', 'GEOIP', 'DST-PORT', 'SRC-PORT', 'TYPE', 'RULE-SET', 
                      'MATCH', 'PROCESS-NAME', 'PROCESS-PATH', 'NETWORK']
    
    invalid_rule_count = 0
    for idx, rule in enumerate(rules):
        if not isinstance(rule, str):
            print(f"[❌ 规则错误] 第{idx+1}个规则必须是字符串类型。")
            invalid_rule_count += 1
            continue
        
        parts = rule.split(',')
        if len(parts) < 2:
            print(f"[❌ 规则错误] 第{idx+1}个规则格式错误: {rule}")
            invalid_rule_count += 1
            continue
        
        rule_type = parts[0]
        if rule_type not in valid_rule_types:
            print(f"[⚠️ 未知规则类型] 第{idx+1}个规则: {rule_type}")
    
    if invalid_rule_count > 0:
        print(f"[❌ 规则验证失败] 共有 {invalid_rule_count} 个无效规则")
        return False
    
    print(f"[✅ 规则验证成功] 共有 {len(rules)} 条规则")
    return True

def validate_clash_yaml(file_path):
    """验证Clash YAML配置文件"""
    print(f"[🔍 开始验证配置文件: {file_path}]")
    
    yaml = YAML(typ='safe')  # Safe模式只加载标准类型，防止任意代码执行
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f)
    except ConstructorError as e:
        print(f"[❌ YAML构造异常] {e}")
        return False
    except Exception as e:
        print(f"[❌ 加载失败] {e}")
        return False

    if not isinstance(config, dict):
        print("[❌ 配置文件格式错误] 根结构应为字典类型。")
        return False

    # 验证必填字段
    missing = [key for key in REQUIRED_FIELDS if key not in config]
    if missing:
        print(f"[⚠️ 缺失字段] 配置文件缺少关键字段: {', '.join(missing)}")
        return False
    
    # 详细验证各个部分
    print("\n[📋 开始详细验证]")
    
    # 验证proxies
    print("\n[🔧 验证代理节点]")
    proxies_valid = validate_proxies(config.get('proxies', []))
    
    # 验证proxy-groups
    print("\n[🔧 验证代理组]")
    groups_valid = validate_proxy_groups(config.get('proxy-groups', []))
    
    # 验证rules
    print("\n[🔧 验证规则]")
    rules_valid = validate_rules(config.get('rules', []))
    
    # 验证其他可选但重要的字段
    print("\n[🔧 验证其他配置项]")
    if 'port' not in config:
        print("[⚠️ 警告] 未配置代理端口(port)")
    if 'socks-port' not in config:
        print("[⚠️ 警告] 未配置SOCKS5端口(socks-port)")
    if 'redir-port' not in config:
        print("[⚠️ 警告] 未配置透明代理端口(redir-port)")
    if 'tproxy-port' not in config:
        print("[⚠️ 警告] 未配置TPROXY端口(tproxy-port)")
    if 'allow-lan' not in config:
        print("[⚠️ 警告] 未配置是否允许局域网访问(allow-lan)")
    if 'mode' not in config:
        print("[⚠️ 警告] 未配置运行模式(mode)")
    
    # 总体验证结果
    if proxies_valid and groups_valid and rules_valid:
        print("\n[✅ 配置文件验证成功] 所有必需字段齐全，格式正确。")
        return True
    else:
        print("\n[❌ 配置文件验证失败] 请修复上述错误。")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python validate_clash_yaml.py xxx.yaml")
        sys.exit(1)

    yaml_path = sys.argv[1]
    valid = validate_clash_yaml(yaml_path)
    if not valid:
        sys.exit(1)
