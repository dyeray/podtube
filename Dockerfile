FROM gcr.io/google_appengine/python-compat
ADD . /app
RUN apt-get update && apt-get install -y \
    libxml2-dev\
    libxslt1-dev\
    python-dev
RUN pip install -r requirements.txt