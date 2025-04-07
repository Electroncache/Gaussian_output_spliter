import subprocess
import os
import time
import sys
import re
import shutil

class filename_class:
    def __init__(self, fullpath):
        fullpath = fullpath.replace('\\', '/')
        self.re_path_temp = re.match(r".+/", fullpath)
        if self.re_path_temp:
            self.path = self.re_path_temp.group(0)  # 包括最后的斜杠
        else:
            self.path = ""
        self.name = fullpath[len(self.path):]
        self.name_stem = self.name[:self.name.rfind('.')]  # not including "."

        self.append = self.name[len(self.name_stem) - len(self.name) + 1:]
        self.only_remove_append = self.path + self.name_stem  # not including "."

    def replace_append_to(self, new_append):
        return self.only_remove_append + '.' + new_append

# 创建或清空tmp文件夹
tmp_dir = os.path.join(os.getcwd(), "tmp")
if os.path.exists(tmp_dir):
    # 清空文件夹
    print(f"清空tmp文件夹: {tmp_dir}")
    for file_name in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, file_name)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"删除文件 {file_path} 时出错: {e}")
else:
    # 创建文件夹
    print(f"创建tmp文件夹: {tmp_dir}")
    os.makedirs(tmp_dir)

input_filenames = []
specified_queue = ""
if len(sys.argv) > 1:
    input_filenames = sys.argv[1:]

if not input_filenames:
    print("Filenames (end with empty line):")
    while True:
        input_filename = input()
        if input_filename:
            input_filenames.append(input_filename)
        else:
            break

def split_list(input_list: list, separator, lower_case_match=False, include_separator=False, include_separator_after=False, include_empty=False):
    '''

    :param input_list:
    :param separator: a separator, either a str or function. If it's a function, it should take a str as input, and return
    :param lower_case_match:
    :param include_separator:
    :param include_empty:
    :return:
    '''
    ret = []
    temp = []

    if include_separator or include_separator_after:
        assert not (include_separator and include_separator_after), 'include_separator and include_separator_after can not be True at the same time'

    for item in input_list:

        split_here_bool = False
        if callable(separator):
            split_here_bool = separator(item)
        elif isinstance(item, str) and item == separator:
            split_here_bool = True
        elif lower_case_match and isinstance(item, str) and item.lower() == separator.lower():
            split_here_bool = True

        if split_here_bool:
            if include_separator_after:
                temp.append(item)
            ret.append(temp)
            temp = []
            if include_separator:
                temp.append(item)
        else:
            temp.append(item)
    ret.append(temp)

    if not include_empty:
        ret = [x for x in ret if x]

    return ret

for file in input_filenames:
    input_file_name = filename_class(file).name_stem  # Get the input file name without extension

    with open(file) as output_file_object:
        output_lines = output_file_object.readlines()

    # 修改点1: 支持 Gaussian 16
    output_steps = split_list(output_lines, lambda x: 'Normal termination of Gaussian' in x, include_separator_after=True)

    output_steps_process = []
    for step in output_steps:
        if output_steps_process and True in ['Proceeding to internal job step' in x for x in step[:20]]:
            output_steps_process[-1] = output_steps_process[-1] + step
        else:
            output_steps_process.append(step)

    output_steps = output_steps_process

    # 提取每一步的chk文件名
    chk_filenames = []
    for step in output_steps:
        chkfile_filename = ""
        for count, line in enumerate(step):
            if "%chk" in line:
                chkfile_filename += (line.strip().lstrip('%chk='))
                for chk_lines in step[count + 1:]:
                    if '.chk' in chkfile_filename:
                        break
                    chkfile_filename += chk_lines.strip()
                break
        chkfile_filename = chkfile_filename.strip()
        if chkfile_filename:
            chk_filenames.append(filename_class(chkfile_filename).name_stem)
        else:
            chk_filenames.append("")

    # 修改点2: 改进输出文件命名
    output_filenames = []
    # 找出重复的chk文件名
    chk_names_count = {}
    for chk_name in chk_filenames:
        if chk_name:
            if chk_name in chk_names_count:
                chk_names_count[chk_name] += 1
            else:
                chk_names_count[chk_name] = 1
    
    # 为每一步生成输出文件名 (只保留文件名，不含路径)
    base_file_name = filename_class(file).name_stem
    for step_count, chk_name in enumerate(chk_filenames):
        if not chk_name:
            # 没有chk文件名的情况
            output_filenames.append(f"{base_file_name}_step{step_count+1}.log")
        elif chk_names_count[chk_name] > 1:
            # 重复的chk文件名，添加步骤顺序号
            duplicate_index = sum(1 for i in range(step_count) if chk_filenames[i] == chk_name) + 1
            output_filenames.append(f"{base_file_name}_{chk_name}_{duplicate_index}.log")
        else:
            # 唯一的chk文件名
            output_filenames.append(f"{base_file_name}_{chk_name}.log")

    print(f"Total steps: {len(output_steps)}")

    for step_count, step in enumerate(output_steps):
        # 将输出文件保存到tmp文件夹中
        output_filename = os.path.join(tmp_dir, output_filenames[step_count])
        with open(output_filename, 'w') as output_file:
            output_file.write("".join(step))
            print(f"Step {step_count+1}: {len(step)} lines -> {output_filename}")

print("所有分割后的文件已保存到tmp文件夹中。")