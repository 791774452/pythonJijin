

FROM python:3.9

ADD . /app
WORKDIR /app

RUN  pip3 install --upgrade pip \
    && pip3 install -r requirements.txt

COPY simhei.ttf /usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/fonts
COPY matplotlibrc /usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/ttf

CMD python3 main.py
#CMD ["python3","main.py"]

