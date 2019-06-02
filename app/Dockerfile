FROM python:3.6
RUN pip3 install Flask
RUN pip3 install kubernetes
RUN pip3 install flask_wtf
RUN pip3 install flask_oauthlib
WORKDIR /usr/src/app

COPY ./ ./
ENV FLASK_APP app.py

EXPOSE 5000
CMD ["python", "app.py", "--debug"]
#CMD ["python", "app.py"]
