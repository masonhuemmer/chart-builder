# build stage
FROM mcr.microsoft.com/vscode/devcontainers/python:3.9-bullseye AS builder

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY src/chart-builder /chart-builder/

# install dependencies and project
WORKDIR /chart-builder
RUN pdm install --prod --no-lock --no-editable


# run stage
FROM mcr.microsoft.com/vscode/devcontainers/python:3.9-bullseye

# retrieve packages from build stage
ENV PYTHONPATH=/chart-builder/python3.9/site-packages
COPY --from=builder /chart-builder/.venv/lib  /chart-builder

# copy script
COPY --from=builder /chart-builder/chart-builder /usr/local/bin
RUN chmod +x /usr/local/bin/chart-builder

# Kubectl, Helm
ENV KUBECTL_VERSION="latest" \
    HELM_VERSION="latest"
RUN curl --output /tmp/kubectl-helm-debian.sh https://raw.githubusercontent.com/microsoft/vscode-dev-containers/main/script-library/kubectl-helm-debian.sh
RUN apt-get update && bash /tmp/kubectl-helm-debian.sh ${KUBECTL_VERSION} ${HELM_VERSION}

# Set user
USER vscode

# Set Bash
ENTRYPOINT [ "/bin/bash" ]
