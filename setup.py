from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = "PySLAM",
    packages = [
        "pyslam"
    ],
    platforms = [
        "linux",
    ],
    version = "1.2.0",
    license = "AGPLv3",
    description = "Python implementation of Source Live Audio Mixer",
    long_description = long_description,
    long_description_content_type="text/markdown",
    author = "Alex Wicks",
    author_email = "alex@awicks.io",
    url = "https://gitlab.com/aw1cks/PySLAM",
    download_url = "https://gitlab.com/aw1cks/PySLAM",
    scripts = [
        "bin/pyslam",
        "bin/pyslam-ytdl",
    ],
    keywords = [
        "csgo",
        "slam",
        "sourceliveaudiomixer",
        "ffmpeg",
        "dmenu",
        "fzf",
    ],
    install_requires = [
        "dynmen",
        "pydub",
        "pyxdg",
        "pyyaml",
        "traitlets",
    ],
    python_requires = ">=3.6",
    package_dir={
        "pyslam": "."
    },
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Communications :: Chat",
    ],
)
