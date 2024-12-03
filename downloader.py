"""
A downloader module used to download emotes from 7TV.
"""

# TODO:
# Replace wget with custom downloading using requests/httpx

from colorama import Fore
import colorama
import httpx

colorama.init(autoreset=True)

import multiprocessing

from progress.bar import ShadyBar

rootLogger = multiprocessing.get_logger()

### SETTINGS

import settings

folder = settings.folder
proxy = settings.proxy
proxy_enabled = settings.proxy_enabled
autofetch_proxy = settings.autofetch_proxy
autofetch_country = settings.autofetch_country

### MAIN

#httpxClient = httpx.Client(follow_redirects=True)

if multiprocessing.current_process().name=="MainProcess": ## Downloader Config
    if proxy_enabled and autofetch_proxy:
        proxies_list = None
        try:
            proxies_list = httpx.get(
                url=f"https://proxylist.geonode.com/api/proxy-list?country={autofetch_country.upper()}&anonymityLevel=elite&protocols=http&limit=500&page=1&sort_by=speed&sort_type=asc",
                timeout=99999
            ).json()["data"]

            if len(proxies_list) > 0:
                best_proxy = proxies_list[0]
                proxy = f"http://{best_proxy['ip']}:{best_proxy['port']}" #"http://165.22.77.86:80"
                rootLogger.info(f"Chosen proxy with latency {best_proxy['latency']}ms -> {proxy}")
                print(Fore.MAGENTA+f"Chosen proxy with latency {best_proxy['latency']}ms -> {proxy}")
                print(httpx.get("https://api64.ipify.org?format=json", proxy=proxy, timeout=999999, follow_redirects=True).json())
            else:
                rootLogger.warn("Failed to fetch proxy list, disabling proxy, disabling proxy.")
                print(Fore.RED+f"Not found any proxy available with autofetch, disabling proxy.")
                proxy = None
        except Exception as e:
            rootLogger.error("Failed to fetch proxy list, disabling proxy.")
            #print(Fore.RED+"Failed to fetch proxy list, disabling proxy.")
            proxy = None
            raise e
        
    if proxy_enabled and not autofetch_proxy:
        rootLogger.info(f"Using proxy: {proxy}")
        print(Fore.MAGENTA+f"Using proxy: {proxy}")
        print(httpx.get("https://api64.ipify.org?format=json", proxy=proxy, timeout=999999, follow_redirects=True).json())

    if not proxy_enabled:
        proxy = None

def downloadEmote(emote, newformat):
    rootLogger.info(f"Downloading {newformat.upper()} ...")
    print(Fore.YELLOW+f"Downloading {newformat.upper()} ...")# [ https://cdn.7tv.app/emote/{emote['id']}/4x.{newformat} to {folder}/{emote['name']}.{newformat} ]
    bar = ShadyBar(Fore.YELLOW+"Downloading...", max=1, suffix="%(index)d/%(max)d bytes | %(percent).1f%%")

    download_response = httpx.get(
        url=f"https://cdn.7tv.app/emote/{emote['id']}/4x.{newformat}",
        timeout=99999,
        proxy=proxy,
        follow_redirects=True
    )

    file = open(f"{folder}/{emote['name']}.{newformat}", "wb")
    file.write(download_response.content)
    bar.index = 1
    bar.max = 1
    bar.update()

    bar.finish()