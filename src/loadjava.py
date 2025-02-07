import sys
import os
import subprocess


def run_java(temp_dir, game_path, operation, this_dir):
    java_class_path = this_dir
    java_command = ["java", "-cp", java_class_path, "FileReplacer", temp_dir, game_path, operation]
    try:
        process = subprocess.Popen(java_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line.strip())
        process.wait()
        if process.returncode != 0:
            print(f"运行Java程序出错，返回码: {process.returncode}")
    except FileNotFoundError:
        print("Java运行环境未找到，请确保已安装Java并配置好环境变量。")
    except Exception as e:
        print(f"运行Java程序时发生错误: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python loadjava.py   <temp_dir> <gamepath> <operation>")
        sys.exit(1)

    temp_dir = sys.argv[1]
    game_path = sys.argv[2]
    operation = sys.argv[3]
    this_dir = sys.argv[4]
    run_java(temp_dir, game_path, operation, this_dir)
