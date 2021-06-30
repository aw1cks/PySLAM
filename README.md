# PySLAM

- [Configuration](#configuration)
  * [Configuration location](#configuration-location)
  * [Example configuration](#example-configuration)
- [Command-line parameters](#command-line-parameters)

CSGO implemenation of SLAM, written in python.

The binaries `pyslam` and `pyslam-ytdl` are provided.

`pyslam-ytdl` will download songs into mp3 format from YouTube to the configured music directory.

## Configuration

### Configuration location

The configuration file location respects XDG, and will try the following paths, in this order:
 - `$XDG_CONFIG_HOME/slam.yaml`
 - `$XDG_CONFIG_HOME/slam.yml`
 - `$XDG_CONFIG_HOME/slam/slam.yaml`
 - `$XDG_CONFIG_HOME/slam/slam.yml`
 - `$XDG_CONFIG_HOME/slam/config.yaml`
 - `$XDG_CONFIG_HOME/slam/config.yml`

 **NOTE**:
  - `$XDG_CONFIG_HOME` will default to `$HOME/.config` on most systems.
  - PySLAM uses a lazy match. This means the first file from the above list which exists will be used.

### Example configuration

```yaml
---

# Key which will be bound to play music
# If not specified, will default to mouse3
bindkey: KP_END

# Path in which music will be stored
# If not specified, will default to $XDG_DATA_HOME/slam/music
# NOTE: In older versions, a key named 'paths' which accepted a list was used
# This is now deprecated.
music:
  path: /home/alex/Documents/slam

csgo:

  # Path to game folder
  # This value is mandatory
  game: /opt/games/steamapps/common/Counter-Strike Global Offensive

  # List of paths to which the pyslam.cfg file will be written
  # If unspecified, will write to csgo/cfg folder under the game folder specified above
  # i.e. in this config: /opt/games/steamapps/common/Counter-Strike Global Offensive/csgo/cfg
  user_profile:
    - /opt/games/steamapps/common/Counter-Strike Global Offensive/csgo/cfg
```

## Command-line parameters

The following parameters are present:

| Argument     | Short argument | Explanation                         | Default | Example                      |
|--------------|----------------|-------------------------------------|---------|------------------------------|
| `--config`   | `-c`           | Override config path                | `None`  | `PySLAM -c /etc/pyslam.yaml` |
| `--printdir` | `-D`           | Print music directory as configured | `False` | `PySLAM -D`                  |
