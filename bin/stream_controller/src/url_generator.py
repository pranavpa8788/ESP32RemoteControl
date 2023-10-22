import requests
from typing import List, Union

from bs4 import BeautifulSoup, Tag, NavigableString

def fetch_urls(preset, video_url, media_blacklist) -> List[str]:
    if (preset == "ANIME_PRESET"):
        return fetch_anime_urls(video_url, media_blacklist)

def fetch_anime_urls(video_url, media_blacklist) -> List[str]:
    url_list = []

    req = requests.get(video_url)

    soup = BeautifulSoup(req.content, "html.parser")

    div_1 = soup.find("div", {"class": "anime_muti_link"})

    url_elements = div_1.findChildren("a")

    for url_element in url_elements:
        server_url = url_element.get("data-video")

        if server_url and not any(blacklist_word in server_url for blacklist_word in media_blacklist):
            url_list.append(server_url)

    return url_list

if __name__ == "__main__":
    urls = fetch_urls("ANIME_PRESET", "https://gogoanimehd.io/one-piece-episode-69", ["goone"])
    print(urls)
