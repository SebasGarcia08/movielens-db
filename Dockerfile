FROM python:3.10-bullseye

WORKDIR /opt/oracle

RUN apt-get update && apt-get install -y libaio1 
RUN wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip && \
    unzip instantclient-basiclite-linuxx64.zip && rm -f instantclient-basiclite-linuxx64.zip && \
    cd /opt/oracle/instantclient* && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci && \
    echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf && ldconfig

RUN python -m pip install oracledb
WORKDIR    /app
COPY       . .
RUN        pip install -e .

# For this statement to work you need to add the next two lines into Pipfilefile
# [scripts]
# server = "python manage.py runserver 0.0.0.0:8000"
CMD ["python", "app.py"]