#!/bin/bash

if [ $# -lt 1 ]; then
    echo "请指定文件名"
    exit 127
fi

target_dir="posts/"
blog_name="$*"

cat >>"${target_dir}/$(date +'%Y-%m-%d')-${blog_name}.md" << eof
---
layout: post
title: "${blog_name}"
date: $(date +%FT%T%:z)
categories:
---
eof

echo "'$blog_name' created"
