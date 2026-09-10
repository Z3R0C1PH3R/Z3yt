# import requests

# r = requests.get("https://api.allanime.day", headers={"referer":"https://allanime.to", "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"})
# print(r.text)
import requests
import re
from urllib.parse import urljoin

def search_anime(query):
    search_gql = """query($search: SearchInput, $limit: Int, $page: Int, $translationType: VaildTranslationTypeEnumType, $countryOrigin: VaildCountryOriginEnumType) {
        shows(search: $search, limit: $limit, page: $page, translationType: $translationType, countryOrigin: $countryOrigin) {
            edges {
                _id name availableEpisodes __typename
            }
        }
    }"""

    allanime_api = "https://api.allanime.day"
    allanime_refr = "https://allanime.to"
    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    mode = "sub"

    variables = {
        "search": {"allowAdult": False, "allowUnknown": False, "query": query},
        "limit": 40,
        "page": 1,
        "translationType": mode,
        "countryOrigin": "ALL"
    }

    headers = {"User-Agent": agent, "Referer": allanime_refr}
    response = requests.get(f"{allanime_api}/api", params={"variables": variables, "query": search_gql}, headers=headers)
    data = response.json()["data"]["shows"]["edges"]

    anime_list = []
    for item in data:
        anime_id = item["_id"]
        anime_name = item["name"]
        available_episodes = item.get("availableEpisodes", 0)  # Use .get() to handle missing key
        anime_list.append((anime_id, anime_name, available_episodes))

    return anime_list

def episodes_list(id):
    episodes_list_gql = """query ($showId: String!) {
        show(_id: $showId) {
            _id availableEpisodesDetail
        }
    }"""

    allanime_api = "https://api.allanime.day"
    allanime_refr = "https://allanime.to"
    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    mode = "sub"

    variables = {"showId": id}
    headers = {"User-Agent": agent, "Referer": allanime_refr}
    response = requests.get(f"{allanime_api}/api", params={"variables": variables, "query": episodes_list_gql}, headers=headers)
    data = response.json()["data"]["show"]["availableEpisodesDetail"][mode]

    ep_list = [str(ep) for ep in data]
    ep_list.sort(key=float)

    return ep_list

# Rest of the code remains the same

def get_episode_url(id, ep_no, mode, allanime_api, allanime_refr, agent):
    # get the embed urls of the selected episode
    episode_embed_gql = """query ($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) {
        episode(
            showId: $showId
            translationType: $translationType
            episodeString: $episodeString
        ) {
            episodeString sourceUrls
        }
    }"""

    variables = {
        "showId": id,
        "translationType": mode,
        "episodeString": ep_no
    }

    headers = {"User-Agent": agent, "Referer": allanime_refr}
    response = requests.get(f"{allanime_api}/api", params={"variables": variables, "query": episode_embed_gql}, headers=headers)
    response_json = response.json()

    resp = [f"{item['sourceName']}: {item['sourceUrl']}" for item in response_json["data"]["episode"]["sourceUrls"]]
    resp = "\n".join(resp)

    providers = "1 2 3 4"
    episode_link = ""

    for provider in providers:
        episode_link = generate_link(resp, provider, allanime_refr, agent)
        if episode_link:
            break

    links = episode_link.split("\n")
    links = [link for link in links if "http" in link]
    links.sort(key=lambda x: int(re.search(r'\d+', x).group()), reverse=True)

    quality = "best"
    episode = select_quality(links, quality)

    return episode

def generate_link(resp, provider, allanime_refr, agent):
    provider_name, provider_id_regex = provider_init(provider)
    provider_id = re.search(provider_id_regex, resp, re.MULTILINE).group().split(":")[1]
    provider_id = decode_provider_id(provider_id)

    if provider_id:
        episode_link = get_links(provider_id, allanime_refr, agent)
        if episode_link and provider_name == "gogoanime":
            episode_link = process_gogoanime_links(episode_link, allanime_refr, agent)

        print(f"\033[1;32m{provider_name}\033[0m Links Fetched", flush=True)
        return episode_link
    return ""

