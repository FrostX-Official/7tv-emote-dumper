# settings

emoteset_id = "61c802080bf6300371940381"
# example emote set by PWGood: 61c802080bf6300371940381 (800+ emotes)
# smaller example by AlexanderLer: 612a670021ca87d781a04e49 (~300 emotes)
# example by me: 670ff57306e6ff74beaa856a | tests downloading emotes with illegal characters
folder = "emotes" # folder to dump emotes and clear it if "remove" setting is true
remove = True # remove all emotes from folder before starting
rescale_to = 512 # for telegram stickers you need either width or height to be 512 so this value is recommended, or 100 for stickerpack icon

skip_long_emotes = "anything else" # skip emotes if they're longer than 3 seconds
#^ y for auto skip and deletion
#| c for choose with input (Want to skip {emote}? [Y/N])
#| ct for c with win10toast notifications
#| anything else for force convertation

output_quality = 30 # / 100
crf_quality = 40 # / 63 | lower values mean better quality: https://trac.ffmpeg.org/wiki/Encode/VP9#constantq