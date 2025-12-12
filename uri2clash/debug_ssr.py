import base64
import urllib.parse

# 从解码后的文件中取一个SSR URI来测试
ssr_uri = "ssr://d3d3LmJhaWR1LmNvbTo4MDphdXRoX2FlczEyOF9tZDU6cmM0LW1kNTp0bHMxLjJfdGlja2V0X2F1dGg6WW5KbFlXdDNZV3hzLz9yZW1hcmtzPTVhNlk1NzJSNVp5dzVaMkFJQzBnYUhSMGNITTZMeTlvYVhSMWJpNXBidz09"

print(f"测试URI: {ssr_uri}")

# 第一步：提取URI主体部分
body = ssr_uri[len("ssr://"):]
print(f"\n1. URI主体部分: {body}")

# 第二步：解码主体部分
try:
    decoded_body = base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)).decode("utf-8")
    print(f"2. 主体解码结果: {decoded_body}")
except Exception as e:
    print(f"2. 主体解码失败: {e}")
    exit(1)

# 第三步：分割主体部分
if "?" in decoded_body:
    main_part, query_part = decoded_body.split("?", 1)
    print(f"3. 主要部分: {main_part}")
    print(f"4. 查询参数部分: {query_part}")

# 第四步：分割主要部分（服务器:端口:协议:加密:混淆:密码）
try:
    parts = main_part.split(":")
    print(f"5. 主要部分分割: {parts}")
    print(f"6. 分割数量: {len(parts)}")
    server, port, protocol, cipher, obfs, password_part = main_part.split(":", 5)
    print(f"7. 服务器: {server}")
    print(f"8. 端口: {port}")
    print(f"9. 协议: {protocol}")
    print(f"10. 加密: {cipher}")
    print(f"11. 混淆: {obfs}")
    print(f"12. 密码部分: {password_part}")
    print(f"13. 密码部分长度: {len(password_part)}")
    print(f"14. 密码部分模4: {len(password_part) % 4}")
except ValueError as e:
    print(f"分割失败: {e}")
    exit(1)

# 第五步：测试密码的多种解码方法
print("\n=== 密码解码尝试 ===")

# 方法1：urlsafe_b64decode
try:
    password = base64.urlsafe_b64decode(password_part + '=' * (-len(password_part) % 4)).decode("utf-8")
    print(f"方法1成功: {password}")
except Exception as e:
    print(f"方法1失败: {e}")

# 方法2：标准b64decode + 手动处理
password_part2 = password_part.replace('-', '+').replace('_', '/')
try:
    password = base64.b64decode(password_part2 + '=' * (-len(password_part2) % 4)).decode("utf-8")
    print(f"方法2成功: {password}")
except Exception as e:
    print(f"方法2失败: {e}")

# 方法3：不同的填充方式
try:
    padding = (4 - len(password_part) % 4) % 4
    password = base64.urlsafe_b64decode(password_part + '=' * padding).decode("utf-8")
    print(f"方法3成功: {password}")
    print(f"填充数量: {padding}")
except Exception as e:
    print(f"方法3失败: {e}")

# 方法4：先看看原始二进制
print("\n原始密码部分二进制:")
try:
    raw_bytes = base64.urlsafe_b64decode(password_part + '=' * (-len(password_part) % 4))
    print(f"二进制数据: {raw_bytes}")
    # 尝试用不同编码解码
    for encoding in ['utf-8', 'latin-1', 'gbk']:
        try:
            password = raw_bytes.decode(encoding)
            print(f"  用{encoding}解码: {password}")
        except Exception as e:
            print(f"  用{encoding}解码失败: {e}")
except Exception as e:
    print(f"获取原始二进制失败: {e}")
