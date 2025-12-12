#!/usr/bin/env python3
import sys
import os
import urllib.parse

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from parser import parse_uri
except ImportError:
    from .parser import parse_uri

def test_single_uri(uri):
    """测试单个URI的转换"""
    print(f"\n=== 测试URI: {uri}")
    try:
        proxy = parse_uri(uri)
        print(f"✅ 解析成功！")
        print(f"\n原始URI: {uri}")
        print(f"\n解析后的配置:")
        for key, value in proxy.items():
            print(f"  {key}: {value}")
        
        # 验证关键参数是否一致
        print(f"\n🔍 参数验证:")
        
        # 根据不同协议验证参数
        if uri.startswith("trojan://"):
            # 验证trojan参数
            userinfo = uri.split("@")[0][len("trojan://"):]
            print(f"  密码: {userinfo} -> {proxy.get('password')} {'✓' if userinfo == proxy.get('password') else '✗'}")
            
        elif uri.startswith("vless://"):
            # 验证vless参数
            userinfo = uri.split("@")[0][len("vless://"):]
            print(f"  UUID: {userinfo} -> {proxy.get('uuid')} {'✓' if userinfo == proxy.get('uuid') else '✗'}")
            
        elif uri.startswith("hysteria2://"):
            # 验证hysteria2参数
            userinfo = uri.split("@")[0][len("hysteria2://"):]
            print(f"  auth-str: {userinfo} -> {proxy.get('auth-str')} {'✓' if userinfo == proxy.get('auth-str') else '✗'}")
            
        # 验证服务器和端口
        server_port_part = uri.split("@")[1].split("?")[0].split("#")[0]
        server, port = server_port_part.split(":")
        # 移除端口中可能的斜杠
        port = port.rstrip('/')
        
        print(f"  服务器: {server} -> {proxy.get('server')} {'✓' if server == proxy.get('server') else '✗'}")
        print(f"  端口: {port} -> {proxy.get('port')} {'✓' if port == str(proxy.get('port')) else '✗'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 URI转换测试工具")
    print("="*50)
    
    # 从url_sample.txt读取前10个URI进行测试
    with open("url_sample.txt", "r", encoding="utf-8") as f:
        uris = [line.strip() for line in f if line.strip()]
    
    if not uris:
        print("❌ 未找到URI")
        return
    
    # 测试前10个URI
    test_uris = uris[:10]
    print(f"\n📋 测试前10个URI...")
    
    success_count = 0
    for uri in test_uris:
        if test_single_uri(uri):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"📊 测试结果: {success_count}/{len(test_uris)} 个URI解析成功")

if __name__ == "__main__":
    main()