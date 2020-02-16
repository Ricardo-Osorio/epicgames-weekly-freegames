FROM python:3.7-alpine3.11

# expose port
EXPOSE 8000

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.11/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.11/community" >> /etc/apk/repositories

# install chromedriver
RUN apk update \
 && apk add chromium chromium-chromedriver

# upgrade pip and install requirements.txt
ADD requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# add the script to where selenium is installed
ADD main.py /usr/local/lib/python3.7/site-packages

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# run the script
CMD [ "python3.7", "/usr/local/lib/python3.7/site-packages/main.py"]
