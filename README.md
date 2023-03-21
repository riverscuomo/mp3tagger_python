# MP3 Tagger [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)

A python GUI that builds filters for the Mp3Tag application. I use this script to filter my demos by various custom tags. You can easily customize the script to filter by any tag you want.

Because it's a pain to write Mp3Tag filters like this `((NOT BPM LESS 80 AND NOT BPM GREATER 100) OR (NOT BPM LESS 160 AND NOT BPM GREATER 200)) AND  (NOT %_folderpath% MATCHES solo|covers|previous|hold|szn|beats) AND  (NOT melodyStart MATCHES before) AND  (NOT Mode MATCHES mixo|mixed) AND (Melody MATCHES 3 OR Melody ABSENT) AND (FirstChord MATCHES 6 OR FirstChord ABSENT) AND  (NOT Feel MATCHES waltz|triplet) AND (Section MATCHES chorus OR Section ABSENT) AND  (NOT Section MATCHES instr|riff) AND  (NOT Masterpiece MATCHES 2|1) AND  (NOT Fall MATCHES 3) AND (Genesis MATCHES aku OR Genesis ABSENT) AND (jd MATCHES 5 OR jd ABSENT) AND (cowriter MATCHES None OR cowriter ABSENT) AND HOLD ABSENT`

Instead, set the switches in the GUI and click `Filter`...

![image](https://user-images.githubusercontent.com/24362267/226625853-29d5d6b1-edfe-4c3a-91e4-d1acf42fa470.png)

... the script builds the filter string and types it into the filter  box in Mp3Tag.

![image](https://user-images.githubusercontent.com/24362267/226626980-96204111-f9d7-4793-8c2f-4d9969752954.png)


## Installation

Before you can run the `MP3 Tagger` script, there are some pre-requisites that are assumed.

### Download and install the Mp3Tag Windows Application

https://www.mp3tag.de/en/

### Environment Variables

The following environment variables are mandatory:
`MP3TAG_PATH=`path_to_mp3tag (mine is C:\Program Files (x86)\Mp3tag\Mp3tag.exe)

The recommended way for setting these environmental variables is to use a `.env` file.

A `.env` file is a file in the root directory of this project or at the root of your home directory that lists the environment variables above. For example:


### Create a Virtual Environment (optional)

These steps are not necessary, but recommended for build environment isolation. You could use [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) (and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/index.html)) or just the built-in [venv](https://docs.python.org/3/library/venv.html).

`MP3 Tagger` also supports [poetry](https://python-poetry.org), a modern dependency management and virtual environment tool. You will need to install `poetry` as explained on its site to use it with `MP3 Tagger`.

### Install dependencies

Installing the package resolves and builds the dependencies required to run `MP3 Tagger`. 
The package can be installed in developement (editable) mode to allow you to make changes locally.

Traditional:

```
pip install -e .
```

Poetry automatically installs dependencies in development mode?

## Running

Once you have completed all the installation steps, run `MP3 Tagger` script by running either:

Traditional:

```shell
py -m mp3tagger
```

Poetry:

```shell
poetry run python -m mp3tagger
```
## Customization
You can change the options in `mp3tagger\mp3tagger\data\sections.py` to customize the GUI to your needs. You can add or remove sections, change the labels, and change the tags that are used to filter the files. I suppose we'll have to keep this file out of the repo and add it to the .gitignore file.
