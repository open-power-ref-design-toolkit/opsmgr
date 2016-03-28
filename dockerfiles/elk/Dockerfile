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

RUN apt-get -y install openjdk-7-jre

VOLUME /elk

#0. ELK setup
#Install Redis, not required for now.
#needs to add port 6379 into the list
#RUN apt-get -y install redis-server redis-tools
#RUN sed -i 's/bind 127.0.0.1/#bind 127.0.0.1/' /etc/redis/redis.conf

#RUN echo "service redis-server start" >> /bin/startservices


#1. Setup sources.list files
RUN wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
RUN echo "deb http://packages.elastic.co/elasticsearch/2.x/debian stable main" > /etc/apt/sources.list.d/elasticsearch-2.x.list 
RUN echo "deb http://packages.elastic.co/logstash/2.2/debian stable main" > /etc/apt/sources.list.d/logstash-2.2.x.list
RUN echo "deb http://packages.elastic.co/kibana/4.4/debian stable main" > /etc/apt/sources.list.d/kibana-4.4.x.list
RUN apt-get update


#2. Install Elasticsearch
RUN apt-get -y install elasticsearch
RUN echo "cluster.name: elk" >> /etc/elasticsearch/elasticsearch.yml
RUN echo "node.name: elkserver" >> /etc/elasticsearch/elasticsearch.yml
RUN echo "service elasticsearch start" >> /bin/startservices

#3. Install Logstash
RUN apt-get -y install logstash
#TODO: config files in /etc/logstash/conf.d/

RUN echo "service logstash start" >> /bin/startservices

#4. Install Kibana
RUN apt-get -y install kibana
#TODO: config file /opt/kibana/config/kibana.yml
RUN echo "service kibana start" >> /bin/startservices

# Put sshd at the end of /bin/startservices
RUN echo "/usr/sbin/sshd -D" >> /bin/startservices


RUN chmod 755 /bin/startservices

#elasticsearch ports: 9200 9300, logstash port xxx, kibbana port 5601
EXPOSE 22 5601 9200 9300 

CMD /bin/startservices
