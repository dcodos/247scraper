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
            profile_url_info = info.xpath("./a")[0].get("href").split("-")
            player_id = profile_url_info[len(profile_url_info) - 1]
            location = info.xpath("./span")[0].text.strip()
            city_state_start = location.rfind("(")
            hs = location[:city_state_start].strip()
            city_state = location[city_state_start + 1:]
            state = "NA"
            city = city_state.split(",")[0].strip()
            if city == "":
                city = "NA"
            if len(city_state.split(",")) > 1:
                state = city_state.split(",")[1].replace(")", "").strip()
            rating_info = player.xpath(".//div[@class='playerinfo_blk skn2']")[0]
            position = rating_info.xpath("./span[@class='position']")[0].text
            if position is None:
                position = ""
            else:
                position = position.strip()
            height = rating_info.xpath("./span[@class='height']")[0].text.strip()
            weight = rating_info.xpath("./span[@class='weight']")[0].text.strip()
            rating = rating_info.xpath("./span[@class='rating']")[0].xpath("text()")[1].strip()
            star_span = rating_info.xpath("./span[@class='rating']/span")
            stars = 0
            for element in star_span:
                element_class = element.get("class")
                if element_class == "yellow":
                    stars += 1
            player_row = [player_id, name, city, state, hs, position, height, weight, stars, rating]
            player_list.append(player_row)
    return player_list


def get_interest_urls(trees):
    url_list = []
    for tree in trees:
        players = tree.xpath("//li[@class='team_itm']")
        for player in players:
            if len(player.xpath("./a[@class='toggle_anc2']")) < 1:
                continue
            link = player.xpath("./a[@class='toggle_anc2']")[0].get("href")
            link = link.replace("?view=Complex", "")
            link = link.replace("\"", "")
            link = link.replace("(", "")
            link = link.replace(")", "")
            link = link.replace(",", "")
            link = link.replace("\t", "")
            if "43059" in link:
                link = "/Recruitment/Pookela-Ahmad-43059"
            if "19060" in link:
                link = "/Recruitment/Toms-Rivera-19060"
            link += "/RecruitInterests"
            url_list.append(link)
    return url_list


def get_timeline_urls(trees):
    url_list = []
    for tree in trees:
        players = tree.xpath("//li[@class='player_itm']")
        for player in players:
            info = player.xpath(".//div[@class='playerinfo_blk']")[0]
            profile_url_info = info.xpath("./a")[0].get("href").split("-")
            player_id = profile_url_info[len(profile_url_info) - 1]
            link = "/Player/" + str(player_id) + "/TimelineEvents"
            url_list.append(link)
    return url_list

def get_player_timelines(url):
    timelines = []
    res = requests.get(url, headers=HEADERS)
    time.sleep(0.7)
    try:
        tree = html.fromstring(res.content)
    except etree.ParseError:
        return None

    page_list = tree.xpath("//ul[@class='pagn']/li[not(@class)]")
    num_pages = 1
    if len(page_list) > 0:
        num_pages = len(page_list)

    cur_page = 1

    profile_url_info = tree.xpath("//a[@class='name']")[0].get("href").split("-")
    player_id = profile_url_info[len(profile_url_info) - 1]

    current_entry = 1
    while cur_page <= num_pages:
        timeline_list = tree.xpath("//ul[@class='timeline-event-index_lst']/li[not(@class)]")
        for timeline_item in timeline_list:
            headline = timeline_item.xpath(".//b")[0].text.strip()
            info = timeline_item.xpath(".//p")[1].text.strip()
            headline_items = headline.split(":")
            date = headline_items[0]
            event_type = headline_items[1].strip()
            school = extract_school(event_type, info)
            timeline_row = [player_id, current_entry, date, event_type, school, info]
            timelines.append(timeline_row)
            current_entry += 1
        cur_page += 1
        if cur_page <= num_pages:
            next_page_url = url + "?page=" + str(cur_page)
            res = requests.get(next_page_url, headers=HEADERS)
            time.sleep(0.7)
            try:
                tree = html.fromstring(res.content)
            except etree.ParseError:
                return None
    return timelines


