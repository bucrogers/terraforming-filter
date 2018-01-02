#Dockerfile to encapsulate terraforming-filter
#
#How-to build docker image (from working-directory having terraforming-filter source)
#  docker build -t terraforming-filter .
#
#How-to run docker container (from working-directory having *.tf files)
#Required args shown below, optional args follow
#
#  Syntax to run in foreground (to stop: ^C):
#    docker run -it --rm -v $(pwd):/indir -v <outdir>:/outdir terraforming-filter
#
# Syntax to run detached (to stop: docker rm -f tf1):
#    docker run -d --name tf1 -v $(pwd):/indir -v <outdir>:/outdir terraforming-filter


FROM python:3.6-alpine3.7

ENV JSON2HCL_VERSION=0.0.6

RUN apk update --no-cache \
    && apk add --no-cache curl \
    && curl -ssL -o /usr/local/bin/json2hcl https://github.com/kvz/json2hcl/releases/download/v${JSON2HCL_VERSION}/json2hcl_v${JSON2HCL_VERSION}_linux_amd64 \
    && chmod +x /usr/local/bin/json2hcl

#Install json2hcl
#ADD https://github.com/kvz/json2hcl/releases/download/v${JSON2HCL_VERSION}/json2hcl_v${JSON2HCL_VERSION}_linux_amd64 /usr/local/bin/json2hcl
#RUN chmod +x /usr/local/bin/json2hcl

#Set up app
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt \
    && chmod +x docker-entrypoint.sh \
    && chmod +x run-json2hcl.sh

#set up runtime workdir for tf files
WORKDIR /indir

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD [""]
