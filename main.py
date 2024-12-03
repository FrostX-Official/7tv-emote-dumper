"""
7TV Emote Dumper by frost | github: frostx-official | discord: fsxg | twitch: frostxoff
Based of this code snippet: https://gist.github.com/FrostX-Official/a268e881f4ecf6cd1f2af5d4031e993d

All animated emotes will be converted to webm ("video" stickers)
All static emotes will be converted to png ("static" stickers)

Edit settings in settings.py file.
"""

### MODULES / INITIATION

from colorama import Fore
import colorama

colorama.init(autoreset=True)

import multiprocessing

from PIL import Image, ImageSequence
import requests
import shutil
import time
import wget
import os

from ffmpeg_progress_yield import FfmpegProgress
from progress.bar import ShadyBar

import convertation
import downloader
import resizing

import logging
rootLogger = multiprocessing.get_logger()

### SETTINGS

import settings

emoteset_id = settings.emoteset_id
folder = settings.folder
logs_folder = settings.logs_folder
clear_emotes = settings.clear_emotes
clear_logs = settings.clear_logs
rescale_to = settings.rescale_to
output_quality = settings.output_quality
crf_quality = settings.crf_quality
converting_abort_time = settings.converting_abort_time
skip_long_emotes = settings.skip_long_emotes
ffmpeg_preset = settings.ffmpeg_preset
dumping_done_notification = settings.dumping_done_notification

### TOASTER

toaster = None

if skip_long_emotes == "ct" or dumping_done_notification:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()

### MAIN FUNCTIONS
    
def getEmotesFromEmoteSetId(id):
    """
    Returns an emotes list, emoteset name and emoteset author from emoteset ID
    """

    fetchBody = {"operationName":"GetEmoteSet","variables":{"id":id},"query":"query GetEmoteSet($id: ObjectID!) {\n  emoteSet(id: $id) {\n    id\n    name\n    owner {\n    display_name\n    }\n    emotes {\n      id\n      name\n      data {\n      animated\n      }\n}\n}\n}"}

    emotesetJson = requests.post("https://7tv.io/v3/gql",json=fetchBody).json()
    emotesetname = emotesetJson["data"]["emoteSet"]["name"]
    emotesetauthor = emotesetJson["data"]["emoteSet"]["owner"]["display_name"]

    emotes = []
    for emote in emotesetJson["data"]["emoteSet"]["emotes"]:
        emotes.append(emote)

    return emotes, emotesetname, emotesetauthor

def processDurationWarning(emotename, duration):
    """
    If `emotename` is longer than 3 seconds proceed to show a warning and skip emote depending on `skip_long_emotes` setting.
    """

    if duration > 3 and skip_long_emotes.lower() != "d":
        if skip_long_emotes.lower() == "y":
            rootLogger.warning(f"\"{emotename}\" duration is more than 3 seconds ({duration}s) deleting and skipping...")
            print(Fore.RED+f"WARN ⚠ | \"{emotename}\" duration is more than 3 seconds ({duration}s) deleting and skipping...")
            return "deleted"
        
        elif skip_long_emotes.lower() == "c":
            inp = input(Fore.RED+f"WARN ⚠ | \"{emotename}\" duration is more than 3 seconds ({duration}s) want to skip and delete \"{emotename}\"? [Y/N] > ")
            rootLogger.warning(f"\"{emotename}\" duration is more than 3 seconds ({duration}s) want to skip and delete \"{emotename}\"? [Y/N] > {inp.lower()}")
            if inp.lower() == "y" or inp.lower() == "yes":
                rootLogger.warning(f"Skipped and deleted \"{emotename}\".")
                print(Fore.RED+f"Skipped and deleted \"{emotename}\".")
                return "deleted"
            
        elif skip_long_emotes.lower() == "ct":
            toaster.show_toast(f"Emote \"{emotename}\"",
                    f"\"{emotename}\" duration is more than 3 seconds ({duration}s)",
                    duration=3,
                    threaded=True
                )
            
            inp = input(Fore.RED+f"WARN ⚠ | \"{emotename}\" duration is more than 3 seconds ({duration}s) want to skip and delete \"{emotename}\"? [Y/N] > ")
            rootLogger.warning(f"\"{emotename}\" duration is more than 3 seconds ({duration}s) want to skip and delete \"{emotename}\"? [Y/N] > {inp.lower()}")
            if inp.lower() == "y" or inp.lower() == "yes":
                rootLogger.warning(f"Skipped and deleted \"{emotename}\".")
                print(Fore.RED+f"Skipped and deleted \"{emotename}\".")
                return "deleted"

        rootLogger.warning(f"\"{emotename}\" duration is more than 3 seconds ({duration}s) and may not pass Telegram video sticker checks.")
        print(Fore.RED+f"WARN ⚠ | \"{emotename}\" duration is more than 3 seconds ({duration}s) and may not pass Telegram video sticker checks.")

