# terraforming-filter 

For the purpose of reverse-engineering a cloud diagram, convert output from [terraforming](https://github.com/dtan4/terraforming) to be compatible
with [blast-radius](https://github.com/28mm/blast-radius)

Performs the following filtering:
* Removes duplicate resources (such as dup EC2 instances provisioned by AWS ElasticBeanstalk)
* TODO tag grouping by environment / app - to yield a manageable-sized diagram per app / environment

### Running with Docker (recommended)
Running with docker is recommended to most easily handle installation of all dependencies.

How-to build docker image (from working-directory having terraforming-filter source)

    $ docker build -t terraforming-filter .

How-to run docker container (from working-directory having *.tf files)

Required args shown below, optional args follow

  Syntax to run in foreground (to stop: ^C):

    $ docker run -it --rm -v $(pwd):/indir -v <outdir>:/outdir terraforming-filter

 Syntax to run detached (to stop: docker rm -f tf1):

    $ docker run -d --name tf1 -v $(pwd):/indir -v <outdir>:/outdir terraforming-filter

### Running without Docker

Prerequisites - see Dockerfile for details
* Python3
* pip install -r requirements.txt
* Install json2hcl

    $ python3 main.py INPUTDIR OUTPUTDIR

INPUTDIR: *.tf files created by terraforming

OUTPUTDIR: target for filtered *.tf files to be later graphed by blast-radius

### Implementation Notes
* Uses [pyhcl](https://github.com/virtuald/pyhcl) library to read hcl-formatted .tf files
* Internal filtering performed on json (python dictionaries)
* Uses [json2hcl](https://github.com/kvz/json2hcl) to convert programmatically-generated json to hcl-formatted .tf files
