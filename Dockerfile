

FROM  python:3.9

ADD . /app
WORKDIR /app
#
RUN  pip3 install --upgrade pip \
    && pip3 install -r requirements.txt

#CMD python3 main.py
CMD ["python3","main.py"]

