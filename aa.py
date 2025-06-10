import os
import requests
from pathlib import Path
import shutil

def clear_directory():
    """清理SillyTavern相关目录，准备新下载"""
    base_dir = Path("/root/SillyTavern")
    target_dirs = [
        base_dir / "src",
        base_dir / "src/middleware",
        base_dir / "src/endpoints"
    ]
    
    print("清理目标目录...")
    for dir_path in target_dirs:
        if dir_path.exists() and dir_path.is_dir():
            # 仅删除目录中的文件，保留目录结构
            for item in dir_path.iterdir():
                if item.is_file():
                    item.unlink()
                    print(f"已删除文件: {item}")
    
    print("清理完成，准备下载新文件。\n" + "="*50)

def download_file(url, destination):
    """下载文件到指定路径，自动创建目录"""
    dest_path = Path(destination)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"正在下载: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        print(f"✓ 下载成功: {dest_path} ({len(response.content)} bytes)")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"✗ 下载失败: {str(e)}")
        return False

def main():
    base_dir = "/root/SillyTavern"
    base_url = "https://raw.githubusercontent.com/qilan2/st_qilan/refs/heads/main"
    
    # 1. 先清理目录
    clear_directory()
    
    # 2. 下载文件列表
    files_to_download = {
        f"{base_url}/config.default.js": f"{base_dir}/src/config.default.js",
        f"{base_url}/ip-whitelist.js": f"{base_dir}/src/middleware/ip-whitelist.js",
        f"{base_dir}/users-lng.js": f"{base_dir}/src/endpoints/users-lng.js",
        f"{base_dir}/users-internal.js": f"{base_dir}/src/endpoints/users-internal.js"
    }
    
    print(f"开始在 {base_dir} 下载配置文件...\n")
    success_count = 0
    
    for url, dest in files_to_download.items():
        if download_file(url, dest):
            success_count += 1
        print("-" * 40)
    
    print(f"\n操作完成: 共 {len(files_to_download)} 个文件, 成功 {success_count} 个")

if __name__ == "__main__":
    main()
