FROM sphinxdoc/sphinx:2.4.4

COPY requirements.txt /
RUN pip install -r /requirements.txt
