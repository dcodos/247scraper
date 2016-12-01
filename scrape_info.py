import requests
from lxml import html, etree
import csv
import sys
import time

HEADERS = {'User-Agent': 'request', 'X-Requested-With': 'XMLHttpRequest'}
BASE_PLAYER_URL = 'http://247sports.com'


def print_header():
    head = """ _____   ___  ______  _____
/ __  \ /   ||___  / /  ___|
`' / /'/ /| |   / /  \ `--.  ___ _ __ __ _ _ __   ___ _ __
  / / / /_| |  / /    `--. \/ __| '__/ _` | '_ \ / _ \ '__|
./ /__\___  |./ /    /\__/ / (__| | | (_| | |_) |  __/ |
\_____/   |_/\_/     \____/ \___|_|  \__,_| .__/ \___|_|
                                          | |
                                          |_|              """
    print(head)

def get_year_pages(year):
    pages = []
    page = 1
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
        pages.append(tree)
        page += 1
    print("")
    return pages


def get_player_info(trees):
    player_list = []
    for tree in trees:
        players = tree.xpath("//li[@class='player_itm']")
        for player in players:
            info = player.xpath(".//div[@class='playerinfo_blk']")[0]
            name = info.xpath("./a")[0].text.strip()
            location = info.xpath("./span")[0].text.strip().replace("(HS)", "")
            hs = location.split("(")[0].strip()
            city = location.split("(")[1].split(",")[0].strip()
            state = location.split("(")[1].split(",")[1].replace(")", "").strip()
            rating_info = player.xpath(".//div[@class='playerinfo_blk skn2']")[0]
            position = rating_info.xpath("./span[@class='position']")[0].text.strip()
            height = rating_info.xpath("./span[@class='height']")[0].text.strip()
            weight = rating_info.xpath("./span[@class='weight']")[0].text.strip()
            rating = rating_info.xpath("./span[@class='rating']")[0].xpath("text()")[1].strip()
            star_span = rating_info.xpath("./span[@class='rating']/span")
            stars = 0
            for element in star_span:
                element_class = element.get("class")
                if element_class == "yellow":
                    stars += 1
            player_row = [name, city, state, hs, position, height, weight, stars, rating]
            player_list.append(player_row)
    return player_list


def get_interest_urls(trees):
    url_list = []
    for tree in trees:
        players = tree.xpath("//li[@class='team_itm']")
        for player in players:
            link = player.xpath("./a[@class='toggle_anc2']")[0].get("href")
            link = link.replace("?view=Complex", "")
            link += "/RecruitInterests"
            url_list.append(link)
    return url_list


def get_player_interests(url):
    interests = []
    res = requests.get(url, headers=HEADERS)
    time.sleep(0.5)
    try:
        tree = html.fromstring(res.content)
    except etree.ParserError:
        return None

    interest_list = tree.xpath("//ul[@class='recruit-interest-index_lst']/li[not(@class)]")
    name = tree.xpath("//a[@class='name']")[0].text.strip()

    for interest in interest_list:
        try:
            first_blk = interest.xpath(".//div[@class='first_blk']")[0]
        except IndexError:
            print(name + " " + str(len(interest_list)) + " " + url)
            print(etree.tostring(interest))
            continue
        school = first_blk.xpath("./a")[0].text.strip()
        status_block = first_blk.xpath("./span[@class='status']")[0]
        status_string = status_block.xpath("./span")[0].text.strip()
        date = ""
        if status_string != "None":
            status_string = status_string.replace("Status:", "").strip()
            date = status_block.xpath("./a")[0].text.replace("(", "").replace(")", "").strip()

        offer = interest.xpath(".//div[@class='secondary_blk']/span[@class='offer']")[0].xpath("text()")[1].strip()

        interest_row = [name, school, offer, status_string, date]
        interests.append(interest_row)
    return interests


def run_full_year(year):
    print("Getting list of players from year: " + str(year))
    page_trees = get_year_pages(year)
    print("Parsing info from list of players")
    players = get_player_info(page_trees)

    with open("output/player_info_" + str(year) + ".csv", "w") as output:
        writer = csv.writer(output)
        writer.writerows(players)
    print("Wrote player info to output/player_info_" + str(year) + ".csv")

    interest_output = open("output/player_interests_" + str(year) + ".csv", "w")
    interest_writer = csv.writer(interest_output)
    print("Getting player interests")
    interest_urls = get_interest_urls(page_trees)
    for num, interest_url in enumerate(interest_urls):
        if num % 50 == 0:
            print(".", end="")
            sys.stdout.flush()
        interest_rows = get_player_interests(BASE_PLAYER_URL + interest_url)
        interest_writer.writerows(interest_rows)
    print("")
    print("Wrote player interests to output/player_interests_" + str(year) + ".csv")
    print("============================================")


if __name__ == "__main__":
    # get_player_interests("http://247sports.com/Recruitment/Doug-Datish-28242/RecruitInterests")
    print_header()
    print("============================================")
    for cur_year in range(2002, 2018):
        run_full_year(cur_year)
