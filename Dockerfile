

FROM python:3.9

ADD . /app
WORKDIR /app

RUN  pip install  --index-url https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip \
    && pip install  --index-url https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY simhei.ttf /usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/
COPY matplotlibrc /usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/

#CMD python3 main.py
CMD python3 zhishu.py
#CMD ["python3","main.py"]

