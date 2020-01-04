FROM python:3.7-alpine3.8

# expose port
EXPOSE 8000

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.8/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.8/community" >> /etc/apk/repositories

# install chromedriver
RUN apk update
RUN apk add chromium chromium-chromedriver

# upgrade pip
RUN pip install --upgrade pip

# install selenium
RUN pip install selenium

# add the script to where selenium is installed
ADD main.py /usr/local/lib/python3.7/site-packages

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# run the script
CMD [ "python3.7", "/usr/local/lib/python3.7/site-packages/main.py"]
