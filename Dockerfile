# install ubuntu
FROM		ubuntu:22.04
RUN			apt-get -y update

# install dependencies
RUN			apt -y install curl vim software-properties-common ffmpeg streamlink git

# move to home directory
WORKDIR 	/root

# install pip
RUN			curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN 		python3 get-pip.py

# clone isedol woowakgood stream recorder repository
RUN 		git clone https://github.com/wlsdml1114/isedol_and_wakgood-stream-recorder.git

# move to repository
WORKDIR 	isedol_and_wakgood-stream-recorder/

# clone youtube-upload repository
RUN			git clone https://github.com/tokland/youtube-upload.git
WORKDIR		youtube-upload/
RUN 		pip install --upgrade google-api-python-client oauth2client progressbar2 && \
    		python3 setup.py install

