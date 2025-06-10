import socket
import subprocess
import time
import threading
import os
import sys
import platform
import signal

# 全局变量
OWN_PID = os.getpid()
print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 脚本PID: {OWN_PID}")

# 设置信号处理，防止被意外终止
def signal_handler(sig, frame):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 收到信号 {sig}，正在安全退出...")
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 检查是否为Linux系统
if platform.system() != 'Linux':
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 错误：此脚本只能在Linux系统上运行。")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 当前系统为：{platform.system()}")
    sys.exit(1)

# data_folder = '/opt/SillyTavern5'
data_folder = os.path.dirname(os.path.abspath(__file__))
print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 当前目录：{data_folder}")
status = False

def kill_process_on_port(port):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        print(f"[{current_time}] 检查并终止端口 {port} 的进程...")
        # 查找并终止使用指定端口的进程 (仅Linux)
        result = subprocess.run(f'lsof -i :{port} -t', shell=True, capture_output=True, text=True)
        if result.stdout:
            pids_to_kill = []
            for pid_str in result.stdout.splitlines():
                pid = pid_str.strip()
                if pid and pid.isdigit():
                    pid = int(pid)
                    # 避免杀死脚本自身
                    if pid != OWN_PID:
                        pids_to_kill.append(pid)
                    else:
                        print(f"[{current_time}] 跳过脚本自身进程 (PID: {pid})")
            
            if pids_to_kill:
                for pid in pids_to_kill:
                    print(f"[{current_time}] 正在终止使用端口 {port} 的进程 (PID: {pid})")
                    try:
                        subprocess.run(f'kill -15 {pid}', shell=True, check=False)  # 先尝试优雅终止
                        time.sleep(1)  # 给进程一点时间来关闭
                        # 检查进程是否仍然存在
                        if subprocess.run(f'ps -p {pid} > /dev/null', shell=True, check=False).returncode == 0:
                            print(f"[{current_time}] 进程 {pid} 未响应，强制终止")
                            subprocess.run(f'kill -9 {pid}', shell=True, check=False)
                    except Exception as e:
                        print(f"[{current_time}] 终止进程 {pid} 时出错: {e}")
                print(f"[{current_time}] 端口 {port} 的所有进程已终止")
            else:
                print(f"[{current_time}] 没有需要终止的进程")
        else:
            print(f"[{current_time}] 未发现使用端口 {port} 的进程")
    except Exception as e:
        print(f"[{current_time}] 终止端口 {port} 进程时发生错误: {e}")

def monitor_port():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始监控端口 8000...")
    check_count = 0
    while True:
        try:
            check_count += 1
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 检查端口前进行输出
            if check_count % 10 == 1:  # 每10次检查才输出一次，避免日志过多
                print(f"[{current_time}] 正在检查端口 8000 状态... (第{check_count}次检查)")
                
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)  # 设置超时时间为5秒
                result = sock.connect_ex(('localhost', 8000))
                
                if result == 0:
                    print(f"[{current_time}] 端口 8000 正在使用中")
                else:
                    print(f"[{current_time}] 端口 8000 未被使用，正在启动服务...")
                    # 直接在主线程中运行，但使用try-except确保不会崩溃
                    try:
                        Run_SillyTavern()
                    except Exception as e:
                        print(f"[{current_time}] 启动服务时发生错误: {e}")
        except Exception as e:
            print(f"[{current_time}] 监控端口时发生错误: {e}")
            
        # 短暂休眠，便于调试
        time.sleep(30)  # 每30秒检查一次

def Run_SillyTavern():
    global status  # 关键修复：声明全局变量
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    
    if status:
        print(f"[{current_time}] 服务正在启动或运行中，跳过...")
        return
        
    try:
        status = True
        print(f"[{current_time}] 尝试切换到目录: {data_folder}")
        original_dir = os.getcwd()  # 保存当前目录
        os.chdir(data_folder)
        
        print(f"[{current_time}] 尝试启动服务...")
        # 先终止可能在运行的8000端口进程
        kill_process_on_port(8000)
        
        # 验证启动脚本存在
        start_script = f"{data_folder}/start.sh"
        if not os.path.exists(start_script):
            print(f"[{current_time}] 错误: 启动脚本不存在: {start_script}")
            status = False
            return
            
        print(f"[{current_time}] 执行启动命令...")
        # 使用nohup确保进程在后台运行，即使脚本终止
        try:
            subprocess.run(f'yes | sh {data_folder}/start.sh', shell=True)
            print(f"[{current_time}] 启动命令已执行，服务将在后台运行")
        except Exception as e:
            print(f"[{current_time}] 启动命令执行失败: {e}")
        
        # 恢复原来的目录
        os.chdir(original_dir)
        
    except subprocess.CalledProcessError as e:
        print(f"[{current_time}] 命令失败，返回码: {e.returncode}")
    except Exception as e:
        print(f"[{current_time}] 发生异常: {e}")
    finally:
        # 延迟重置状态，给服务启动一些时间
        time.sleep(10)
        status = False
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 服务启动流程完成")

def clean_log_file():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    log_file = 'st2.log'
    try:
        max_log_size = 10 * 1024 * 1024  # 10MB
        if os.path.exists(log_file) and os.path.getsize(log_file) > max_log_size:
            os.remove(log_file)
            print(f"[{current_time}] 清理日志文件 {log_file}")
    except Exception as e:
        print(f"[{current_time}] 清理日志时发生错误: {e}")

def drop_caches():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 缓存清理线程已启动")
    while True:
        try:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            clean_log_file()
            print(f"[{current_time}] 执行内存清理...")
            # 使用sudo需要设置无密码执行，否则可能会失败
            try:
                # subprocess.run('sync && echo 1 | sudo tee /proc/sys/vm/drop_caches > /dev/null', shell=True, timeout=10)
                print(f"[{current_time}] 内存清理完成")
            except subprocess.TimeoutExpired:
                print(f"[{current_time}] 内存清理命令超时")
            except Exception as e:
                print(f"[{current_time}] 内存清理命令失败: {e}")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 清理缓存时发生错误: {e}")
        time.sleep(1800)  # 每30分钟执行一次

try:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 启动缓存清理线程...")
    cache_thread = threading.Thread(target=drop_caches, daemon=True)
    cache_thread.start()

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 启动主监控线程...")
    monitor_port()
except KeyboardInterrupt:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 收到用户中断，正在退出...")
except Exception as e:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 主程序异常: {e}")
    sys.exit(1)
