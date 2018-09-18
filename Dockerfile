FROM python:3
ENV PYTHONUNBUFFERED 1

RUN mkdir /src
WORKDIR /src
ADD . /src
RUN pip install -r requirements.txt
RUN python3 manage.py collectstatic --noinput
RUN for file in $(find /src/static_root -name "*.scss"); do pyscss "$file" -o "${file%.*}.css"; done

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]
