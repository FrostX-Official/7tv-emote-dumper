<img src="Thumbnail.png" alt="Emote Dumper Thumbnail" width="100%"/>

> [!IMPORTANT]
> Если вы хотите поддержать этот проект просто нажмите на **Star** (на главной странице проекта) и вы добавите проект в избранное.

# 7TV Emote Dumper 🇷🇺
### Сделано для [Pepeland Комьюнити](https://pepeland.net)

7TV Emote Dumper от **фрост ♡**<br>
<img src="https://img.icons8.com/m_sharp/200/FFFFFF/github.png" alt="GitHub Logo" width="22px"/> GitHub: frostx-official<br>
<img src="https://cdn.worldvectorlogo.com/logos/discord-6.svg" alt="Discord Logo" width="22px"/> Discord: fsxg<br>
<img src="https://freelogopng.com/images/all_img/1656152266logo-twitch.png" alt="Discord Logo" width="22px"/> Twitch: frostxoff<br>
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/2048px-Telegram_logo.svg.png" alt="Telegram Logo" width="22px"/> Telegram: @frostxoff<br>

Эта программа сделана для того чтобы скачивать эмоуты с [сервиса 7TV](https://7tv.app/)<br>
Сделано специально для того чтобы делать стикерпаки в [Telegram](https://telegram.org/)

Изменяйте настройки в файле `settings.py`

Построено на этом сниппете кода —<br>
https://gist.github.com/a268e881f4ecf6cd1f2af5d4031e993d

Все анимированные эмоции будут конвертированы в webm ("video" стикеры)<br>
Все статичные эмоции будут конвертированы в png ("static" стикеры)

## Требования
* [Python 3.11+](https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe)
Все модули которые должны быть установлены можно найти в файле `requirements.txt`<br>
Вы можете установить Python на https://python.org
и запустить файл `install-requirements.bat` для того чтобы автоматически установить все модули.
> [!NOTE]
> Модуль `win10toast` нужен только если вы собираетесь использовать настройку `skip_long_emotes` с значением `ct`
## Дампинг занимает много времени?
Вы можете ощущать медленный дампинг эмоут-сетов если дампер находится на медленных дисках, самая долгая часть дампинга это конвертирование анимированных эмоутов в формат **webM**. Чтобы устранить данную проблему просто переместите дампер на более быстрый диск.