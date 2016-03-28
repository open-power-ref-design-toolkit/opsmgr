This is the repository of the Dockerfiles for Ulysses operational management project.


The dockerimages/ulysses/base/Dockerfile is the base image for Ulysses docker images.

The dockerimages/ulysses/elk/Dockerfile is the ELK server docker file,
use the following command to build docker image:

*docker build -t ulysses/elk -f Dockerfile .*

Then start the docker instance with: 

*docker run -d -p 5601:5601 -p 9200:9200 -p 9300:9300 -v /elk:/elk ulysses/elk*
