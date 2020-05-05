FROM nvidia/cuda:latest

# Install system dependencies
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential \
        curl \
        wget \
        git \
        unzip \
        screen \
        vim \
    && apt-get clean

# Install python miniconda3 + requirements
ENV MINICONDA_HOME="/opt/miniconda"
ENV PATH="${MINICONDA_HOME}/bin:${PATH}"
RUN curl -o Miniconda3-latest-Linux-x86_64.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && chmod +x Miniconda3-latest-Linux-x86_64.sh \
    && ./Miniconda3-latest-Linux-x86_64.sh -b -p "${MINICONDA_HOME}" \
    && rm Miniconda3-latest-Linux-x86_64.sh

# Code server
RUN wget https://github.com/cdr/code-server/releases/download/3.2.0/code-server-3.2.0-linux-x86_64.tar.gz && \
    tar -xzvf code-server-3.2.0-linux-x86_64.tar.gz && chmod +x code-server-3.2.0-linux-x86_64/code-server && \
    rm code-server-3.2.0-linux-x86_64.tar.gz

# Project dependencies
RUN conda install pytorch=0.4.0 torchvision cuda91 -c pytorch && \
    conda install scikit-image cython && \
    conda install visdom dominate -c conda-forge
COPY . /proSR
WORKDIR /proSR
RUN pip install -Ur requirements.txt

# Start container in notebook mode
CMD python 3 -m visdom && \
    /code-server-3.2.0-linux-x86_64/code-server --bind-addr 0.0.0.0:8080

# docker build -t prosr .
# docker run -e PASSWORD='yourpassword' -P 8097:8097 -p 8080:8080 -it prosr
