import requests
from lxml import html, etree
import csv
import sys

HEADERS = {'User-Agent': 'request', 'X-Requested-With': 'XMLHttpRequest'}
BASE_PLAYER_URL = 'http://247sports.com'


def get_one_player(url):
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return None
    tree = html.fromstring(res.content)
    info = tree.xpath("//div[@class='player-info clearfix']")[0]
    try:
        name = info.xpath("//h2")[0].text.strip()
    except IndexError:
        name = "NA"
    try:
        location = info.xpath(".//p[@class='location']")[0].text.strip()
    except IndexError:
        location = "NA"
    try:
        city = location.split(",", 1)[0]
    except IndexError:
        city = "NA"
    try:
        state = location.split(",", 1)[1].split()[0]
    except IndexError:
        state = "NA"
    try:
        hs = location.split(",", 1)[1].strip().split(" ", 1)[1].replace("(", "").replace(")", "").strip()
    except IndexError:
        hs = "NA"
    try:
        position = info.xpath(".//p[@class='position']/a")[0].text.strip()
    except IndexError:
        position = "NA"
    except AttributeError:
        position = "NA"

    height = info.xpath(".//ul[@class='playerinfo_lst h_lst']/li")[0].xpath("string()").split()[1].strip()
    weight = info.xpath(".//ul[@class='playerinfo_lst h_lst']/li")[1].xpath("string()").split()[1].strip()

    star_span = tree.xpath("//span[@class='composite-stars']/span")
    stars = 0
    for element in star_span:
        element_class = element.get("class")
        if element_class == "yellow":
            stars += 1
    try:
        rating = tree.xpath("//div[@class='rating']/span")[0].text.strip()
    except IndexError:
        rating = "0"

    return [name, location, city, state, hs, position, height, weight, stars, rating]


def get_players_info_from_urls(urls):
    player_rows = []
    player_num = 1
    for url in urls:
        if player_num % 50 == 0:
            print(".", end="")
            sys.stdout.flush()
        player_row = get_one_player(BASE_PLAYER_URL + url)
        if player_row is not None:
            player_rows.append(player_row)
        player_num += 1
    print("")
    return player_rows


def get_player_profile_urls(year):
    page = 1
    url_list = []
    while True:
        year_url = "http://247sports.com/Season/" + str(year) + "-Football/CompositeRecruitRankings?ViewPath=~%2FViews%2FPlayerSportRanking%2F_SimpleSetForSeason.ascx&InstitutionGroup=HighSchool&Page=" + str(page)
        res = requests.get(year_url, headers=HEADERS)
        print(".", end="")
        sys.stdout.flush()
        if page % 50 == 0:
            print("")
        try:
            tree = html.fromstring(res.content)
        except etree.ParserError:
            break
        players = tree.xpath("//div[@class='playerinfo_blk']/a")
        for player in players:
            url_list.append(player.get("href"))
        page += 1
    print("")
    return url_list


def run_full_year(year):
    print("============================================")
    print("Getting list of players")
    urls = get_player_profile_urls(year)
    with open("output/player_urls_" + str(year) + ".csv", "w") as f:
        writer = csv.writer(f)
        for url in urls:
            writer.writerow([url])
    print("============================================")
    print("Wrote player urls to player_urls_" + str(year) + ".csv")
    print("============================================")

    print("Getting player info")
    print("============================================")

    player_rows = get_players_info_from_urls(urls)

    with open("output/player_info_" + str(year) + ".csv", "w") as output:
        writer = csv.writer(output)
        writer.writerows(player_rows)
    print("============================================")
    print("Wrote player info to player_info_" + str(year) + ".csv")
    print("============================================")


# Interests: //ul[@class='recruit-interest-index_lst']//div[@class='left']
if __name__ == "__main__":
    for year in range(2002, 2018):
        run_full_year(year)
