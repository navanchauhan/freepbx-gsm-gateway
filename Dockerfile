FROM tiredofit/freepbx:latest

USER root

# Fix Debian Buster archive repositories
RUN echo "deb http://archive.debian.org/debian/ buster main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list

# Install build dependencies for chan_dongle
RUN apt-get update -o Acquire::Check-Valid-Until=false && \
    apt-get install -y --no-install-recommends \
        build-essential \
        autoconf \
        automake \
        libtool \
        pkg-config \
        wget \
        unzip \
        libsqlite3-dev \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Download and compile chan_dongle from navanchauhan fork (Asterisk 18-23 compatible)
WORKDIR /usr/src
RUN wget --no-check-certificate -O chan_dongle.tar.gz \
    https://github.com/navanchauhan/asterisk-chan-dongle/archive/refs/heads/main.tar.gz && \
    tar -xzf chan_dongle.tar.gz && \
    mv asterisk-chan-dongle-main chan_dongle

# Build chan_dongle for Asterisk 17.9.3
WORKDIR /usr/src/chan_dongle
RUN ./bootstrap && \
    ./configure --with-astversion=17.9.3 && \
    make && \
    make install

# Create necessary directories
RUN mkdir -p /var/log/asterisk && \
    chmod 755 /var/log/asterisk

# Cleanup build artifacts
WORKDIR /
RUN rm -rf /usr/src/chan_dongle* && \
    apt-get purge -y build-essential autoconf automake libtool pkg-config wget unzip && \
    apt-get autoremove -y && \
    apt-get clean

# Expose Asterisk ports
EXPOSE 80 5060/udp 5060/tcp 5061/udp 10000-10200/udp

# Use the base image's entrypoint
