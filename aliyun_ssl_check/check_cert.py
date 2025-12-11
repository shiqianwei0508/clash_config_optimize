import ssl
import socket
import pprint

def get_server_cert_chain(host, port=465):
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host)
    conn.connect((host, port))
    
    # 获取 PEM 格式证书
    cert_chain = conn.getpeercert(True)  # 获取 DER 格式证书
    pem_cert = ssl.DER_cert_to_PEM_cert(cert_chain)
    print("服务器证书 PEM 格式：\n")
    print(pem_cert)
    
    # 使用标准函数获取解析后的证书信息
    cert_info = conn.getpeercert()  # 不传入True参数，获取解析后的证书信息
    print("\n证书详细信息：")
    pprint.pprint(cert_info)
    
    conn.close()

if __name__ == "__main__":
    try:
        print("正在获取证书信息...")
        get_server_cert_chain("smtpdm.aliyun.com", 465)
    except Exception as e:
        print(f"发生错误: {type(e).__name__}: {e}")
