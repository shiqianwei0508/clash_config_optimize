#!/usr/bin/env python3
import argparse
import yaml
import sys
import os
import socket
import concurrent.futures
from tqdm import tqdm

# 添加当前目录到Python路径，确保能直接运行时正确导入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 尝试相对导入（作为包运行时）
    from .parser import parse_uri
    from .utils import load_uri_file, load_uri_from_url, save_yaml
except ImportError:
    # 直接导入（直接运行时）
    from parser import parse_uri
    from utils import load_uri_file, load_uri_from_url, save_yaml

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
        'proxy-groups': []
    }
    
    # 创建基础节点选择组
    node_selection_group = {
        'name': '🚀 节点选择',
        'type': 'select',
        'proxies': []
    }
    
    # 创建并添加国家代理组（只添加有节点的国家）
    country_groups = []
    
    if country_proxies['🇺🇸']:
        us_group = {
            'name': '🇺🇸 美国节点',
            'type': 'url-test',
            'proxies': country_proxies['🇺🇸'],
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300
        }
        country_groups.append(us_group)
        node_selection_group['proxies'].append('🇺🇸 美国节点')
    
    if country_proxies['🇭🇰']:
        hk_group = {
            'name': '🇭🇰 香港节点',
            'type': 'url-test',
            'proxies': country_proxies['🇭🇰'],
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300
        }
        country_groups.append(hk_group)
        node_selection_group['proxies'].append('🇭🇰 香港节点')
    
    if country_proxies['🇯🇵']:
        jp_group = {
            'name': '🇯🇵 日本节点',
            'type': 'url-test',
            'proxies': country_proxies['🇯🇵'],
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300
        }
        country_groups.append(jp_group)
        node_selection_group['proxies'].append('🇯🇵 日本节点')
    
    if country_proxies['other']:
        other_group = {
            'name': '🌐 其他节点',
            'type': 'url-test',
            'proxies': country_proxies['other'],
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300
        }
        country_groups.append(other_group)
        node_selection_group['proxies'].append('🌐 其他节点')
    
    # 添加节点选择组和国家分组
    config['proxy-groups'].append(node_selection_group)
    config['proxy-groups'].extend(country_groups)
    
    # 添加其他功能分组（流媒体、全球直连、隐私保护）
    if node_selection_group['proxies']:  # 只有当有节点选择组时才添加这些组
        config['proxy-groups'].extend([
            {
                'name': '📺 流媒体',
                'type': 'url-test',
                'proxies': ['🇺🇸 美国节点'] if country_proxies['🇺🇸'] else ['🚀 节点选择'],
                'url': 'http://www.gstatic.com/generate_204',
                'interval': 300
            },
            {
                'name': '🌍 全球直连',
                'type': 'url-test',
                'proxies': ['🚀 节点选择'],
                'url': 'http://www.gstatic.com/generate_204',
                'interval': 300
            },
            {
                'name': '🛡️ 隐私保护',
                'type': 'url-test',
                'proxies': ['🚀 节点选择'],
                'url': 'http://www.gstatic.com/generate_204',
                'interval': 300
            }
        ])
        
        # 规则配置
        config['rules'] = [
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
    
    return config

def check_proxy_port(server, port, proxy_type=None, network=None, timeout=3):
    """检测代理服务器端口是否可达
    
    Args:
        server: 服务器地址
        port: 端口号
        proxy_type: 代理类型（如trojan, vless, hysteria2等）
        network: 网络类型（tcp/udp）
        timeout: 超时时间，单位秒
        
    Returns:
        bool: 端口是否可达
    """
    try:
        # 判断是否为UDP端口
        is_udp = False
        if network == "udp":
            is_udp = True
        elif proxy_type == "hysteria2":
            # Hysteria2默认使用UDP
            is_udp = True
        
        if is_udp:
            # UDP端口检测：创建UDP套接字并尝试发送空数据包
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(timeout)
                # 发送一个空数据包
                s.sendto(b"", (server, port))
                # 尝试接收响应（可选，有些服务可能不响应）
                try:
                    s.recvfrom(1024)
                except socket.timeout:
                    # UDP无响应不一定表示端口关闭，只要能发送数据包通常就认为端口是开放的
                    pass
                return True
        else:
            # TCP端口检测（默认）
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((server, port))
                return result == 0
    except Exception as e:
        # print(f"端口检测错误 ({server}:{port}): {e}")
        return False

def batch_check_proxies(proxies, max_workers=100):
    """批量检测代理节点的端口可达性
    
    Args:
        proxies: 代理节点列表
        max_workers: 最大线程数
        
    Returns:
        list: 过滤后的有效代理节点列表
    """
    print(f"🔍 开始检测 {len(proxies)} 个节点的端口可达性...")
    
    valid_proxies = []
    
    # 使用线程池并行检测
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 创建任务字典，键是future对象，值是代理节点
        future_to_proxy = {executor.submit(check_proxy_port, 
                                           proxy['server'], 
                                           proxy['port'], 
                                           proxy.get('type'),
                                           proxy.get('network', 'tcp')): proxy for proxy in proxies}
        
        # 显示进度条
        with tqdm(total=len(future_to_proxy), desc="检测进度", bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            for future in concurrent.futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    is_reachable = future.result()
                    if is_reachable:
                        valid_proxies.append(proxy)
                    else:
                        print(f"❌ 端口不可达，移除节点: {proxy['name']} ({proxy['server']}:{proxy['port']})")
                except Exception as e:
                    print(f"❌ 检测节点失败: {proxy['name']} ({proxy['server']}:{proxy['port']})，错误: {e}")
                pbar.update(1)
    
    print(f"✅ 端口检测完成！有效节点: {len(valid_proxies)}, 移除节点: {len(proxies) - len(valid_proxies)}")
    return valid_proxies

def main():
    parser = argparse.ArgumentParser(description="🔗 URI 节点转 Clash YAML 工具")
    # 使用互斥组，让用户只能选择从文件或URL获取节点
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="包含 URI 节点的文本文件")
    group.add_argument("--url", help="包含 URI 节点的 URL 地址")
    parser.add_argument("--output", default="converted.yaml", help="输出 YAML 文件路径")
    parser.add_argument("--skip-port-check", action="store_true", help="跳过端口可达性检测，保留所有解析成功的节点")
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

    # 批量检测端口可达性
    if args.skip_port_check:
        print(f"⏭️  跳过端口检测，保留所有 {len(proxies)} 个解析成功的节点")
    else:
        proxies = batch_check_proxies(proxies)

    # 生成完整的Clash配置
    config = generate_clash_config(proxies)
    
    # 保存配置文件
    save_yaml(config, args.output)
    print(f"✅ 已保存 {len(proxies)} 个节点到 {args.output}")
    print(f"📋 配置包含: {len(config['proxy-groups'])} 个代理组")

if __name__ == "__main__":
    main()
