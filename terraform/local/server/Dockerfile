FROM ubuntu:24.04
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv openssh-server sudo python3 python3-apt ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /run/sshd \
 && sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config \
 && systemctl enable ssh
RUN mkdir -p /home/ubuntu/.ssh \
 && chmod 700 /home/ubuntu/.ssh \
 && chown -R ubuntu:ubuntu /home/ubuntu \
 && echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/ubuntu
EXPOSE 22
STOPSIGNAL SIGRTMIN+3
CMD ["/sbin/init"]
