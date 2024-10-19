import os

os.chdir('tmp')

def replace_content_in_file(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    with open(output_file, 'w') as file:
        for line in lines:
            if ':' not in line and '.js' not in line and '/' not in line:
                if line.strip().startswith("||") and line.strip().endswith("^"):
                    line = line.replace("||", "DOMAIN,").replace("^", ",reject")
                file.write(line)

input_file_path = ".././data/rules/dns.txt"
output_file_path = ".././data/rules/qx.list"
replace_content_in_file(input_file_path, output_file_path)
