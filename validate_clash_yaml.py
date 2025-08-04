import sys
from ruamel.yaml import YAML
from ruamel.yaml.constructor import ConstructorError

REQUIRED_FIELDS = ['proxies', 'proxy-groups', 'rules']

def validate_clash_yaml(file_path):
    yaml = YAML(typ='safe')  # Safe模式只加载标准类型，防止任意代码执行
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f)
    except ConstructorError as e:
        print(f"[❌ YAML构造异常] {e}")
        return False
    except Exception as e:
        print(f"[❌ 加载失败] {e}")
        return False

    if not isinstance(config, dict):
        print("[❌ 配置文件格式错误] 根结构应为字典类型。")
        return False

    missing = [key for key in REQUIRED_FIELDS if key not in config]
    if missing:
        print(f"[⚠️ 缺失字段] 配置文件缺少关键字段: {', '.join(missing)}")
        return False

    print("[✅ 验证成功] 配置文件语法正确，关键字段齐全。")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python validate_clash_yaml.py xxx.yaml")
        sys.exit(1)

    yaml_path = sys.argv[1]
    valid = validate_clash_yaml(yaml_path)
    if not valid:
        sys.exit(1)
