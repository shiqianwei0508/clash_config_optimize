#!/usr/bin/env python3
import yaml
import requests

def load_uri_file(file_path):
    """从文件中加载URI列表"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def load_uri_from_url(url):
    """从URL加载URI列表"""
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功
    content = response.text
    return [line.strip() for line in content.split('\n') if line.strip()]

def load_uri_from_multiple_urls(urls):
    """从多个URL加载URI列表并合并"""
    all_uris = []
    for url in urls:
        if url.strip():  # 确保URL不为空
            try:
                uris = load_uri_from_url(url.strip())
                all_uris.extend(uris)
                print(f"从URL {url} 加载了 {len(uris)} 个节点")
            except Exception as e:
                print(f"加载URL {url} 失败: {e}")
                continue
    return all_uris

def save_yaml(data, file_path):
    """保存数据为YAML文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
