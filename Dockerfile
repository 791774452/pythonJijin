

FROM python:3.9

# 拷贝SSH配置和密钥到容器
COPY ~/.ssh /root/.ssh

# 设置权限
RUN chmod 700 /root/.ssh && \
    chmod 600 /root/.ssh/id_rsa

ADD . /app
WORKDIR /app

RUN  pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple\
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY simhei.ttf /usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/
COPY matplotlibrc /usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]

#CMD python3 main.py
#CMD python3 zhishu.py
#CMD ["python3","main.py"]

