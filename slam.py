import argparse
import pathlib
import sys
import yaml

from dynmen import Menu as dynmenu
from multiprocessing import Pool
from os import cpu_count
from pydub import AudioSegment
from xdg import BaseDirectory


class PySLAM():
    args = [
        {
            "name": "--config",
            "short_name": "-c",
            "help": "Optional path to config file. defaults to ~/.config/slam/config.yaml",
            "default": None,
            "action": "store",
            "required": False,
        },
        {
            "name": "--printdir",
            "short_name": "-D",
            "help": "Print path in which songs are configured to be stored and exit",
            "default": False,
            "action": "store_true",
            "required": False,
        }
    ]
    exec_config = """
    // ** ++++++ **
    // ** PYSLAM **
    // ** ++++++ **
    clear
    bind {0} music_on
    alias music_on "voice_inputfromfile 1;+voicerecord; voice_loopback 1; bind {0} music_off"
    alias music_off "voice_inputfromfile 0;-voicerecord; voice_loopback 0; bind {0} music_on"
    clear
    echo "Commands loaded, just press {0} to start / stop playing your song."
    """

    # Convert audio to a wav file with the necessary settings
    def convert_audio(self, inpath):
        myfile = pathlib.Path(inpath)
        outpath = pathlib.Path(inpath).parent.joinpath(
            "converted/" + myfile.with_suffix(".wav").name
        )

        # Create output directory if it doesn't exist
        outpath.parent.mkdir(parents=True, exist_ok=True)

        # Convert with ffmpeg
        sound = AudioSegment.from_file(inpath, format=myfile.suffix[1:])
        sound.export(
            outpath,
            format="wav",
            parameters=[
                "-ac",      "1",          # Mono
                "-acodec",  "pcm_s16le",  # 16bit little-endian
                "-ar",      "22050",      # 22.05KHz
                "-flags",   "bitexact",
                "-fflags",  "+bitexact",
                "-flags:v", "+bitexact",
                "-flags:a", "+bitexact",
                "-vn"
            ],
        )

        # Delete the source file
        myfile.unlink()


    def get_config_path(self, config_path):
        # If the argument was provided explicitly,
        # override the below logic
        if config_path is not None:
            return config_path

        basedir = pathlib.Path(BaseDirectory.xdg_config_home)
        path_suffix = None

        # Look for file which exists
        # First match wins
        for path in [
            "slam.yaml",
            "slam.yml",
            "slam/slam.yaml",
            "slam/slam.yml",
            "slam/config.yaml",
            "slam/config.yml",
        ]:
            if basedir.joinpath(path).is_file():
                path_suffix = path
                break

        # If it's still None, no config files exist
        if path_suffix is None:
            return None

        return basedir.joinpath(path_suffix)


    def main(self):
        music_dir = None
        csgo_game_dir = None
        csgo_conf_dir = None
        parser = argparse.ArgumentParser()
        for arg in self.args:
            parser.add_argument(
                arg["short_name"],
                arg["name"],
                action=arg["action"],
                help=arg["help"],
                default=arg["default"],
                required=arg["required"],
            )
        args = parser.parse_args()

        # Validate config
        try:
            # Get our path according to path precedence
            config_path = self.get_config_path(args.config)

            config = None
            with open(config_path, "r") as conf:
                config = yaml.load(conf, Loader=yaml.SafeLoader)

            # Bind key used for pyslam.cfg
            # Defaults to mouse3 if unspecified
            bind_key = config.get("bindkey", "mouse3")

            # Default to $XDG_DATA_HOME/slam/music if no value provided
            music_dir = config.get("music", {}).get(
                "path",
                str(
                    pathlib.Path(
                        BaseDirectory.xdg_data_home
                    ).joinpath("slam/music")
                )
            )

            music_dir_path = pathlib.Path(music_dir)
            if not music_dir_path.is_dir():
                try:
                    music_dir_path.mkdir(parents=True)
                except:
                    print(
                        "Music directory '{}' does not exist "
                        "and is unable to be created.".format(music_dir)
                    )
                    sys.exit(1)

            csgo_game_dir = config.get("csgo", {}).get("game")

            normalise_str_to_list = lambda lst: [lst] if isinstance(lst, str) else lst
            csgo_conf_dir = normalise_str_to_list(
                    config.get("csgo", {}).get("user_profile")
            )
            # If no value provided, default to csgo_game_path + 'csgo/cfg'
            if not isinstance(csgo_conf_dir, list):
                csgo_conf_dir = normalise_str_to_list(
                    str(pathlib.Path(csgo_game_dir).joinpath("csgo/cfg"))
                )

            # Check if all the directories exist
            for directory in csgo_conf_dir + [csgo_game_dir]:
                if not pathlib.Path(directory).is_dir():
                    print("Directory '{}' does not exist.".format(directory))
                    sys.exit(2)

        except Exception as e:
            if config_path is None:
                print("No config file could be found. Exiting...")
            else:
                print("Exception {} while processing config file. Exiting...".format(e))
            sys.exit(3)

        if args.printdir is True:
            print(config["music"]["path"])
            sys.exit(0)

        # Find files that need converting
        unconverted_files = []
        for f in pathlib.Path(music_dir).iterdir():
            if f.is_file() and f.suffix in [".mp3", ".wav", ".ogg", ".flac"]:
                unconverted_files += [str(f.resolve())]

        # Convert all files in parallel
        pool = Pool(cpu_count())
        pool.map(self.convert_audio, unconverted_files)

        # Construct list of all converted songs
        songs = {}
        for d in music_dir:
            for f in pathlib.Path(d).joinpath("converted").glob("*.wav"):
                songs[str(f.resolve().stem)] = f.resolve()
        # Exit if no songs found
        if len(songs) == 0:
            print("No songs found. Import some songs with pyslam-ytdl")
            sys.exit(0)

        # Let the user pick the song they want
        # Check for TTY. Use dmenu if no TTY, else fzf
        menu_arr = [
            "fzf", "--prompt=Select song: "
        ] if sys.__stdin__.isatty() else [
            "dmenu", "-p", "Select song: ", "-fn", "sans-serif:pixelsize=17",
            "-nb", "black", "-nf", "white", "-sb", "white", "-sf", "black",
        ]
        menu = dynmenu(menu_arr)
        try:
            selected_song = menu(songs).value
        except:
            print("User aborted. Exiting...")
            exit()

        # Copy song to the right place
        song = pathlib.Path(selected_song)
        target_path = pathlib.Path(csgo_game_dir).joinpath("voice_input.wav")
        target_path.write_bytes(song.read_bytes())

        # Template our exec config, to use bind key configured
        # Falls back to default mouse3 if no key configured
        exec_config = self.exec_config.format(bind_key)

        # Write our config exec
        for d in csgo_conf_dir:
            pathlib.Path(d).joinpath("pyslam.cfg").write_text(exec_config)
