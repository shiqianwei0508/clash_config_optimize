import sys
import os
from ruamel.yaml import YAML
from ruamel.yaml.constructor import ConstructorError

REQUIRED_FIELDS = ['proxies', 'proxy-groups', 'rules']

# 不同代理类型的必填字段 - 基于uri2clash/parser.py中的解析逻辑
PROXY_TYPE_REQUIRED_FIELDS = {
    'vmess': ['name', 'type', 'server', 'port', 'uuid'],  # 根据parse_vmess函数
    'vless': ['name', 'type', 'server', 'port', 'uuid'],  # 根据parse_vless函数
    'trojan': ['name', 'type', 'server', 'port', 'password'],  # 根据parse_trojan函数
    'ss': ['name', 'type', 'server', 'port', 'cipher', 'password'],  # 根据parse_ss函数
    'hysteria2': ['name', 'type', 'server', 'port'],  # 移除auth-str作为必填字段，因为某些配置可能不包含
    'anytls': ['name', 'type', 'server', 'port', 'password'],  # 添加anytls代理类型支持
    'ssr': ['name', 'type', 'server', 'port', 'protocol', 'cipher', 'obfs', 'password']  # 根据parse_ssr函数
}

# 不同代理类型的可选字段 - 基于uri2clash/parser.py中的解析逻辑并扩展常见字段
PROXY_TYPE_OPTIONAL_FIELDS = {
    'vmess': ['alterId', 'cipher', 'network', 'tls', 'host', 'path', 'sni', 'udp', 
              'servername', 'ws-opts', 'client-fingerprint', 'alpn', 'ws-path', 'ws-headers',
              'version', 'skip-cert-verify'],  # 扩展了常见字段，添加更多WebSocket相关字段和版本相关字段
    'vless': ['security', 'encryption', 'flow', 'sni', 'fp', 'pbk', 'network', 'header', 
              'servername', 'ws-opts', 'client-fingerprint', 'alpn', 'udp', 
              'reality-opts', 'skip-cert-verify', 'reality', 'ws-path', 'ws-headers',
              'version', 'grpc-opts'],  # 扩展了常见字段，添加reality、WebSocket相关字段、版本和grpc相关字段
    'trojan': ['security', 'sni', 'fp', 'skip-cert-verify', 'type-tcp', 'header-type', 
               'servername', 'client-fingerprint', 'alpn', 'udp', 'reality-opts', 'reality', 
               'network', 'tls', 'ws-opts', 'ws-path', 'ws-headers',
               'version', 'grpc-opts'],  # 扩展了常见字段，添加network、tls、WebSocket相关字段、版本和grpc相关字段
    'ss': ['plugin', 'plugin-opts', 'udp', 'network', 'tls', 'servername', 'ws-opts', 'ws-path', 'ws-headers',
           'version', 'skip-cert-verify', 'grpc-opts'],  # 扩展了常见字段，添加WebSocket相关字段、版本和grpc相关字段
    'hysteria2': ['sni', 'skip-cert-verify', 'alpn', 'obfs', 'obfs-password', 'upmbps', 'downmbps', 
                 'udp', 'network', 'auth-str', 'password', 'tls',
                 'version', 'grpc-opts'],  # 扩展了常见字段，添加password作为可选字段，支持简单tls字段和其他常见字段
    'anytls': ['network', 'tls', 'servername', 'ws-path', 'ws-headers', 'grpc-opts', 'version', 'skip-cert-verify', 'client-fingerprint', 'udp', 'alpn', 'sni'],  # 根据实际配置更新anytls代理类型的可选字段
    'ssr': ['obfs-param', 'protocol-param', 'group', 'udp', 'network', 'tls', 'sni', 'alpn', 'skip-cert-verify', 'version']  # 根据parse_ssr函数添加ssr的可选字段
}

def validate_proxies(proxies, return_valid_list=False):
    """验证代理节点列表"""
    if not isinstance(proxies, list):
        print("[❌ 配置错误] proxies 必须是列表类型。")
        return False if not return_valid_list else ([], 0, 0, 0)
    
    if not proxies:
        print("[⚠️ 警告] proxies 列表为空。")
    
    valid_count = 0
    invalid_count = 0
    unknown_type_count = 0
    valid_proxies = []
    
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
        
        # 检查未知字段（仅警告）- 暂时禁用，避免过多警告信息
        # all_valid_fields = PROXY_TYPE_REQUIRED_FIELDS[proxy_type] + PROXY_TYPE_OPTIONAL_FIELDS[proxy_type]
        # unknown_fields = [field for field in proxy if field not in all_valid_fields]
        # if unknown_fields:
        #     print(f"[⚠️ 未知字段] {proxy_name}: {', '.join(unknown_fields)}")
        
        valid_count += 1
        valid_proxies.append(proxy)
    
    print(f"\n[📊 代理节点统计]")
    print(f"  有效节点数: {valid_count}")
    print(f"  无效节点数: {invalid_count}")
    print(f"  未知类型节点数: {unknown_type_count}")
    
    if return_valid_list:
        return (valid_proxies, valid_count, invalid_count, unknown_type_count)
    
    # 即使有无效节点，也返回True，让用户可以继续使用大部分有效的代理节点
    # 只在完全没有有效节点时才返回False
    return valid_count > 0

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

def validate_clash_yaml(file_path, clean=False):
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
    
    # 验证proxies，根据是否需要清理决定是否返回有效节点列表
    print("\n[🔧 验证代理节点]")
    if clean:
        valid_proxies, valid_count, invalid_count, unknown_type_count = validate_proxies(config.get('proxies', []), return_valid_list=True)
        proxies_valid = valid_count > 0
        
        # 如果有无效节点且用户要求清理，则更新配置文件
        if invalid_count > 0:
            print("\n[🧹 开始清理无效节点]")
            original_count = len(config.get('proxies', []))
            config['proxies'] = valid_proxies
            
            # 生成新文件名
            base_name, ext = os.path.splitext(file_path)
            new_file_path = f"{base_name}_cleaned{ext}"
            
            # 保存清理后的配置
            try:
                yaml_dumper = YAML()
                yaml_dumper.indent(mapping=2, sequence=4, offset=2)
                with open(new_file_path, 'w', encoding='utf-8') as f:
                    yaml_dumper.dump(config, f)
                print(f"✅ 清理完成！已生成新文件: {new_file_path}")
                print(f"📊 清理统计：")
                print(f"  原节点总数: {original_count}")
                print(f"  清理后有效节点数: {len(valid_proxies)}")
                print(f"  移除的无效节点数: {invalid_count + unknown_type_count}")
            except Exception as e:
                print(f"❌ 保存清理后的文件失败: {e}")
                return False
    else:
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
    # if 'redir-port' not in config:
    #     print("[⚠️ 警告] 未配置透明代理端口(redir-port)")
    # if 'tproxy-port' not in config:
    #     print("[⚠️ 警告] 未配置TPROXY端口(tproxy-port)")
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
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("用法：python validate_clash_yaml.py xxx.yaml [--clean]")
        print("选项：")
        print("  --clean   清理无效节点并生成新文件(文件名会添加_cleaned后缀)")
        sys.exit(1)

    yaml_path = sys.argv[1]
    clean = len(sys.argv) == 3 and sys.argv[2] == "--clean"
    
    valid = validate_clash_yaml(yaml_path, clean=clean)
    if not valid:
        sys.exit(1)
