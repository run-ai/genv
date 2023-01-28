FROM genv:devel

RUN apt-get update && apt-get install -y --no-install-recommends \
  openssh-server \
&& rm -rf /var/lib/apt/lists/*

RUN mkdir -p /run/sshd

RUN passwd -d root

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
RUN sed -i 's/#PermitEmptyPasswords no/PermitEmptyPasswords yes/g' /etc/ssh/sshd_config
RUN sed -i "/^AcceptEnv/s/$/ GENV_*/" /etc/ssh/sshd_config

EXPOSE 22

CMD [ "/usr/sbin/sshd", "-D" ]
