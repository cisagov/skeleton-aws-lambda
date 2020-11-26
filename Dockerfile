ARG PY_VERSION=3.8

FROM lambci/lambda:build-python$PY_VERSION
LABEL maintainer="mark.feldhousen@trio.dhs.gov"
LABEL vendor="Cyber and Infrastructure Security Agency"

# Declare it a second time so it's brought into this scope.
ARG PY_VERSION=3.8
ARG FILE_NAME=skeleton-aws-lambda
ARG IS_RELEASE=FALSE

ENV BUILD_PY_VERSION=$PY_VERSION
ENV BUILD_FILE_NAME=$FILE_NAME
ENV BUILD_IS_RELEASE=$IS_RELEASE

COPY build.sh .
COPY bump_version.sh .

COPY lambda_handler.py .

# Files needed to install local eal module
COPY README.md .
COPY requirements.txt .
COPY setup.py .
COPY eal ./eal

ENTRYPOINT ["./build.sh"]
