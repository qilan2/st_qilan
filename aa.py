import os
import requests
from pathlib import Path
import shutil

def delete_specific_files():
    """删除将要下载的四个特定文件（如果存在）"""
    base_dir = Path("/root/SillyTavern")
    
    files_to_delete = [
        base_dir / "src/config.default.js",
        base_dir / "src/middleware/ip-whitelist.js",
        base_dir / "src/endpoints/users-lng.js",
        base_dir / "src/endpoints/users-internal.js"
    ]
    
    print("删除指定目标文件...")
    deleted_count = 0
    
    for file_path in files_to_delete:
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"✓ 已删除: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"✗ 删除失败 [{file_path}]: {str(e)}")
        else:
            print(f"☑ 无需删除 (文件不存在): {file_path}")
    
    print(f"删除完成: 共删除 {deleted_count} 个指定文件\n" + "="*50)

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
    
    # 1. 只删除指定目标文件
    delete_specific_files()
    
    # 2. 下载文件列表
    files_to_download = {
        f"{base_url}/st2.py": f"{base_dir}/st2.py",
        f"{base_url}/config.default.js": f"{base_dir}/src/config.default.js",
        f"{base_url}/ip-whitelist.js": f"{base_dir}/src/middleware/ip-whitelist.js",
        f"{base_url}/users-lng.js": f"{base_dir}/src/endpoints/users-lng.js",
        f"{base_url}/users-internal.js": f"{base_dir}/src/endpoints/users-internal.js"
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
