

FROM 791774452/xiaolu:v1

ADD . /opt
WORKDIR /opt
#
RUN  pip3 install --upgrade pip \
    && pip3 install -r requirements.txt

CMD python3 main.py
#CMD ["python3","main.py"]

