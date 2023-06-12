FROM ubuntu:20.04

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  python3-pip \
  sudo \
&& rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "/bin/bash" ]
