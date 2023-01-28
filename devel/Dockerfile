FROM ubuntu:20.04

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  sudo \
&& rm -rf /var/lib/apt/lists/*

RUN echo "export PATH=\$PATH:\$HOME/genv/bin:\$HOME/genv/devel/shims" >> /root/.bashrc
RUN echo 'eval "$(genv init -)"' >> /root/.bashrc
