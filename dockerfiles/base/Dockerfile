FROM ubuntu:14.04.4
MAINTAINER Guang Cheng Li liguangc@cn.ibm.com

ENV codename trusty
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $codename main restricted universe multiverse" > /etc/apt/sources.list
RUN echo "deb http://archive.ubuntu.com/ubuntu/ ${codename}-updates main restricted universe multiverse" >> /etc/apt/sources.list
RUN echo "deb http://archive.ubuntu.com/ubuntu/ ${codename}-security main restricted universe multiverse" >> /etc/apt/sources.list

RUN apt-get update

RUN apt-get -y install openssh-server

RUN ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa

RUN echo root:passw0rd | chpasswd -S

RUN mkdir /var/run/sshd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
