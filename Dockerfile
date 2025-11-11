FROM andrius/asterisk:23

USER root

# Install build dependencies for chan_dongle
RUN apt-get update && apt-get install -y \
    build-essential \
    autoconf \
    automake \
    libtool \
    pkg-config \
    wget \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and compile chan_dongle from navanchauhan fork (Asterisk 18-23 compatible)
WORKDIR /usr/src
RUN wget --no-check-certificate -O chan_dongle.tar.gz \
    https://github.com/navanchauhan/asterisk-chan-dongle/archive/refs/heads/main.tar.gz && \
    tar -xzf chan_dongle.tar.gz && \
    mv asterisk-chan-dongle-main chan_dongle

# Build chan_dongle for Asterisk 23
WORKDIR /usr/src/chan_dongle
RUN ./bootstrap && \
    ./configure --with-astversion=23.0.0 && \
    make && \
    make install

# Create necessary directories
RUN mkdir -p /var/log/asterisk && \
    chmod 755 /var/log/asterisk

# Cleanup build artifacts
WORKDIR /
RUN rm -rf /usr/src/chan_dongle* && \
    apt-get purge -y build-essential autoconf automake libtool pkg-config wget && \
    apt-get autoremove -y && \
    apt-get clean

# Expose Asterisk ports
EXPOSE 5060/udp 5060/tcp 5160/udp 5160/tcp 10000-10200/udp

# Use the base image's entrypoint
