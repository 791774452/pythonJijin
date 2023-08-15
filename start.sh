#!/bin/bash

cd /app
git pull

python3 zhishu.py

git add data.json
git commit -m "更新基准价"
git push origin master