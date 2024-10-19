# settings

emoteset_id = "61c802080bf6300371940381"
#^ example emote set by PWGood: 61c802080bf6300371940381 (800+ emotes)
#| smaller example by AlexanderLer: 612a670021ca87d781a04e49 (~300 emotes)
#| example by me: 670ff57306e6ff74beaa856a | tests downloading various emotes that can break dumper

folder = "emotes" # folder to dump emotes and clear it if "remove" setting is true
remove = True # remove all emotes from folder before starting

rescale_to = 512 # for telegram stickers you need either width or height to be 512 so this value is recommended, or 100 for stickerpack icon

ffmpeg_preset = "placebo"
#^ presets: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
#| this only changes file size, choose ultrafast if you don't care about size

skip_long_emotes = "d" # skip emotes if they're longer than 3 seconds, d as value is recommended since Telegram may also allow video stickers longer than 3 seconds.
#^ y for auto skip and deletion
#| c for choose with input (Want to skip {emote}? [Y/N])
#| ct for c with win10toast notifications
#| d for force convertation without warning
#| anything else for force convertation with warning

dumping_done_notification = True # create windows 10 notification (win10toast) when dumping process is done

output_quality = 30 # / 100
crf_quality = 40 # / 63 | lower values mean better quality: https://trac.ffmpeg.org/wiki/Encode/VP9#constantq

converting_abort_time = 30 # seconds, recommended value is 20-40 seconds
# sometimes ffmpeg can just be dumb and freeze while converting,
# so if convertation takes too long it will just be terminated and specific emote dumping will be skipped.
# for example, for me 75th emote dumping "this" from pwgood emote-set just completely freezes program forever so it just aborts convertation.

ffmpeg_progress = False
# enabling this setting may cause some issues and freeze program on some emotes, not really recommended (you can try it though.)

pathToFFMPEG = "ffmpeg/bin/ffmpeg.exe"
# if you already have ffmpeg installed on your system,
# please provide path to it and delete it from dumper folder.
# if you have it added to PATH just change this setting to "ffmpeg"