def provider_init(provider):
    if provider == "1":
        return "dropbox", r"/Sak :/p"
    elif provider == "2":
        return "wetransfer", r"/Kir :/p"
    elif provider == "3":
        return "sharepoint", r"/S-mp4 :/p"
    else:
        return "gogoanime", r"/Luf-mp4 :/p"

def decode_provider_id(encoded_id):
    decode_dict = {
        "01": "9", "08": "0", "05": "=", "0a": "2", "0b": "3", "0c": "4", "07": "?",
        "00": "8", "5c": "d", "0f": "7", "5e": "f", "17": "/", "54": "l", "09": "1",
        "48": "p", "4f": "w", "0e": "6", "5b": "c", "5d": "e", "0d": "5", "53": "k",
        "1e": "&", "5a": "b", "59": "a", "4a": "r", "4c": "t", "4e": "v", "57": "o",
        "51": "i"
    }
    decoded_id = "".join(decode_dict.get(encoded_id[i:i+2], encoded_id[i:i+2]) for i in range(0, len(encoded_id), 2))
    if "clock" in decoded_id:
        decoded_id = decoded_id.replace("clock", "clock.json")
    return decoded_id

def get_links(provider_id, allanime_refr, agent):
    headers = {"User-Agent": agent, "Referer": allanime_refr}
    url = f"https://allanime.day{provider_id}"
    response = requests.get(url, headers=headers)
    episode_link = response.text.replace("{},{", "\n").replace('link":"', "").replace('"resolutionStr":"', " >").replace('hls","url":"', "").replace('"hardsub_lang":"en-US"', "")
    return episode_link

def process_gogoanime_links(episode_link, allanime_refr, agent):
    if "vipanicdn" in episode_link or "anifastcdn" in episode_link:
        links = episode_link.split("\n")
        if "original.m3u" in links[0]:
            return episode_link
        else:
            extract_link = links[0].split(" >")[1]
            relative_link = "/".join(extract_link.split("/")[:-1]) + "/"
            headers = {"User-Agent": agent, "Referer": allanime_refr}
            m3u8_response = requests.get(extract_link, headers=headers)
            m3u8_content = m3u8_response.text.replace("#EXT-X-BYTERANGE", "").replace("#EXTINF", "p").replace("\n#", "")
            processed_links = [f"{quality} >{urljoin(relative_link, link)}" for quality, link in (line.split(",") for line in m3u8_content.split("p")[1:])]
            return "\n".join(sorted(processed_links, reverse=True))
    else:
        return episode_link

def select_quality(links, quality):
    if quality == "best":
        return links[0].split(" >")[1]
    elif quality == "worst":
        return [link for link in links if re.search(r'\d+', link)][0].split(" >")[1]
    else:
        for link in links:
            if re.search(rf'^{quality}', link):
                return link.split(" >")[1]
        print("Specified quality not found, defaulting to best", flush=True)
        return links[0].split(" >")[1]
    
import sys

def main():
    # Initialize the required parameters
    allanime_api = "https://api.allanime.day"
    allanime_refr = "https://allanime.to"
    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    mode = "sub"  # Change to "dub" for dubbed version

    # Ask the user for the anime name
    anime_name = input("Enter the anime name: ")

    # Search for the anime and get the ID
    anime_list = search_anime(anime_name)
    if anime_list:
        print("Search results:")
        for i, result in enumerate(anime_list, start=1):
            print(f"{i}. {result[1]} ({result[2]} episodes)")

        choice = int(input("Select the anime by entering the corresponding number: "))
        id = anime_list[choice - 1][0]
    else:
        print("No results found!")
        sys.exit(1)

    # Get the list of available episodes
    ep_list = episodes_list(id)
    print("Available episodes:")
    for ep in ep_list:
        print(ep)

    # Ask the user for the episode number
    ep_no = input("Enter the episode number (or a range, e.g., 1-5): ")

    # Get the episode URL
    episode_url = get_episode_url(id, ep_no, mode, allanime_api, allanime_refr, agent)
    print(f"Episode URL: {episode_url}")

    # You can add code here to play or download the episode using the episode_url

if __name__ == "__main__":
    main()