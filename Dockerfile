 FROM python:3
 ENV PYTHONUNBUFFERED 1

 RUN mkdir /src
 WORKDIR /src
 ADD . /src
 RUN pip install -r requirements.txt
 RUN for file in $(find static_root -name "*.scss"); do pyscss "$file" -o "${file%.*}.css"; done
