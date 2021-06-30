import argparse
import pathlib
import sys
import yaml

from dynmen import Menu as dynmenu
from multiprocessing import Pool
from os import cpu_count
from pydub import AudioSegment
from xdg import xdg_config_home


class PySLAM():
    args = [
        {
            "name": "--config",
            "short_name": "-c",
            "help": "Optional path to config file. defaults to ~/.config/slam/config.yaml",
            "default": xdg_config_home().joinpath("slam/config.yaml"),
            "required": False,
        },
    ]
    exec_config = """
    // ** ++++++ **
    // ** PYSLAM **
    // ** ++++++ **
    clear
    bind mouse3 music_on
    alias music_on "voice_inputfromfile 1;+voicerecord; voice_loopback 1; bind mouse3 music_off"
    alias music_off "voice_inputfromfile 0;-voicerecord; voice_loopback 0; bind mouse3 music_on"
    clear
    echo "Commands loaded, just press mouse3 (middle mouse button) to start / stop playing your song."
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


    def main(self):
        music_dir = None
        csgo_game_dir = None
        csgo_conf_dir = None
        parser = argparse.ArgumentParser()
        for arg in self.args:
            parser.add_argument(
                arg["short_name"],
                arg["name"],
                help=arg["help"],
                default=arg["default"],
                required=arg["required"],
            )
        args = parser.parse_args()

        # Validate config
        try:
            config = None
            with open(args.config, "r") as conf:
                config = yaml.load(conf, Loader=yaml.SafeLoader)
            music_dir = (
                config["music"]["paths"]
                if isinstance(config["music"]["paths"], list)
                else [config["music"]["paths"]]
            )
            csgo_conf_dir = (
                config["csgo"]["user_profile"]
                if isinstance(config["csgo"]["user_profile"], list)
                else [config["csgo"]["user_profile"]]
            )
            csgo_game_dir = config["csgo"]["game"]
            for f in music_dir + csgo_conf_dir + [csgo_game_dir]:
                if not pathlib.Path(f).is_dir():
                    print("Directory {} does not exist.")
                    exit(1)
        except:
            print("Error processing config file. Exiting...")
            exit(2)

        # Find files that need converting
        unconverted_files = []
        for d in music_dir:
            for f in pathlib.Path(d).iterdir():
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

        # Write our config exec
        for d in csgo_conf_dir:
            pathlib.Path(d).joinpath("pyslam.cfg").write_text(exec_config)
