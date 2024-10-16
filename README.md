> [!NOTE]
> Доступна версия всего ниже [на русском](README-russian.md)

<img src="Thumbnail.png" alt="Emote Dumper Thumbnail" width="100%"/>

> [!IMPORTANT]
> If you want to support this project just press **Star** and you will favorite this project.

# 7TV Emote Dumper
### Made for [Pepeland Community](https://pepeland.net)

7TV Emote Dumper by **frost ♡**<br>
<img src="https://img.icons8.com/m_sharp/200/FFFFFF/github.png" alt="GitHub Logo" width="22px"/> GitHub: frostx-official<br>
<img src="https://cdn.worldvectorlogo.com/logos/discord-6.svg" alt="Discord Logo" width="22px"/> Discord: fsxg<br>
<img src="https://freelogopng.com/images/all_img/1656152266logo-twitch.png" alt="Twitch Logo" width="22px"/> Twitch: frostxoff<br>
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/2048px-Telegram_logo.svg.png" alt="Telegram Logo" width="22px"/> Telegram: @frostxoff<br>

This program is made to download emotes from [7TV service](https://7tv.app/)<br>
Made specifically to make stickerpacks on [Telegram](https://telegram.org/)

Edit settings in `settings.py` file

Based on this code snippet —<br>
https://gist.github.com/a268e881f4ecf6cd1f2af5d4031e993d

All animated emotes will be converted to webm ("video" stickers)<br>
All static emotes will be converted to png ("static" stickers)

## Requirements
* [Python 3.11+](https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe)
All modules that need to be installed can be located in `requirements.txt` file<br>
You can install python on https://python.org
and run `install-requirements.bat` file to automatically install all modules.
> [!NOTE]
> Module `win10toast` is required only if you want to use setting `skip_long_emotes` with value `ct`
## Long dumping times?
You can experience long emote-sets dumping times if dumper is on slow drives, the slowest part of dumping is converting animated emotes to **webM**. To fix that problem simply move your dumper install path to faster drive.