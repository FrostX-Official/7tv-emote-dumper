"""
7TV Emote Dumper by frost | github: frostx-official | discord: fsxg | twitch: frostxoff
Based of this code snippet: https://gist.github.com/FrostX-Official/a268e881f4ecf6cd1f2af5d4031e993d

All animated emotes will be converted to webp
All static emotes will be converted to png

Edit settings in settings.py file.
"""

from colorama import Fore
import colorama

colorama.init(autoreset=True)

from PIL import Image, ImageSequence
import requests
import shutil
import time
import wget
import os

from progress.bar import ShadyBar

# settings

import settings

emoteset_id = settings.emoteset_id
folder = settings.folder 
remove = settings.remove
rescale_to = settings.rescale_to
webp_quality = settings.webp_quality

# remove all emotes from folder

if remove:
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(Fore.RED+"Failed to delete %s. Reason: %s" % (file_path, e))

def getEmotesFromEmoteSetId(id):
    emotes = []
    fetchBody = {"operationName":"GetEmoteSet","variables":{"id":id},"query":"query GetEmoteSet($id: ObjectID!) {\n  emoteSet(id: $id) {\n    id\n    name\n    emotes {\n      id\n      name\n      data {\n      animated\n      }\n}\n}\n}"}

    emotesetJson = requests.post("https://7tv.io/v3/gql",json=fetchBody).json()
    for emote in emotesetJson["data"]["emoteSet"]["emotes"]:
        emotes.append(emote)

    return emotes

allEmotes = getEmotesFromEmoteSetId(emoteset_id)

downloadTookSpace = 0
downloadTookTime = 0

print(Fore.MAGENTA+f"=== ALL EMOTES ({len(allEmotes)})")
i = 0
for emote in allEmotes:
    emoteExecutionTime = time.time()
    i+=1
    isAnimated = emote["data"]["animated"]
    newformat = isAnimated and "webp" or "png"
    print(Fore.MAGENTA+emote["name"], f"({emote['id']}),", isAnimated and Fore.MAGENTA+"Animated" or Fore.YELLOW+"Static", f"https://cdn.7tv.app/emote/{emote['id']}/4x.{newformat}")

    try:
        print(Fore.YELLOW+f"Downloading...")
        wget.download(f"https://cdn.7tv.app/emote/{emote['id']}/4x.{newformat}",f"{folder}/{emote['name']}.{newformat}")
    except Exception as e:
        if isinstance(e, OSError):
            print(Fore.RED+f"\nFailed to download {emote['name']}: {e} | This might be because emote contains invalid characters | SKIPPING...\n\n")
            continue

        print(Fore.RED+f"\nFailed to download {emote['name']}: {e}")
        raise e
    
    try:
        if isAnimated:
            img: Image.Image = Image.open(f"{folder}/{emote['name']}.webp")
            img.info.pop('background', None)
            width, height = img.size
            highest = max(width,height)
            buh = rescale_to/highest
            
            print(Fore.YELLOW+f"\nResizing {width}x{height} -> {int(width*buh)}x{int(height*buh)} ...")
            if buh == 1:
                emoteSizeResult = os.path.getsize(f"{folder}/{emote['name']}.{newformat}")
                downloadTookSpace += emoteSizeResult
                emoteNewPath = f"{os.getcwd()}\{folder}\{emote['name']}.{newformat}"

                emoteTimeResult = time.time()-emoteExecutionTime
                downloadTookTime += emoteTimeResult
                
                print(Fore.GREEN+f"Skipped resizing! (Width or Height is already 512) Saving \"{emote['name']}\" took {round(emoteTimeResult, 2)}s -> {emoteNewPath} ({emoteSizeResult/1000}kB) ({i}/{len(allEmotes)})\n")
                continue
            scaled_up = (int(width*buh), int(height*buh))

            frames = []
            for frame in ImageSequence.Iterator(img):
                frames.append(frame)

            new_frames = []

            framenum = 0
            framestotal = len(frames)

            bar = ShadyBar(Fore.YELLOW+"Resizing...", max=framestotal, suffix="%(index)d frames resized | %(percent).1f%%")

            for frame in frames:
                framenum += 1
                thumbnail: Image.Image = frame.copy()
                thumbnail = thumbnail.resize(scaled_up, Image.Resampling.NEAREST)
                thumbnail.info.pop('background', None)
                new_frames.append(thumbnail)
                bar.next()
            bar.finish()

            om = new_frames[0]
            om.info = img.info
            om.save(f"{folder}/{emote['name']}.webp", "webp", save_all=True, append_images=new_frames, loop=0, duration=om.info["duration"], quality=webp_quality)
            img.close()
            #print(f"\n{emote['name']}: resized gif and saved as webp\n")
        else:
            img = Image.open(f"{folder}/{emote['name']}.{newformat}")
            width, height = img.size
            highest = max(width,height)
            buh = rescale_to/highest
            print(Fore.YELLOW+f"\nResizing {width}x{height} -> {int(width*buh)}x{int(height*buh)} ...")
            bar = ShadyBar(Fore.YELLOW+"Resizing...", max=1, suffix="%(index)d frames resized | %(percent).1f%%")
            scaled_up = (int(width*buh), int(height*buh))
            img.resize(scaled_up, Image.Resampling.NEAREST).save(f"{folder}/{emote['name']}.{newformat}")
            bar.next()
            bar.finish()
            img.close()
    except Exception as e:
        if str(e) != "illegal image mode":
            print(Fore.RED+f"\nFailed to resize and save {emote['name']}: {e}")
            raise e
        
    emoteSizeResult = os.path.getsize(f"{folder}/{emote['name']}.{newformat}")
    emoteTimeResult = time.time()-emoteExecutionTime
    emoteNewPath = f"{os.getcwd()}\{folder}\{emote['name']}.{newformat}"

    downloadTookSpace += emoteSizeResult
    downloadTookTime += emoteTimeResult
            
    print(Fore.GREEN+f"Saving \"{emote['name']}\" took {round(emoteTimeResult, 2)}s -> {emoteNewPath} ({emoteSizeResult/1000}kB) ({i}/{len(allEmotes)})\n")

print(Fore.MAGENTA+"===")
print(Fore.GREEN+f"Emotes downloading took {round(downloadTookTime, 2)}s and {downloadTookSpace/1000000}MB")