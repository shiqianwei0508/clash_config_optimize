import subprocess
import os
import shutil

# 🛠️ 配置参数
MAIN_SCRIPT = "main_ui_pyside6.py"
EXE_NAME = "ClashOptimizer"
RESOURCE_PATH = "static/pic/loading.gif"
MMDB_PATH = "mmdb/GeoLite2-Country.mmdb"
script_base = os.path.splitext(os.path.basename(MAIN_SCRIPT))[0]
dist_dir = os.path.join("dist", f"{script_base}.dist")
final_exe = os.path.join(dist_dir, f"{script_base}.exe")


# # ✅ 清理旧构建
# for folder in ["dist", "build", f"{EXE_NAME}.dist", f"{EXE_NAME}.build"]:
#     if os.path.exists(folder):
#         shutil.rmtree(folder)

# ✅ 构建 Nuitka 命令
cmd = [
    "nuitka",
    "--standalone",
    "--enable-plugin=pyside6",
    f"--output-dir=dist",
    f"--windows-console-mode=disable",
    f"--include-data-file={RESOURCE_PATH}={RESOURCE_PATH}",
    f"--include-data-file={MMDB_PATH}={MMDB_PATH}",
    MAIN_SCRIPT
]

print("🚀 正在使用 Nuitka 编译，请稍候...")
result = subprocess.run(" ".join(cmd), shell=True)

if result.returncode == 0:
    print(f"\n✅ 打包完成：{final_exe}")
else:
    print("\n❌ 打包失败，请检查错误信息")

# ✅ 自动重命名 exe 文件
original_exe = os.path.join(dist_dir, f"{script_base}.exe")
target_exe = os.path.join(dist_dir, f"{EXE_NAME}.exe")

if os.path.exists(original_exe):
    os.rename(original_exe, target_exe)
    print(f"✅ 已重命名为：{target_exe}")
else:
    print("⚠️ 未找到生成的 EXE 文件，无法重命名")
