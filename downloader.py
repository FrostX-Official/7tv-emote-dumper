"""
A downloader module used to download emotes from 7TV.
"""

# TODO:
# Replace wget with custom downloading using requests/httpx

from colorama import Fore
import colorama

colorama.init(autoreset=True)

import multiprocessing
import wget
from progress.bar import ShadyBar

rootLogger = multiprocessing.get_logger()

### SETTINGS

from settings import folder

### MAIN

def downloadEmote(emote, newformat):
    rootLogger.info(f"Downloading {newformat.upper()} ...")
    print(Fore.YELLOW+f"Downloading {newformat.upper()} ...")# [ https://cdn.7tv.app/emote/{emote['id']}/4x.{newformat} to {folder}/{emote['name']}.{newformat} ]
    bar = ShadyBar(Fore.YELLOW+"Downloading...", max=10000, suffix="%(index)d/%(max)d bytes | %(percent).1f%%")
    def wget_download_progressbar(current, total, *args, **kwargs):
        bar.index = current
        bar.max = total
        bar.update()
    wget.download(f"https://cdn.7tv.app/emote/{emote['id']}/4x.{newformat}",f"{folder}/{emote['name']}.{newformat}", wget_download_progressbar)
    bar.finish()