def processAnimatedEmote(emote):
    """
    Animated emotes processing code.
    Duration Check -> Resizing -> Skip resizing if width or height is already 512 pixels -> Converting
    """

    img: Image.Image = Image.open(f"{folder}/{emote['name']}.gif")
    img.info.pop("background", None)
    width, height = img.size
    highest = max(width,height)
    aspect_ratio_thingy = rescale_to/highest

    # duration check

    total_duration = 0
    for frame in ImageSequence.Iterator(img):
        thumbnail: Image.Image = frame.copy()
        total_duration += thumbnail.info["duration"]
    total_duration /= 1000 # ms to s
    if processDurationWarning(emote["name"], total_duration) == "deleted":
        return "deleted"
    
    # resizing

    resizing.resizeAnimatedEmote(emote, img)

    # converting
    
    convertResult = convertation.convertAnimatedEmote(emote["name"])

    if convertResult != "deleted":
        convertResult = total_duration

    return convertResult


### PROGRAM START
    
if __name__ == '__main__':
    ## Logger initiation

    rootLogger.setLevel(logging.DEBUG)

    logFormatter = logging.Formatter(f"%(asctime)s [%(levelname)-8.8s] %(message)s")
    logFilename = f"logs/{emoteset_id}-{time.time()}".replace(".","-")+".log"
    fileHandler = logging.FileHandler(logFilename)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    rootLogger.critical("7TV Emote Dumper Log")

    ## Clear all emotes from folder
    if clear_emotes:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                rootLogger.error(f"Failed to delete \"{file_path}\". Reason: \"{e}\"")
                print(Fore.RED+f"Failed to delete \"{file_path}\". Reason: \"{e}\"")

    ## Clear all logs from logs folder
    if clear_logs:
        for filename in os.listdir(logs_folder):
            file_path = os.path.join(logs_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                rootLogger.error(f"Failed to delete \"{file_path}\". Reason: \"{e}\"")
                print(Fore.RED+f"Failed to delete \"{file_path}\". Reason: \"{e}\"")

    ## Main

    allEmotes, emotesetname, emotesetauthor = getEmotesFromEmoteSetId(emoteset_id)

    downloadTookSpace = 0
    downloadTookTime = 0

    rootLogger.info(f"=== ALL EMOTES | {emotesetname} by {emotesetauthor} ({len(allEmotes)})")
    print(Fore.MAGENTA+f"=== ALL EMOTES | {emotesetname} by {emotesetauthor} ({len(allEmotes)})")
    i = 0
    for emote in allEmotes:
        emoteExecutionTime = time.time()
        i+=1
        isAnimated = emote["data"]["animated"]
        newformat = isAnimated and "gif" or "png"
        isAnimatedText = isAnimated and Fore.MAGENTA+"Animated" or Fore.YELLOW+"Static"
        isAnimatedTextForLogger = isAnimated and "Animated" or "Static"
        rootLogger.info(emote["name"] +" "+ f"({emote['id']}),"  +" "+ isAnimatedTextForLogger  +" "+ f"https://cdn.7tv.app/emote/{emote['id']}/4x.{newformat}")
        print(Fore.MAGENTA+emote["name"] +" "+ f"({emote['id']}),"  +" "+ isAnimatedText  +" "+ Fore.RESET + f"https://cdn.7tv.app/emote/{emote['id']}/4x.{newformat}")

        try:
            downloader.downloadEmote(emote, newformat)
        except Exception as e:
            if "WinError 10060" in str(e):
                rootLogger.error(Fore.RED+f"Failed to download {emote['name']}: {e} | You might have not stable internet connection, or 7TV CDN is down, or you have 7TV blocked by your provider | SKIPPING...\n\n")
                print(Fore.RED+f"Failed to download {emote['name']}: {e} | You might have not stable internet connection, or 7TV CDN is down, or you have 7TV blocked by your provider | SKIPPING...\n\n")
                continue
            if "[Errno 22] Invalid argument:" in str(e):
                rootLogger.error(Fore.RED+f"Failed to download {emote['name']}: {e} | This might be because emote contains invalid characters like \"?\" | SKIPPING...\n\n")
                print(Fore.RED+f"Failed to download {emote['name']}: {e} | This might be because emote contains invalid characters like \"?\" | SKIPPING...\n\n")
                continue

            rootLogger.error(f"Failed to download {emote['name']}: {e}")
            print(Fore.RED+f"Failed to download {emote['name']}: {e}")
            inp = input(Fore.MAGENTA+f"Skip this emote downloading? [Y - yes/N - raise error and crash program] > ")
            rootLogger.debug(f"Skip this emote downloading? [Y - yes/N - raise error and crash program] > {inp.lower()}")
            if inp.lower() == "y" or inp.lower() == "yes":
                continue
            else:
                raise e
            
        isAnimatedDurationResult = 0
        
        try:
            if isAnimated:
                result = processAnimatedEmote(emote)
                if result == "deleted":
                    os.remove(f"{folder}/{emote['name']}.gif")
                    continue
                else:
                    isAnimatedDurationResult = result
            else:
                img = Image.open(f"{folder}/{emote['name']}.{newformat}")
                width, height = img.size
                highest = max(width,height)
                aspect_ratio_thingy = rescale_to/highest
                rootLogger.info(f"Resizing {width}x{height} -> {int(width*aspect_ratio_thingy)}x{int(height*aspect_ratio_thingy)} ...")
                print(Fore.YELLOW+f"Resizing {width}x{height} -> {int(width*aspect_ratio_thingy)}x{int(height*aspect_ratio_thingy)} ...")
                bar = ShadyBar(Fore.YELLOW+"Resizing...", max=1, suffix="%(index)d/%(max)d frames resized | %(percent).1f%%")
                scaled_up = (int(width*aspect_ratio_thingy), int(height*aspect_ratio_thingy))
                img.resize(scaled_up, Image.Resampling.NEAREST).save(f"{folder}/{emote['name']}.{newformat}")
                bar.next()
                bar.finish()
                img.close()
        except Exception as e:
            if str(e) != "illegal image mode":
                rootLogger.error(Fore.RED+f"\nFailed to resize and save {emote['name']}: {e}")
                print(Fore.RED+f"\nFailed to resize and save {emote['name']}: {e}")
                raise e
            
        if isAnimated:
            newformat = "webm" # after convertation of animated emote file format changes
            
        emoteSizeResult = os.path.getsize(f"{folder}/{emote['name']}.{newformat}")

        if isAnimated:
            if emoteSizeResult > 256000:
                rootLogger.warning(f"\"{emote['name']}\" size is more than 256 kilobytes and may not pass Telegram video sticker checks.")
                print(Fore.RED+f"WARN ⚠ | \"{emote['name']}\" size is more than 256 kilobytes and may not pass Telegram video sticker checks.")
        else:
            if emoteSizeResult > 512000:
                rootLogger.warning(f"\"{emote['name']}\" size is more than 512 kilobytes and may not pass Telegram static sticker checks.")
                print(Fore.RED+f"WARN ⚠ | \"{emote['name']}\" size is more than 512 kilobytes and may not pass Telegram static sticker checks.")
        emoteTimeResult = time.time()-emoteExecutionTime
        emoteNewPath = f"{os.getcwd()}\{folder}\{emote['name']}.{newformat}"

        downloadTookSpace += emoteSizeResult
        downloadTookTime += emoteTimeResult

        emoteDurationResult = isAnimated and f" ({isAnimatedDurationResult}s)" or ""
                
        rootLogger.info(f"Saving \"{emote['name']}\" took {round(emoteTimeResult, 2)}s -> {emoteNewPath} ({round(emoteSizeResult/1000, 2)}KiB){emoteDurationResult} ({i}/{len(allEmotes)})\n")
        print(Fore.GREEN+f"Saving \"{emote['name']}\" took {round(emoteTimeResult, 2)}s -> {emoteNewPath} ({round(emoteSizeResult/1000, 2)}KiB){emoteDurationResult} ({i}/{len(allEmotes)})\n")
        if isAnimated:
            os.remove(f"{folder}/{emote['name']}.gif")

    ## End
   
    rootLogger.info("===")
    rootLogger.info(f"Emotes downloading took {round(downloadTookTime, 2)}s and {round(downloadTookSpace/1000000, 2)}MB")
    print(Fore.MAGENTA+"===")
    print(Fore.GREEN+f"Emotes downloading took {round(downloadTookTime, 2)}s and {round(downloadTookSpace/1000000, 2)}MB")

    if dumping_done_notification:
        rootLogger.info(f"Emotes downloading took {round(downloadTookTime, 2)}s and {round(downloadTookSpace/1000000, 2)}MB")
        toaster.show_toast(f"{emotesetname} by {emotesetauthor}",
                        f"Emotes dumping took {round(downloadTookTime, 2)}s and {round(downloadTookSpace/1000000, 2)}MB",
                        duration=10,
                        threaded=True
                    )