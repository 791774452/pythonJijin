#!/bin/bash
echo "140.82.112.4 github.com" >> /etc/hosts

cd /app
git pull origin master

python3 zhishu_tiantian.py