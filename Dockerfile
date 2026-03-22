# Base Image 
FROM fedora:40

# 1. Setup
RUN mkdir -p /bot && chmod 777 /bot
WORKDIR /bot
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Africa/Lagos
ENV TERM=xterm

# 2. Install Dependencies (بدون aria2 نهائي)
RUN dnf -qq -y update && \
    dnf -qq -y install git bash xz wget curl pv jq python3-pip mediainfo psmisc procps-ng && \
    python3 -m pip install --upgrade pip setuptools

# 3. Install ffmpeg
RUN arch=$(arch | sed s/aarch64/arm64/ | sed s/x86_64/64/) && \
    wget -q https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n7.1-latest-linux${arch}-gpl-7.1.tar.xz && \
    tar -xvf *xz && \
    cp *7.1/bin/* /usr/bin && \
    rm -rf *xz *7.1

# 4. Copy project
COPY . .

# 5. Install requirements (لازم تتأكد بنفسك إنها مفيهاش aria2)
RUN pip3 install -r requirements.txt

# 6. Cleanup
RUN dnf clean all

# 7. Run
CMD ["bash","run.sh"]
