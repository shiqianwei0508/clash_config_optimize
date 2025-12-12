import base64

# 读取下载的文件
with open('downloaded_sub.txt', 'r') as f:
    encoded_content = f.read().strip()

# 解码base64
print('开始解码base64内容...')
decoded_content = base64.b64decode(encoded_content).decode('utf-8')

print('解码完成！')
print(f'解码后大小: {len(decoded_content)} 字符')
print(f'解码后行数: {decoded_content.count(chr(10)) + 1} 行')

# 保存解码后的内容
with open('decoded_sub.txt', 'w') as f:
    f.write(decoded_content)

# 分析代理类型
lines = decoded_content.split(chr(10))
# 过滤空行
lines = [line.strip() for line in lines if line.strip()]

ss_count = sum(1 for line in lines if line.startswith('ss://'))
ssr_count = sum(1 for line in lines if line.startswith('ssr://'))
trojan_count = sum(1 for line in lines if line.startswith('trojan://'))
vless_count = sum(1 for line in lines if line.startswith('vless://'))
vmess_count = sum(1 for line in lines if line.startswith('vmess://'))
hysteria_count = sum(1 for line in lines if line.startswith('hysteria2://') or line.startswith('hysteria://'))

print('\n代理类型统计:')
print(f'- Shadowsocks (ss): {ss_count} 个')
print(f'- ShadowsocksR (ssr): {ssr_count} 个')
print(f'- Trojan: {trojan_count} 个')
print(f'- VLESS: {vless_count} 个')
print(f'- VMess: {vmess_count} 个')
print(f'- Hysteria: {hysteria_count} 个')
print(f'- 总计: {ss_count + ssr_count + trojan_count + vless_count + vmess_count + hysteria_count} 个代理')
print(f'- 空行数: {len(decoded_content.split(chr(10))) - len(lines)} 个')

# 显示前10个代理链接
print('\n前10个代理链接:')
for i, line in enumerate(lines[:10]):
    print(f'{i+1}. {line[:100]}...')
