FROM airbyte/python-connector-base:1.0.0

WORKDIR /airbyte/integration_code

COPY requirements.txt ./
COPY setup.py ./
COPY . ./source_groww

RUN pip install -r requirements.txt && pip install .

ENV AIRBYTE_ENTRYPOINT="python -m source_groww.run"

ENTRYPOINT ["python", "-m", "source_groww.run"]
