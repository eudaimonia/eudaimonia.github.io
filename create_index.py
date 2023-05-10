#!/usr/bin/env python3

import os
import re
import posixpath

# 遍历posts目录下的所有文件
links = []
for filename in os.listdir('posts'):
    if filename.endswith('.md'):
        # 读取文件内容
        with open(os.path.join('posts', filename), 'r', encoding='utf-8') as f:
            file_content = f.read()

        # 在文件内容中查找元信息区
        match = re.match(r'---\n(.*?)\n---\n(.*)', file_content, re.S)
        if match:
            # 解析元信息
            meta_str = match.group(1)
            meta = {}
            for line in meta_str.split('\n'):
                if line.strip():
                    key, value = line.split(':', 1)
                    meta[key.strip()] = value.strip()

            # 构造链接格式
            title = meta.get('title').strip('"')
            file_path = posixpath.join('posts', filename)
            link = f'[{title}]({file_path})'

            # 将链接添加到列表中
            links.append(link)

# 生成README.md文件内容
readme_content = f'# My Blog\n\n## Posts\n'
for link in links:
    readme_content += f'- {link}\n'

# 将README.md文件内容写入文件
with open('readme.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)