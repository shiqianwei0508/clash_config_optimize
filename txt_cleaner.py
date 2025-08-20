import re
import sys
import logging

from pathlib import Path

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 英文标点 → 中文标点映射表
PUNCTUATION_MAP = {
    ",": "，", ".": "。", "?": "？", "!": "！", ":": "：", ";": "；",
    "\"": "“", "'": "’", "(": "（", ")": "）", "[": "【", "]": "】",
    "{": "｛", "}": "｝", "<": "《", ">": "》"
}

def load_text(path: Path) -> list[str]:
    """尝试使用 UTF-8 或 GBK 编码读取文本"""
    for encoding in ("utf-8", "gbk"):
        try:
            with open(path, "r", encoding=encoding) as f:
                lines = f.readlines()
            logging.info(f"✅ 成功使用 {encoding.upper()} 编码读取文件：{path}")
            return lines
        except UnicodeDecodeError:
            logging.warning(f"⚠️ {encoding.upper()} 解码失败，尝试下一种编码")
    logging.error(f"❌ 无法读取文件：{path}，请确认编码格式")
    sys.exit(1)

def replace_punctuation(text: str) -> str:
    """替换英文标点为中文标点"""
    for en, zh in PUNCTUATION_MAP.items():
        text = text.replace(en, zh)
    return text

def count_chinese(text: str) -> int:
    """统计中文字符数量"""
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def contains_garbled(text: str) -> bool:
    """判断是否包含乱码（非法字符）"""
    return bool(re.search(r'[�\x00-\x1F]', text))

def clean_lines(lines: list[str]) -> list[str]:
    """处理每一行：替换标点 + 删除乱码短行"""
    cleaned = []
    dropped = 0

    for i, line in enumerate(lines, 1):
        original = line.strip()
        replaced = replace_punctuation(original)
        chinese_count = count_chinese(replaced)

        if chinese_count < 15 and contains_garbled(replaced):
            logging.info(f"🗑️ 删除第 {i} 行：字符数={chinese_count}，检测到乱码")
            dropped += 1
            continue

        cleaned.append(replaced)

    logging.info(f"📊 共处理 {len(lines)} 行，删除 {dropped} 行，保留 {len(cleaned)} 行")
    return cleaned

def save_text(lines: list[str], output_path: Path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logging.info(f"💾 清洗后的文本已保存到：{output_path}")

def main(input_path: str, output_path: str):
    input_file = Path(input_path)
    output_file = Path(output_path)

    logging.info("🚀 开始处理文本文件")
    lines = load_text(input_file)
    cleaned = clean_lines(lines)
    save_text(cleaned, output_file)
    logging.info("✅ 文本处理完成")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="🧹 中文 TXT 文本清洗工具")
    parser.add_argument("input", help="输入的 TXT 文件路径")
    parser.add_argument("output", help="输出的清洗后 TXT 文件路径")
    args = parser.parse_args()

    main(args.input, args.output)
