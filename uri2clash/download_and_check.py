import requests

# 下载文件
url = 'https://s3.v2rayse.com/public/20251211/x7dejxng.txt'
response = requests.get(url)

# 保存文件
with open('downloaded_sub.txt', 'w') as f:
    f.write(response.text)

print('文件下载完成！')
print(f'文件大小: {len(response.text)} 字符')
print(f'行数: {response.text.count(chr(10)) + 1} 行')
print('\n前20行内容:')
lines = response.text.split(chr(10))
for i, line in enumerate(lines[:20]):
    print(f'第 {i+1} 行: {line}')

print('\n后20行内容:')
for i, line in enumerate(lines[-20:]):
    print(f'第 {len(lines) - 19 + i} 行: {line}')

# 检查是否为订阅文件
is_subscription = False
# 订阅文件通常包含base64编码或多个代理链接
if len(lines) == 1 and len(lines[0]) > 100:
    # 可能是base64编码的订阅文件
    print('\n[分析] 这可能是一个base64编码的订阅文件')
    is_subscription = True
elif any(line.startswith('ss://') or line.startswith('trojan://') or line.startswith('vless://') or line.startswith('vmess://') for line in lines):
    # 包含代理链接
    print('\n[分析] 这是一个包含代理链接的订阅文件')
    # 统计不同类型的代理数量
    ss_count = sum(1 for line in lines if line.startswith('ss://'))
    trojan_count = sum(1 for line in lines if line.startswith('trojan://'))
    vless_count = sum(1 for line in lines if line.startswith('vless://'))
    vmess_count = sum(1 for line in lines if line.startswith('vmess://'))
    print(f'\n代理类型统计:')
    print(f'- Shadowsocks (ss): {ss_count} 个')
    print(f'- Trojan: {trojan_count} 个')
    print(f'- VLESS: {vless_count} 个')
    print(f'- VMess: {vmess_count} 个')
    print(f'- 总计: {ss_count + trojan_count + vless_count + vmess_count} 个代理')
    is_subscription = True
else:
    print('\n[分析] 这不是一个常见的代理订阅文件格式')
