ARG PY_VERSION
FROM lambci/lambda:build-python$PY_VERSION
LABEL maintainer="mark.feldhousen@trio.dhs.gov"
LABEL vendor="Cyber and Infrastructure Security Agency"

COPY build.sh .

# Files needed to install local eal module
COPY setup.py .
COPY requirements.txt .
COPY README.md .
COPY eal ./eal

COPY lambda_handler.py .

ENTRYPOINT ["./build.sh", "$PY_VERSION"]
