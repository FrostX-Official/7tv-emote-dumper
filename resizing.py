"""
A resizing module used to resize images to specific sizes, respecting aspect ratio.
"""

from colorama import Fore
import colorama

colorama.init(autoreset=True)

import multiprocessing

from PIL import Image, ImageSequence
import io
# import time
# import os

from progress.bar import ShadyBar

rootLogger = multiprocessing.get_logger()

### SETTINGS

import settings

folder = settings.folder
rescale_to = settings.rescale_to
output_quality = settings.output_quality

### MAIN

def multiprocess_resize(queue: multiprocessing.Queue, img, frames, width, height, aspect_ratio_thingy):
    """
    Resizing in another process since progressbar breaks otherwise (idk why tbhhhh)
    """

    bar = ShadyBar(Fore.YELLOW+"Resizing...", max=len(frames), suffix="%(index)d/%(max)d frames resized | %(percent).1f%%")
    scaled_up = (int(width*aspect_ratio_thingy), int(height*aspect_ratio_thingy))

    new_frames = []
    framenum = 0

    for frame in frames:
        thumbnail: Image.Image = frame.copy()
        framenum += 1
        thumbnail = thumbnail.resize(scaled_up, Image.Resampling.NEAREST, reducing_gap=3.0).convert("RGBA")
        thumbnail.info.pop("background", None)
        new_frames.append(thumbnail)
        bar.index += 1
        bar.update()
    bar.finish()

    queue.put(new_frames)
    return new_frames

def resizeAnimatedEmote(emote: dict, img: Image.Image) -> bool:
    """Resizes animated emote and saves it as a GIF.

    Args:
        emote (dict): An emote that is passed in `processAnimatedEmote` function.
        img (Image.Image): PIL Image which is generated by opening 7TV gif with `Image.open`

    Returns:
        bool: Returns `True` if resizing was skipped
    """

    width, height = img.size
    highest = max(width,height)
    aspect_ratio_thingy = rescale_to/highest

    rootLogger.info(f"Resizing {width}x{height} -> {int(width*aspect_ratio_thingy)}x{int(height*aspect_ratio_thingy)} ...")
    print(Fore.YELLOW+f"Resizing {width}x{height} -> {int(width*aspect_ratio_thingy)}x{int(height*aspect_ratio_thingy)} ...")

    if aspect_ratio_thingy == 1:
        # emoteSizeResult = os.path.getsize(f"{folder}/{emote['name']}.gif")
        # downloadTookSpace += emoteSizeResult
        # emoteNewPath = f"{os.getcwd()}\{folder}\{emote['name']}.gif"

        # emoteTimeResult = time.time()-emoteExecutionTime
        # downloadTookTime += emoteTimeResult
        
        rootLogger.info(f"Skipped resizing! (Width or Height is already 512)")#\nSaving \"{emote['name']}\" took {round(emoteTimeResult, 2)}s -> {emoteNewPath} ({emoteSizeResult/1000}KiB) ({i}/{allEmotesLen})\n
        print(Fore.GREEN+f"Skipped resizing! (Width or Height is already 512)")#\nSaving \"{emote['name']}\" took {round(emoteTimeResult, 2)}s -> {emoteNewPath} ({emoteSizeResult/1000}KiB) ({i}/{allEmotesLen})\n
        
        return True
    
    frames = []
    for frame in ImageSequence.Iterator(img):
        frames.append(frame)

    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=multiprocess_resize, name=f"RESIZING|{emote['name']}", args=(queue, img, frames, width, height, aspect_ratio_thingy))
    process.start()
    process.join()
    new_frames = queue.get()

    om: Image.Image = new_frames[0]
    om.info = img.info
    om.save(f"{folder}/{emote['name']}.gif", format="GIF",
            optimize=False,
            save_all=True,
            append_images=new_frames[1:],
            loop=0,
            duration=om.info["duration"],
            quality=output_quality,
            disposal=2
        )
    img.close()
    om.close()

    return False