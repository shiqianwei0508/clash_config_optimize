import base64
import urllib.parse

# 测试一个SSR URI
ssr_uri = "ssr://d3d3LmJhaWR1LmNvbTo4MDphdXRoX2FlczEyOF9tZDU6cmM0LW1kNTp0bHMxLjJfdGlja2V0X2F1dGg6WW5KbFlXdDNZV3hzLz9yZW1hcmtzPTVhNlk1NzJSNVp5dzVaMkFJQzBnYUhSMGNITTZMeTlvYVhSMWJpNXBidz09"

print(f"原始URI: {ssr_uri}")
body = ssr_uri[len("ssr://"):]
print(f"URI主体: {body}")
print(f"主体长度: {len(body)}")
print(f"长度模4: {len(body) % 4}")

# 尝试不同的解码方法
print("\n=== 解码尝试 ===")

# 方法1: 标准填充
try:
    # 处理URL安全的base64
    body = body.replace('-', '+').replace('_', '/')
    # 计算需要的填充
    padding = 4 - (len(body) % 4) if len(body) % 4 != 0 else 0
    padded_body = body + '=' * padding
    print(f"填充后: {padded_body}")
    print(f"填充后长度: {len(padded_body)}")
    decoded = base64.b64decode(padded_body)
    print(f"方法1解码成功: {decoded}")
    print(f"解码后字符串: {decoded.decode('utf-8')}")
except Exception as e:
    print(f"方法1失败: {e}")

# 方法2: 使用base64.urlsafe_b64decode
try:
    decoded = base64.urlsafe_b64decode(body)
    print(f"方法2解码成功: {decoded}")
    print(f"解码后字符串: {decoded.decode('utf-8')}")
except Exception as e:
    print(f"方法2失败: {e}")

# 方法3: 手动处理填充
try:
    # 计算需要的填充字符数
    missing_padding = len(body) % 4
    if missing_padding:
        body += '=' * (4 - missing_padding)
    decoded = base64.urlsafe_b64decode(body)
    print(f"方法3解码成功: {decoded}")
    print(f"解码后字符串: {decoded.decode('utf-8')}")
except Exception as e:
    print(f"方法3失败: {e}")
