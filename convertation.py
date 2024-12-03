"""
A convertation module used to convert animated emotes from GIF to WEBM using FFMPEG.
"""

from colorama import Fore
import colorama

colorama.init(autoreset=True)

import multiprocessing

from ffmpeg_progress_yield import FfmpegProgress
from progress.bar import ShadyBar

rootLogger = multiprocessing.get_logger()

### SETTINGS

import settings

folder = settings.folder
converting_abort_time = settings.converting_abort_time

### MAIN

def multiprocess_ffmpeg(emotepath, bar):
    """
    FFMPEG can freeze which is unrelated to this program,
    therefore we use ffmpeg convertation in separate multiprocessing Process,
    and if it freezes we just abort convertation after `settings.converting_abort_time`.

    See `settings.converting_abort_time` description for more information.
    """

    command = [settings.pathToFFMPEG, "-i", f"{emotepath}.gif", "-crf", str(settings.crf_quality), "-framerate", "30", "-b:v", "0", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-row-mt", "1", "-loop", "1", "-f", "webm", f"{emotepath}.webm"]
    # ff = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)
    # for line in ff.stdout:
    #     print(line)
    ff = FfmpegProgress(command)
    for progress in ff.run_command_with_progress():
        bar.index = progress
        bar.update()
    bar.finish()

def convertAnimatedEmote(emotename: str) -> None:
    """Convert an animated emote from GIF to WEBM.
    Animated emote must already exist in `settings.folder`\`emotename`.gif path.

    Converting is divided into 2 functions, one of them is in another process to prevent program freezing on specific emote
    See `settings.converting_abort_time` description for more information.

    Args:
        emotename (str): An emote name that must be found in `settings.folder`\`emotename`.gif path.
    """

    rootLogger.info("Converting to WEBM...")
    print(Fore.YELLOW+"Converting to WEBM...")
    bar = ShadyBar(Fore.YELLOW+"Converting...", max=100, suffix="%(percent).1f%%")

    process = multiprocessing.Process(target=multiprocess_ffmpeg, name=f"FFMPEG|{emotename}", args=(f"{folder}\{emotename}", bar))
    process.start()

    process.join(converting_abort_time)

    if process.is_alive():
        process.terminate()
        process.join()
        bar.finish()
        rootLogger.warning(f"Converting took too long. Terminated convertation process. Aborting \"{emotename}\" dumping.\n")
        print(Fore.RED+f"WARN ⚠ | Converting took too long. Terminated convertation process. Aborting \"{emotename}\" dumping.\n")
        return "deleted"
    
    return None