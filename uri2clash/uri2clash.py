#!/usr/bin/env python3
import argparse
import yaml
from .parser import parse_uri
from .utils import load_uri_file, load_uri_from_url, save_yaml

def generate_clash_config(proxies):
    """生成完整的Clash配置"""
    # 按国家分组节点
    country_proxies = {
        '🇺🇸': [],  # 美国
        '🇭🇰': [],  # 香港
        '🇯🇵': [],  # 日本
        'other': []  # 其他国家
    }
    
    # 识别节点国家
    for proxy in proxies:
        name = proxy['name']
        # 检查名称中是否包含国家标识
        if '🇺🇸' in name or 'US' in name:
            country_proxies['🇺🇸'].append(name)
        elif '🇭🇰' in name or 'HK' in name:
            country_proxies['🇭🇰'].append(name)
        elif '🇯🇵' in name or 'JP' in name:
            country_proxies['🇯🇵'].append(name)
        else:
            country_proxies['other'].append(name)
    
    # 构建完整配置
    config = {
        # 基础配置
        'mixed-port': 7890,
        'allow-lan': False,
        'bind-address': '127.0.0.1',
        'socks-port': 7891,
        'redir-port': 7892,
        'mode': 'Rule',
        'log-level': 'info',
        'unified-delay': True,
        'tun': {
            'enable': False
        },
        
        # 代理节点
        'proxies': proxies,
        
        # 代理组配置
        'proxy-groups': [
            {
                'name': '🚀 节点选择',
                'type': 'select',
                'proxies': ['DIRECT', '🇺🇸 美国节点', '🇭🇰 香港节点', '🇯🇵 日本节点', '🌐 其他节点']
            },
            {
                'name': '🇺🇸 美国节点',
                'type': 'select',
                'proxies': ['DIRECT'] + country_proxies['🇺🇸']
            },
            {
                'name': '🇭🇰 香港节点',
                'type': 'select',
                'proxies': ['DIRECT'] + country_proxies['🇭🇰']
            },
            {
                'name': '🇯🇵 日本节点',
                'type': 'select',
                'proxies': ['DIRECT'] + country_proxies['🇯🇵']
            },
            {
                'name': '🌐 其他节点',
                'type': 'select',
                'proxies': ['DIRECT'] + country_proxies['other']
            },
            {
                'name': '📺 流媒体',
                'type': 'select',
                'proxies': ['DIRECT', '🇺🇸 美国节点']
            },
            {
                'name': '🌍 全球直连',
                'type': 'select',
                'proxies': ['DIRECT', '🚀 节点选择']
            },
            {
                'name': '🛡️ 隐私保护',
                'type': 'select',
                'proxies': ['DIRECT', '🚀 节点选择']
            }
        ],
        
        # 规则配置
        'rules': [
            # Telegram相关规则
            'DOMAIN-SUFFIX,telegram.org,🚀 节点选择',
            'DOMAIN-SUFFIX,t.me,🚀 节点选择',
            'DOMAIN-SUFFIX,telegram.me,🚀 节点选择',
            'DOMAIN-SUFFIX,tdesktop.com,🚀 节点选择',
            # 流媒体相关规则
            'DOMAIN-SUFFIX,youtube.com,📺 流媒体',
            'DOMAIN-SUFFIX,netflix.com,📺 流媒体',
            'DOMAIN-SUFFIX,disneyplus.com,📺 流媒体',
            'DOMAIN-SUFFIX,hbo.com,📺 流媒体',
            'DOMAIN-SUFFIX,spotify.com,📺 流媒体',
            # 国内应用规则
            'DOMAIN-SUFFIX,bilibili.com,DIRECT',
            'DOMAIN-SUFFIX,netease.com,DIRECT',
            'DOMAIN-SUFFIX,163.com,DIRECT',
            'DOMAIN-SUFFIX,qq.com,DIRECT',
            'DOMAIN-SUFFIX,weixin.qq.com,DIRECT',
            'DOMAIN-SUFFIX,weibo.com,DIRECT',
            'DOMAIN-SUFFIX,baidu.com,DIRECT',
            # 国内IP规则
            'GEOIP,CN,DIRECT',
            # 其他规则
            'DOMAIN-KEYWORD,tiktok,🚀 节点选择',
            # 默认规则
            'MATCH,🚀 节点选择'
        ]
    }
    
    return config

def main():
    parser = argparse.ArgumentParser(description="🔗 URI 节点转 Clash YAML 工具")
    # 使用互斥组，让用户只能选择从文件或URL获取节点
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="包含 URI 节点的文本文件")
    group.add_argument("--url", help="包含 URI 节点的 URL 地址")
    parser.add_argument("--output", default="converted.yaml", help="输出 YAML 文件路径")
    args = parser.parse_args()

    # 加载URI列表
    if args.input:
        print(f"📥 从文件加载节点: {args.input}")
        uris = load_uri_file(args.input)
    else:
        print(f"📥 从URL加载节点: {args.url}")
        uris = load_uri_from_url(args.url)
    
    print(f"🔍 发现 {len(uris)} 个节点")
    
    proxies = []
    name_counts = {}  # 用于跟踪节点名称出现次数
    name_server_map = {}  # 用于跟踪节点名称与服务器地址的映射
    
    for uri in uris:
        try:
            proxy = parse_uri(uri)
            original_name = proxy['name']
            server = proxy['server']
            port = proxy['port']
            server_port = f"{server}:{port}"
            
            # 构建唯一标识键
            unique_key = f"{original_name}#{server_port}"
            
            # 检查是否已经存在相同名称和相同服务器端口的节点
            if unique_key in name_server_map:
                # 完全相同的节点，跳过
                print(f"⏭️  跳过重复节点: {original_name} ({server_port})")
                continue
            
            # 检查是否存在相同名称但不同服务器端口的节点
            if original_name in name_counts:
                # 同名不同服务器，添加编号后缀
                name_counts[original_name] += 1
                new_name = f"{original_name} ({name_counts[original_name]})"
                proxy['name'] = new_name
                print(f"📝 重命名节点: {original_name} -> {new_name} ({server_port})")
            else:
                # 新名称，初始化计数
                name_counts[original_name] = 1
            
            # 记录节点信息
            name_server_map[unique_key] = True
            proxies.append(proxy)
        except Exception as e:
            print(f"❌ 跳过无效 URI: {uri}\n   原因: {e}")

    # 生成完整的Clash配置
    config = generate_clash_config(proxies)
    
    # 保存配置文件
    save_yaml(config, args.output)
    print(f"✅ 已保存 {len(proxies)} 个节点到 {args.output}")
    print(f"📋 配置包含: {len(config['proxy-groups'])} 个代理组")

if __name__ == "__main__":
    main()
