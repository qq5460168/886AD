import os
import glob
import re
from pathlib import Path

# 切换到临时目录
os.chdir('tmp')

# 函数：合并文件
def merge_files(pattern, output_file):
    print(f"合并符合模式 {pattern} 的文件到 {output_file}")
    file_list = glob.glob(pattern)
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file in file_list:
            with open(file, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
                outfile.write('\n')

# 函数：清理规则文件
def clean_rules(input_file, output_file):
    print(f"清理规则文件 {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    # 移除注释和无效的行
    content = re.sub(r'^[!].*$', '', content, flags=re.MULTILINE)  # 以 ! 开头的行
    content = re.sub(r'^#(?!\s*#).*$', '', content, flags=re.MULTILINE)  # 单井号注释行
    content = re.sub(r'^\s*$', '', content, flags=re.MULTILINE)  # 空行
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

# 合并并清理拦截规则
merge_files('adblock*.txt', 'combined_adblock.txt')
clean_rules('combined_adblock.txt', 'cleaned_adblock.txt')
print("拦截规则合并和清理完成")

# 合并并清理白名单规则
merge_files('allow*.txt', 'combined_allow.txt')
clean_rules('combined_allow.txt', 'cleaned_allow.txt')
print("白名单规则合并和清理完成")

# 提取白名单规则到 allow.txt
print("提取白名单规则到 allow.txt")
with open('cleaned_allow.txt', 'r', encoding='utf-8') as f:
    # 匹配白名单规则，规则以 "@@||" 开头，且以 "^" 或 "^$important" 结尾
    allow_lines = [line for line in f if re.match(r'^@@\|\|.*\^(?:$|\$important)$', line)]

with open('allow.txt', 'w', encoding='utf-8') as f:
    f.writelines(allow_lines)

# 将白名单规则追加到拦截规则中
print("将白名单规则追加到拦截规则中")
with open('cleaned_adblock.txt', 'a', encoding='utf-8') as outfile:
    outfile.writelines(allow_lines)

# 移动文件到目标目录
print("移动规则文件到目标目录")
current_dir = os.getcwd()
target_dir = os.path.join(current_dir, '../data/rules/')
Path(target_dir).mkdir(parents=True, exist_ok=True)

os.rename('cleaned_adblock.txt', os.path.join(target_dir, 'adblock.txt'))
os.rename('allow.txt', os.path.join(target_dir, 'allow.txt'))

# 去重规则文件
print("规则去重中")
os.chdir(target_dir)
for file in os.listdir(target_dir):
    if file.endswith('.txt'):
        with open(file, 'r', encoding='utf-8') as f:
            unique_lines = sorted(set(f.readlines()))
        with open(file, 'w', encoding='utf-8') as f:
            f.writelines(unique_lines)
print("规则去重完成")