# Puddler (Emby/Jellyfin-MPV-CLI)
Emby/Jellyfin command line client, powered by mpv.

### Currently, in extreme buggy alpha state.
___

### Installation:
```
$ python -m pip install Puddler --upgrade
$ python -m puddler
```

**Latest update:**

+ "full" windows support (no more exception spamming and script-freezing)

+ ~~while testing on *panels of glass* I also realised `getch` (the linux one), will flat-out fail to install -> fixed~~

Seem's like I still don't know nothing, how pip works. Windows will only be able to install the newest version (without any problems) by running the following command:
```commandline
python -m pip install Puddler --upgrade --no-binary :all:
```
since the pre-built stuff completely ignores the platform functions I've added to the setup.py
___

### Information:

Currently, not a lot of features.

But at least both emby and jellyfin are supported.

Playback using search-term and some ridiculous playlist mode.

___

Instead of a list with features, here is a to-do list:

- flawless playback of multiple episodes
- actual good playback report

___