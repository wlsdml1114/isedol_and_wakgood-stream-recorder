# Isedol and Woowakgood Stream Recorder
This script allows you to record twitch streams live to .mp4 files.  
It is an improved version of [junian's twitch-recorder](https://gist.github.com/junian/b41dd8e544bf0e3980c971b0d015f5f6), migrated to [**helix**](https://dev.twitch.tv/docs/api) - the new twitch API. It uses OAuth2.
## Requirements (without Docker)
### If you want to run this project in Docker, you don't need to install requirements below
1. [python3.9](https://www.python.org/downloads/release/python-3913/) or higher  
2. [streamlink](https://streamlink.github.io/)  
3. [ffmpeg](https://ffmpeg.org/)
    * ffmpeg library path must add to environment variable PATH
        * Path\to\Extract\ffmpeg-something-full_build\bin 
        * ex) C:\Users\user\Downloads\ffmpeg-2022-11-03-git-5ccd4d3060-full_build\bin
4. [youtube-uploader](https://github.com/tokland/youtube-upload)

## Setting up in Docker
1) Download and install docker
    * [Docker](https://www.docker.com/)
2) Download or build docker image (choose one)
    1. Download docker image
        ```
        > docker pull wlsdml1114/twitch_stream_recorder:1.1

        > docker images
        REPOSITORY                          TAG       IMAGE ID       CREATED             SIZE
        wlsdml1114/twitch_stream_recorder   1.1       213455da8a36   About an hour ago   1.13GB
        ```
    2. Build docker image using github repository
        ```
        > docker build -t twitch_recorder https://github.com/wlsdml1114/isedol_and_wakgood-stream-recorder.git

        > docker images
        REPOSITORY        TAG       IMAGE ID       CREATED          SIZE
        twitch_recorder   latest    a85da980fccc   17 minutes ago   1.26GB
        ```
3) Docker run on background
    1. Check Image repository
        ```
        > docker images
        REPOSITORY                          TAG       IMAGE ID       CREATED             SIZE
        twitch_recorder                     latest    a85da980fccc   About an hour ago   1.26GB
        wlsdml1114/twitch_stream_recorder   1.1       213455da8a36   About an hour ago   1.13GB
        ```
    2. Docker run with mount the path where streaming video will saved
        ```
        # runnig format
        # docker run -i -t -d --name container_name -v {your/computer/streaming/save/path}:/data/ REPOSITORY:TAG
        
        > docker run -i -t -d --name recorder_docker -v C:\Users\user\Documents:/data/ wlsdml1114/twitch_stream_recorder:1.1
        cf3c6c202edbf934d71dff2bbac197d08495cdf36fd9128d4113bd2e84acbf81
        
        > docker ps
        CONTAINER ID   IMAGE                                   COMMAND   CREATED         STATUS         PORTS     NAMES
        cf3c6c202edb   wlsdml1114/twitch_stream_recorder:1.1   "bash"    6 seconds ago   Up 5 seconds             recorder_docker
        ```
    3. Make sure your container name and attach to container using container name
        ```
        > docker attach recorder_docker
        root@cf3c6c202edb:~/isedol_and_wakgood-stream-recorder/youtube-upload#
        ```
    4. Create config.yaml in mounted path using notepad(메모장)
        ```
        root@cf3c6c202edb:~/isedol_and_wakgood-stream-recorder/youtube-upload# cd /data/
        root@cf3c6c202edb:/data# ls
        config.yaml (may here is other folders or files)
        ```
        * contents of config.yaml file
        * `client_id` - you can grab this from [here](https://dev.twitch.tv/console/apps) once you register your application  
        * `client_secret` - you generate this [here](https://dev.twitch.tv/console/apps) as well, for your registered application
            ```
            client_id : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            client_secret : "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
            ```
    5. Run recorder
        ```
        root@cf3c6c202edb:~/isedol_and_wakgood-stream-recorder# python3 main_docker.py
        streamer ID or name :
        ```
        * enter streamer id who you want to record
        ```
        streamer ID or name : wlsdml1114
        user id is in name list
        checking for wlsdml1114 every 15 seconds, recording with best quality
        wlsdml1114 online, stream recording in session
        [cli][info] streamlink is running as root! Be careful!
        [cli][info] Found matching plugin twitch for URL twitch.tv/wlsdml1114
        [cli][info] Available streams: audio_only, 160p (worst), 360p, 480p, 720p60 (best)
        [cli][info] Opening stream: 720p60 (hls)
        [plugins.twitch][info] Will skip ad segments
        [plugins.twitch][info] Waiting for pre-roll ads to finish, be patient
        [stream.hls][info] Filtering out segments and pausing stream output
        [stream.hls][info] Resuming stream output
        [download][..8h58m15s - test.mp4] Written 146.8 MB (6m3s @ 400.0 KB/s) 
        ```
        * running recorder in background (Optional) 
            * if you want to run recorder in background, you have to fix streamer name using --name option like below example
        ```
        root@cf3c6c202edb:~/isedol_and_wakgood-stream-recorder# nohup python3 main_docker.py --name viichan6 &
        [1] 213
        root@cf3c6c202edb:~/isedol_and_wakgood-stream-recorder# nohup: ignoring input and appending output to 'nohup.out'
        root@cf3c6c202edb:~/isedol_and_wakgood-stream-recorder# cat nohup.out
        checking for viichan6 every 15 seconds, recording with best quality
        viichan6 online, stream recording in session
        [cli][info] streamlink is running as root! Be careful!
        [cli][info] Found matching plugin twitch for URL twitch.tv/viichan6
        [cli][info] Available streams: audio_only, 160p (worst), 360p, 480p, 720p60 (best)
        [cli][info] Opening stream: 720p60 (hls)
        [plugins.twitch][info] Will skip ad segments
        [plugins.twitch][info] Waiting for pre-roll ads to finish, be patient
        [stream.hls][info] Filtering out segments and pausing stream output
        [stream.hls][info] Resuming stream output
        ```

    6. Youtube upload when streaming end (Optional)
        * Frist you have to make your project and credential
            * Go to the Google [console](https://console.developers.google.com/).
            * _Create project_.
            * Side menu: _APIs & auth_ -> _APIs_
            * Top menu: _Enabled API(s)_: Enable all Youtube APIs.
            * Side menu: _APIs & auth_ -> _Credentials_.
            * _Create a Client ID_: Add credentials -> OAuth 2.0 Client ID -> Other -> Name: youtube-upload -> Create -> OK
            * _Download JSON_: Under the section "OAuth 2.0 client IDs". Save the file to your local system. 
            * Use this JSON as your credentials file: `--client-secrets=CLIENT_SECRETS` or copy it to `~/client_secrets.json`.

            *Note: ```client_secrets.json``` is a file you can download from the developer console, the credentials file is something auto generated after the first time the script is run and the google account sign in is followed, the file is stored at ```~/.youtube-upload-credentials.json```.*
        * For make cretential run code below just once
            ```
            root@cf3c6c202edb:/data# youtube-upload --client-secrets ./client_secret.json --title test
            Using client secrets: ./client_secret.json
            Using credentials file: /root/.youtube-upload-credentials.json
            /usr/local/lib/python3.10/dist-packages/oauth2client/_helpers.py:255: UserWarning: Cannot access /root/.youtube-upload-credentials.json: No such file or directory
            warnings.warn(_MISSING_FILE_MESSAGE.format(filename))
            Check this link in your browser: https://accounts.google.com/o/oauth2/auth?client_id=blablablablablablalba~~~~~~shomtehing~~~~response_type=code
            Enter verification code: somethingsomethingblablasomethingsomething
            ```
        * Delete '#' on recorder_docker.py lines 90
            ```
            #self.upload_vod(processed_filename, processed_filename) # if you want upload recoding file
            ->
            self.upload_vod(processed_filename, processed_filename) # if you want upload recoding file
            ```
    7. Run multiple recorder in background for each streamer
        ```
        root@85322e5f76d3:~/isedol_and_wakgood-stream-recorder# ps -ef
        UID        PID  PPID  C STIME TTY          TIME CMD
        root         1     0  0 12:12 pts/0    00:00:00 /usr/bin/qemu-aarch64 /usr/bin/bash bash
        root        66     1  1 12:21 pts/0    00:01:39 /usr/bin/qemu-aarch64 /usr/bin/python3 python3 main_docker.py --name viichan6
        root        94     1  4 12:32 pts/0    00:04:41 /usr/bin/qemu-aarch64 /usr/bin/python3 python3 main_docker.py --name cotton__123
        root       101     1  4 12:34 pts/0    00:04:36 /usr/bin/qemu-aarch64 /usr/bin/python3 python3 main_docker.py --name jingburger
        and so on..
        ```

## Setting up in Windows
1) Check if you have latest version of streamlink:
    * `streamlink --version` shows current version
    * `streamlink --version-check` shows available upgrade
    * `sudo pip install --upgrade streamlink` do upgrade

2) Install `requests` module
    * ```python -m pip install requests```  
3) Install `PyQt5` module
    * ```python -m pip install PyQt5```
4) Create `config.yaml` file in the same directory as `Gui.py` with:
```properties
root_path : "C:/User/yourname/Videos/"
client_id : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
client_secret : "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
```
`root_path` - path to a folder where you want your VODs to be saved to  
`client_id` - you can grab this from [here](https://dev.twitch.tv/console/apps) once you register your application  
`client_secret` - you generate this [here](https://dev.twitch.tv/console/apps) as well, for your registered application

You can run the scipt from `cmd` or [terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701?activetab=pivot:overviewtab), by simply going to the directory where the script is located at and using command:
```shell script
python Gui.py
```
The optional parameters should work exactly the same as on Linux.