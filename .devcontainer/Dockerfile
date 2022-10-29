# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.224.2/containers/debian/.devcontainer/base.Dockerfile

# [Choice] Debian version (use bullseye on local arm64/Apple Silicon): bullseye, buster
ARG VARIANT="buster"
FROM mcr.microsoft.com/vscode/devcontainers/base:0-${VARIANT}

# ** [Optional] Uncomment this section to install additional packages. **
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# Python
ENV PYTHON_VERSION="3.9" \
    PYTHON_PATH=/usr/local/python \
    SITE_PACKAGES=/usr/local/python/lib/python${PYTHON_VERSION}/site-packages \
    PIPX_HOME=/usr/local/py-utils \
    PIPX_BIN_DIR=/usr/local/py-utils/bin
ENV PATH=${PYTHON_PATH}/bin:${PATH}:${PIPX_BIN_DIR}:${SITE_PACKAGES}
RUN curl --output /tmp/python-debian.sh https://raw.githubusercontent.com/microsoft/vscode-dev-containers/main/script-library/python-debian.sh
RUN apt-get update && bash /tmp/python-debian.sh "${PYTHON_VERSION}" "${PYTHON_PATH}" "${PIPX_HOME}"
RUN apt-get -y install python3-venv

# PDM
RUN curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 - --path /usr/local
RUN pdm plugin add pdm-vscode

# Azure CLI
ENV AZCLI_VERSION="latest"
RUN curl --output /tmp/azcli-debian.sh https://raw.githubusercontent.com/microsoft/vscode-dev-containers/main/script-library/azcli-debian.sh
RUN apt-get update && bash /tmp/azcli-debian.sh "${AZCLI_VERSION}"

# Kubectl, Helm
ENV KUBECTL_VERSION="latest" \
    HELM_VERSION="latest"
RUN curl --output /tmp/kubectl-helm-debian.sh https://raw.githubusercontent.com/microsoft/vscode-dev-containers/main/script-library/kubectl-helm-debian.sh
RUN apt-get update && bash /tmp/kubectl-helm-debian.sh ${KUBECTL_VERSION} ${HELM_VERSION}