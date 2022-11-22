# Isedol and Woowakgood Stream Recorder
This script allows you to record twitch streams live to .mp4 files.  
It is an improved version of [junian's twitch-recorder](https://gist.github.com/junian/b41dd8e544bf0e3980c971b0d015f5f6), migrated to [**helix**](https://dev.twitch.tv/docs/api) - the new twitch API. It uses OAuth2.
## Requirements
1. [python3.9](https://www.python.org/downloads/release/python-3913/) or higher  
2. [streamlink](https://streamlink.github.io/)  
3. [ffmpeg](https://ffmpeg.org/)
    * ffmpeg library path must add to environment variable PATH
        * Path\to\Extract\ffmpeg-something-full_build\bin 
        * ex) C:\Users\user\Downloads\ffmpeg-2022-11-03-git-5ccd4d3060-full_build\bin
4. [youtube-uploader](https://github.com/tokland/youtube-upload)

## Setting up in Docker

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
root_path = "C:/User/yourname/Videos/"
client_id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
client_secret = "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
```
`root_path` - path to a folder where you want your VODs to be saved to  
`client_id` - you can grab this from [here](https://dev.twitch.tv/console/apps) once you register your application  
`client_secret` - you generate this [here](https://dev.twitch.tv/console/apps) as well, for your registered application

You can run the scipt from `cmd` or [terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701?activetab=pivot:overviewtab), by simply going to the directory where the script is located at and using command:
```shell script
python Gui.py
```
The optional parameters should work exactly the same as on Linux.