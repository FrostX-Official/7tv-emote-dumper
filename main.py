"""
7TV Emote Dumper by frost | github: frostx-official | discord: fsxg | twitch: frostxoff
Based of this code snippet: https://gist.github.com/FrostX-Official/a268e881f4ecf6cd1f2af5d4031e993d

All animated emotes will be converted to webm ("video" stickers)
All static emotes will be converted to png ("static" stickers)

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

from moviepy.editor import VideoFileClip

from progress.bar import ShadyBar

# settings

import settings

emoteset_id = settings.emoteset_id
folder = settings.folder
remove = settings.remove
rescale_to = settings.rescale_to
output_quality = settings.output_quality
crf_quality = settings.crf_quality
skip_long_emotes = settings.skip_long_emotes
ffmpeg_preset = settings.ffmpeg_preset
moviepy_logger = settings.moviepy_logger
dumping_done_notification = settings.dumping_done_notification

toaster = None

if skip_long_emotes == "ct" or dumping_done_notification:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()

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
    fetchBody = {"operationName":"GetEmoteSet","variables":{"id":id},"query":"query GetEmoteSet($id: ObjectID!) {\n  emoteSet(id: $id) {\n    id\n    name\n    owner {\n    display_name\n    }\n    emotes {\n      id\n      name\n      data {\n      animated\n      }\n}\n}\n}"}

    emotesetJson = requests.post("https://7tv.io/v3/gql",json=fetchBody).json()
    emotesetname = emotesetJson["data"]["emoteSet"]["name"]
    emotesetauthor = emotesetJson["data"]["emoteSet"]["owner"]["display_name"]
    for emote in emotesetJson["data"]["emoteSet"]["emotes"]:
        emotes.append(emote)

    return emotes, emotesetname, emotesetauthor

def convertAnimatedEmote(emote):
    print(Fore.YELLOW+"Converting to WEBM...")

    clip = VideoFileClip(f"{folder}/{emote['name']}.gif")
    if clip.duration > 3:
        if skip_long_emotes.lower() == "y":
            print(Fore.RED+f"WARN ⚠ | \"{emote['name']}\" duration is more than 3 seconds ({clip.duration}s) deleting and skipping...")
            clip.close()
            return "deleted"
        
        elif skip_long_emotes.lower() == "c":
            inp = input(Fore.RED+f"WARN ⚠ | \"{emote['name']}\" duration is more than 3 seconds ({clip.duration}s) want to skip and delete \"{emote['name']}\"? [Y/N] >")
            if inp.lower() == "y" or inp.lower() == "yes":
                print(Fore.RED+f"Skipped and deleted \"{emote['name']}\".")
                clip.close()
                return "deleted"
            
        elif skip_long_emotes.lower() == "ct":
            toaster.show_toast(f"Emote \"{emote['name']}\"",
                    f"\"{emote['name']}\" duration is more than 3 seconds ({clip.duration}s)",
                    duration=3,
                    threaded=True
                )
            
            inp = input(Fore.RED+f"WARN ⚠ | \"{emote['name']}\" duration is more than 3 seconds ({clip.duration}s) want to skip and delete \"{emote['name']}\"? [Y/N] >")
            if inp.lower() == "y" or inp.lower() == "yes":
                print(Fore.RED+f"Skipped and deleted \"{emote['name']}\".")
                clip.close()
                return "deleted"

        print(Fore.RED+f"WARN ⚠ | \"{emote['name']}\" duration is more than 3 seconds ({clip.duration}s) and probably will not pass Telegram video sticker checks.")
    clip.write_videofile(f"{folder}/{emote['name']}.webm", codec="libvpx-vp9", fps=30, audio=False, ffmpeg_params=["-crf",str(crf_quality),"-b:v","0", "-c:v", "libvpx-vp9", "-row-mt", "1", "-pix_fmt", "yuva420p", "-vf", "colorkey=white", "-loop", "1"], preset=ffmpeg_preset, logger=moviepy_logger and "bar" or None)
    clip.close()

def processAnimatedEmote(emote):
    img: Image.Image = Image.open(f"{folder}/{emote['name']}.gif")
    img.info.pop("background", None)
    width, height = img.size
    highest = max(width,height)
    aspect_ratio_thingy = rescale_to/highest
    
    print(Fore.YELLOW+f"\nResizing {width}x{height} -> {int(width*aspect_ratio_thingy)}x{int(height*aspect_ratio_thingy)} ...")

    if aspect_ratio_thingy == 1:
        emoteSizeResult = os.path.getsize(f"{folder}/{emote['name']}.{newformat}")
        downloadTookSpace += emoteSizeResult
        emoteNewPath = f"{os.getcwd()}\{folder}\{emote['name']}.{newformat}"

        emoteTimeResult = time.time()-emoteExecutionTime
        downloadTookTime += emoteTimeResult
        
        print(Fore.GREEN+f"Skipped resizing! (Width or Height is already 512)\nSaving \"{emote['name']}\" took {round(emoteTimeResult, 2)}s -> {emoteNewPath} ({emoteSizeResult/1000}KiB) ({i}/{len(allEmotes)})\n")
        
        return convertAnimatedEmote(emote)

    framestotal = 0
    for frame in ImageSequence.Iterator(img):
        framestotal += 1

    new_frames = []
    framenum = 0

    bar = ShadyBar(Fore.YELLOW+"Resizing...", max=framestotal, suffix="%(index)d/%(max)d frames resized | %(percent).1f%%")
    scaled_up = (int(width*aspect_ratio_thingy), int(height*aspect_ratio_thingy))

    for frame in ImageSequence.Iterator(img):
        framenum += 1
        thumbnail: Image.Image = frame.copy()
        thumbnail = thumbnail.resize(scaled_up, Image.Resampling.NEAREST, reducing_gap=3.0).convert("RGBA")
        thumbnail.info.pop("background", None)
        new_frames.append(thumbnail)
        bar.next()
    bar.finish()

    om: Image.Image = new_frames[0]
    om.info = img.info
    img.close()
    om.save(f"{folder}/{emote['name']}.gif", format="GIF",
            optimize=False,
            save_all=True,
            append_images=new_frames[1:],
            loop=0,
            duration=om.info["duration"],
            quality=output_quality,
            disposal=2
        )
    om.close()

    return convertAnimatedEmote(emote)

allEmotes, emotesetname, emotesetauthor = getEmotesFromEmoteSetId(emoteset_id)

downloadTookSpace = 0
downloadTookTime = 0

print(Fore.MAGENTA+f"=== ALL EMOTES | {emotesetname} by {emotesetauthor} ({len(allEmotes)})")
i = 0
for emote in allEmotes:
    emoteExecutionTime = time.time()
    i+=1
    isAnimated = emote["data"]["animated"]
    newformat = isAnimated and "gif" or "png"
    isAnimatedText = isAnimated and Fore.MAGENTA+"Animated" or Fore.YELLOW+"Static"
    print(Fore.MAGENTA+emote["name"], f"({emote['id']}),", isAnimatedText, f"https://cdn.7tv.app/emote/{emote['id']}/4x.{newformat}")

    try:
        print(Fore.YELLOW+f"Downloading...")# [ https://cdn.7tv.app/emote/{emote['id']}/4x.{newformat} to {folder}/{emote['name']}.{newformat} ]
        wget.download(f"https://cdn.7tv.app/emote/{emote['id']}/4x.{newformat}",f"{folder}/{emote['name']}.{newformat}")
    except Exception as e:
        if "WinError 10060" in str(e):
            print(Fore.RED+f"Failed to download {emote['name']}: {e} | You might have not stable internet connection, or 7TV CDN is down, or you have 7TV blocked by your provider | SKIPPING...\n\n")
            continue
        if "[Errno 22] Invalid argument:" in str(e):
            print(Fore.RED+f"Failed to download {emote['name']}: {e} | This might be because emote contains invalid characters like \"?\" | SKIPPING...\n\n")
            continue

        print(Fore.RED+f"\nFailed to download {emote['name']}: {e}")
        inp = input(Fore.MAGENTA+f"Skip this emote downloading? [Y - yes/N - raise error and crash program] >")
        if inp.lower() == "y" or inp.lower() == "yes":
            continue
        else:
            raise e
    
    try:
        if isAnimated:
            result = processAnimatedEmote(emote)
            if result == "deleted":
                os.remove(f"{folder}/{emote['name']}.gif")
                continue
        else:
            img = Image.open(f"{folder}/{emote['name']}.{newformat}")
            width, height = img.size
            highest = max(width,height)
            aspect_ratio_thingy = rescale_to/highest
            print(Fore.YELLOW+f"\nResizing {width}x{height} -> {int(width*aspect_ratio_thingy)}x{int(height*aspect_ratio_thingy)} ...")
            bar = ShadyBar(Fore.YELLOW+"Resizing...", max=1, suffix="%(index)d/%(max)d frames resized | %(percent).1f%%")
            scaled_up = (int(width*aspect_ratio_thingy), int(height*aspect_ratio_thingy))
            img.resize(scaled_up, Image.Resampling.NEAREST).save(f"{folder}/{emote['name']}.{newformat}")
            bar.next()
            bar.finish()
            img.close()
    except Exception as e:
        if str(e) != "illegal image mode":
            print(Fore.RED+f"\nFailed to resize and save {emote['name']}: {e}")
            raise e
        
    if isAnimated:
        newformat = "webm" # after convertation of animated emote file format changes
        
    emoteSizeResult = os.path.getsize(f"{folder}/{emote['name']}.{newformat}")
    if emoteSizeResult > 512000:
        print(Fore.RED+f"WARN ⚠ | \"{emote['name']}\" size is more than 512 kilobytes and probably will not pass Telegram video sticker checks.")
    emoteTimeResult = time.time()-emoteExecutionTime
    emoteNewPath = f"{os.getcwd()}\{folder}\{emote['name']}.{newformat}"

    downloadTookSpace += emoteSizeResult
    downloadTookTime += emoteTimeResult
            
    print(Fore.GREEN+f"Saving \"{emote['name']}\" took {round(emoteTimeResult, 2)}s -> {emoteNewPath} ({round(emoteSizeResult/1000, 2)}KiB) ({i}/{len(allEmotes)})\n")
    if isAnimated:
        os.remove(f"{folder}/{emote['name']}.gif")

print(Fore.MAGENTA+"===")
print(Fore.GREEN+f"Emotes downloading took {round(downloadTookTime, 2)}s and {round(downloadTookSpace/1000000, 2)}MB")

if dumping_done_notification:
    toaster.show_toast(f"{emotesetname} by {emotesetauthor}",
                    f"Emotes dumping took {round(downloadTookTime, 2)}s and {round(downloadTookSpace/1000000, 2)}MB",
                    duration=10,
                    threaded=True
                )