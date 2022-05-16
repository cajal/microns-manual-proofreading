FROM at-docker.ad.bcm.edu:5000/microns-base 
LABEL mantainer="Stelios Papadopoulos <spapadop@bcm.edu>"

RUN pip3 install \
        cloud-volume \
        analysisdatalink\
        caveclient \
        nglui

WORKDIR /root
ARG CLOUDVOLUME_TOKEN
RUN mkdir -p .cloudvolume/secrets
RUN echo "{\"token\": \"${CLOUDVOLUME_TOKEN:-}\"}" > .cloudvolume/secrets/cave-secret.json

# copy this project and install
COPY . /src/microns-manual-proofreading
RUN pip3 install --prefix=$(python -m site --user-base) -e /src/microns-manual-proofreading/python/microns-manual-proofreading
RUN pip3 install --prefix=$(python -m site --user-base) -e /src/microns-manual-proofreading/python/microns-manual-proofreading-api