def extract_school(event_type, info):
    school = ""
    if event_type == "Enrollment":
        school = info.split("enrolls at")[1].strip()
    elif event_type == "Signing":
        school = info.split("intent to")[1].strip()
    elif event_type == "Commitment":
        school = info.split("commits to")[1].strip()
    elif event_type == "Offer":
        school = info.split("offer")[0].strip()
    elif event_type == "Unofficial Visit":
        school = info.split("visits")[1].strip()
    elif event_type == "School Camp":
        school = info.replace("camp", "").split("attends")[1].strip()
    elif event_type == "Official Visit":
        school = info.split("visits")[1].strip()
    elif event_type == "Junior Day":
        school = info.split("at")[1].strip()
    elif event_type == "Coach Visit":
        school = info.split("from")[1].split("visits")[0].strip()
    return school

def get_player_interests(url):
    interests = []
    res = requests.get(url, headers=HEADERS)
    time.sleep(0.7)
    try:
        tree = html.fromstring(res.content)
    except etree.ParserError:
        return None

    interest_list = tree.xpath("//ul[@class='recruit-interest-index_lst']/li[not(@class)]")
    profile_url_info = tree.xpath("//a[@class='name']")[0].get("href").split("-")
    player_id = profile_url_info[len(profile_url_info) - 1]

    for interest in interest_list:
        try:
            first_blk = interest.xpath(".//div[@class='first_blk']")[0]
        except IndexError:
            print(player_id + " " + str(len(interest_list)) + " " + url)
            #print(etree.tostring(interest))
            continue
        school = first_blk.xpath("./a")[0].text.strip()
        status_block = first_blk.xpath("./span[@class='status']")[0]
        status_string = status_block.xpath("./span")[0].text.strip()
        date = ""
        if "Status" in status_string:
            status_string = status_string.replace("Status:", "").strip()
            date = status_block.xpath("./a")[0].text.replace("(", "").replace(")", "").strip()

        offer = interest.xpath(".//div[@class='secondary_blk']/span[@class='offer']")[0].xpath("text()")[1].strip()
        visit = interest.xpath(".//div[@class='secondary_blk']/span[@class='visit']/a")
        visit_text = "none"
        if len(visit) > 0:
            visit_text = visit[0].xpath("text()")[0].strip()

        interest_row = [player_id, school, visit_text, offer, status_string, date]
        interests.append(interest_row)
    return interests


def run_full_year(year):
    print("Getting list of players from year: " + str(year))
    page_trees = get_year_pages(year)
    print("Parsing info from list of players")
    players = get_player_info(page_trees)

    # with open("output/player_info_" + str(year) + ".csv", "w") as output:
    #     writer = csv.writer(output)
    #     writer.writerows(players)
    # print("Wrote player info to output/player_info_" + str(year) + ".csv")
    #
    # interest_output = open("output/player_interests_" + str(year) + ".csv", "w")
    # interest_writer = csv.writer(interest_output)
    # print("Getting player interests")
    # interest_urls = get_interest_urls(page_trees)
    # for num, interest_url in enumerate(interest_urls):
    #     if num % 50 == 0:
    #         print(".", end="")
    #         sys.stdout.flush()
    #     interest_rows = get_player_interests(BASE_PLAYER_URL + interest_url)
    #     interest_writer.writerows(interest_rows)
    # print("")
    # print("Wrote player interests to output/player_interests_" + str(year) + ".csv")
    # print("============================================")

    timeline_output = open("output/player_timeline_" + str(year) + ".csv", "w")
    timeline_writer = csv.writer(timeline_output)
    print("Getting player timelines")
    timeline_urls = get_timeline_urls(page_trees)
    for num, timeline_url in enumerate(timeline_urls):
        if num % 50 == 0:
            print(".", end="")
            sys.stdout.flush()
        timeline_rows = get_player_timelines(BASE_PLAYER_URL + timeline_url)
        timeline_writer.writerows(timeline_rows)
    print("")
    print("Wrote player interests to output/player_timeline_" + str(year) + ".csv")
    print("============================================")


if __name__ == "__main__":
    # result = get_player_timelines("http://247sports.com/Player/34818/TimelineEvents")
    # result = get_player_timelines("http://247sports.com/Player/Keyvone-Bruton-34787/TimelineEvents")
    # print(result)
    # result = get_player_interests("http://247sports.com/Recruitment/Fotu-Leiato-80507/RecruitInterests")
    # print(result)
    print_header()
    print("============================================")
    for cur_year in range(2014, 2018):
        run_full_year(cur_year)
