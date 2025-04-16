import os
import glob
import re
from pathlib import Path

# 配置路径
BASE_DIR = os.getcwd()
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
RULES_DIR = os.path.join(BASE_DIR, 'data/rules')
ERROR_FILE = os.path.join(BASE_DIR, 'data/mod/error.txt')

def read_error_domains(error_file):
    """读取错误域名列表"""
    if os.path.exists(error_file):
        with open(error_file, 'r') as f:
            error_domains = set(line.strip() for line in f if line.strip())
        print(f"从 {error_file} 读取到 {len(error_domains)} 个错误域名")
        return error_domains
    else:
        print(f"错误域名文件 {error_file} 不存在，跳过过滤步骤")
        return set()

def merge_files(file_pattern, output_file):
    """合并匹配文件到一个文件中"""
    file_list = glob.glob(file_pattern)
    with open(output_file, 'w') as outfile:
        for file in file_list:
            with open(file, 'r') as infile:
                outfile.write(infile.read())
                outfile.write('\n')
    print(f"合并 {file_pattern} 完成，输出到 {output_file}")

def clean_file(input_file, output_file):
    """清理文件内容，删除注释和空行"""
    with open(input_file, 'r') as f:
        content = f.read()
    content = re.sub(r'^[!].*$\n', '', content, flags=re.MULTILINE)  # 删除以 "!" 开头的注释
    content = re.sub(r'^#(?!\s*#).*\n?', '', content, flags=re.MULTILINE)  # 删除以 "#" 开头的注释
    content = re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)  # 删除空行
    with open(output_file, 'w') as f:
        f.write(content)
    print(f"清理文件 {input_file} 完成，输出到 {output_file}")

def filter_error_domains(input_file, output_file, error_domains):
    """过滤错误域名"""
    if not error_domains:
        print("没有需要过滤的错误域名，跳过此步骤")
        return
    with open(input_file, 'r') as f:
        lines = f.readlines()
    with open(output_file, 'w') as f:
        for line in lines:
            if not any(error_domain in line for error_domain in error_domains):
                f.write(line)
    print(f"过滤错误域名完成，输出到 {output_file}")

def remove_duplicates(input_file):
    """去重规则文件"""
    with open(input_file, 'r', encoding='utf8') as f:
        lines = list(set(f.readlines()))
    lines.sort()
    with open(input_file, 'w', encoding='utf8') as f:
        f.writelines(lines)
    print(f"文件 {input_file} 去重完成")

def process_rules():
    """主处理逻辑"""
    os.makedirs(RULES_DIR, exist_ok=True)

    # 切换到临时目录
    os.chdir(TMP_DIR)

    # 读取错误域名
    error_domains = read_error_domains(ERROR_FILE)

    # 合并拦截规则
    merge_files('adblock*.txt', 'combined_adblock.txt')
    clean_file('combined_adblock.txt', 'cleaned_adblock.txt')
    filter_error_domains('cleaned_adblock.txt', 'cleaned_adblock_filtered.txt', error_domains)

    # 合并白名单规则
    merge_files('allow*.txt', 'combined_allow.txt')
    clean_file('combined_allow.txt', 'cleaned_allow.txt')

    # 将白名单追加到拦截规则中
    with open('cleaned_allow.txt', 'r') as f:
        allow_lines = f.readlines()
    with open('cleaned_adblock_filtered.txt', 'a') as f:
        f.writelines(allow_lines)
    print("白名单追加到拦截规则完成")

    # 去重规则文件
    remove_duplicates('cleaned_adblock_filtered.txt')

    # 保存最终文件
    adblock_file_new = os.path.join(RULES_DIR, 'adblock.txt')
    allow_file_new = os.path.join(RULES_DIR, 'allow.txt')
    os.rename('cleaned_adblock_filtered.txt', adblock_file_new)
    os.rename('cleaned_allow.txt', allow_file_new)
    print(f"规则文件已保存到 {RULES_DIR}")

if __name__ == '__main__':
    process_rules()