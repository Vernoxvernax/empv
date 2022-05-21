import requests
import re
from .mediaserver_information import check_information

# Some mildly important variables #
global version
version = "0.2.dev5"
appname = "Puddler"
#


def green_print(text):
    print("\033[92m{}\033[00m".format(text))


def blue_print(text):
    print("\033[96m{}\033[00m".format(text))


def red_print(text):
    print("\033[91m{}\033[00m".format(text))


def choosing_media(head_dict):
    def json_alone(items):
        count = 0
        for x in items:
            count = count + 1
        if count != 1:
            return False
        else:
            return True

    def print_json(items, count):
        item_list = []
        for x in items["Items"]:
            if x["Name"] not in item_list:
                item_list.append(x)
                if x["UserData"]["Played"] == 0:
                    if not count:
                        print(
                            "      [{}] {} - ({})".format(item_list.index(x), x.get("Name"), x.get("Type")))
                    else:
                        blue_print("      [{}] {} - ({})".format("Enter", x.get("Name"), x.get("Type")))
                        input()
                else:
                    if not count:
                        print(
                            "      [{}] {} - ({})".format(item_list.index(x), x.get("Name"), x.get("Type")), end="")
                    else:
                        blue_print("      [{}] {} - ({})".format("Enter", x.get("Name"), x.get("Type")))
                        input()
                    green_print(" [PLAYED]")
        return item_list

    def process_input(already_asked, item_list):
        if len(item_list) > 1:
            if not already_asked:
                raw_pick = input(": ")
            else:
                raw_pick = search
            pick = int(re.sub("[^0-9]", "", raw_pick))
            if pick < (len(item_list) + 1) and not pick < 0:
                print("\nYou've chosen ", end='')
                blue_print(item_list[pick].get("Name"))
            else:
                print("Are you stupid?!")
                exit()
            return pick
        elif len(item_list) == 1:
            pick = 0
            return pick
        else:
            print("Nothing found.\n")
            item_list = choosing_media(head_dict)
            streaming(head_dict, item_list)

    ipaddress = head_dict.get("config_file").get("ipaddress")
    media_server = head_dict.get("media_server")
    user_id = head_dict.get("user_id")
    request_header = head_dict.get("request_header")
    items = requests.get("{}{}/Users/{}/Items/Latest"
                         .format(ipaddress, media_server, user_id), headers=request_header)
    items = {
        "Items": items.json()
    }
    item_list = print_json(items, False)
    search = input("Please choose from above, enter a search term like \"Everything Everywhere\" or type \"ALL\" to "
                   "display literally everything.\n: ")
    if search != "ALL" and not re.search("^[0-9]+$", search):
        items = requests.get("{}{}/Items?SearchTerm={}&UserId={}&Recursive=true&IncludeItemTypes=Series,Movie"
                             .format(ipaddress, media_server, search, user_id), headers=request_header)
        if json_alone(items.json()["Items"]):
            print("\nOnly one item has been found.\nDo you want to select this title?")
            item_list = print_json(items.json(), True)
        else:
            print("Please choose from the following results: ")
            item_list = print_json(items.json(), False)
        pick = process_input(False, item_list)
    elif search == "ALL":
        items = requests.get("{}{}/Items?SearchTerm=&UserId={}&Recursive=true&IncludeItemTypes=Series,Movie"
                             .format(ipaddress, media_server, user_id), headers=request_header)
        if json_alone(items.json()["Items"]):
            print("\nOnly one item has been found.\nDo you want to select this title?")
            item_list = print_json(items.json(), True)
        else:
            print("Please choose from the following results: ")
            item_list = print_json(items.json(), False)
        pick = process_input(False, item_list)
    else:
        pick = process_input(True, item_list)
    return item_list[pick]


def streaming(head_dict, item_list):
    from .playing import run_mpv

    def playlist(starting_pos):
        stream_url = ("{}{}/Videos/{}/stream?Container=mkv&Static=true&SubtitleMethod=External&api_key={}".format(
            ipaddress, media_server, episode_list[starting_pos].get("Id"),
            request_header.get("X-{}-Token".format(media_server_name))))
        run_mpv(stream_url, episode_list[starting_pos], head_dict, appname)
        if not (starting_pos + 1) < len(episode_list):
            print("Ok. bye :)")
            return
        next_ep = True
        try:
            input("Welcome back. Do you want to continue playback with {}?\n[Enter]".format(
                episode_list[starting_pos + 1].get("Name")))
        except KeyboardInterrupt:
            exit()
        index = 1
        while next_ep:
            starting_pos = starting_pos + index
            print("Starting playback of {}.".format(episode_list[starting_pos].get("Name")))
            stream_url = (
                "{}{}/Videos/{}/stream?Container=mkv&Static=true&SubtitleMethod=External&api_key={}".format(
                    ipaddress, media_server, episode_list[starting_pos].get("Id"),
                    request_header.get("X-{}-Token".format(media_server_name))))
            run_mpv(stream_url, episode_list[starting_pos], head_dict, appname)
            if not (starting_pos + 1) < len(episode_list):
                next_ep = False

    ipaddress = head_dict.get("config_file").get("ipaddress")
    media_server = head_dict.get("media_server")
    media_server_name = head_dict.get("media_server_name")
    user_id = head_dict.get("user_id")
    request_header = head_dict.get("request_header")
    if item_list.get("Type") == "Movie":
        print("Starting mpv...".format(item_list.get("Name")))
        stream_url = ("{}{}/Videos/{}/stream?Container=mkv&Static=true&SubtitleMethod=External&api_key={}".format(
            ipaddress, media_server, item_list.get("Id"), request_header.get("X-{}-Token".format(media_server_name))))
        run_mpv(stream_url, item_list, head_dict, appname)
    elif item_list.get("Type") == "Series":
        print("{}:".format(item_list.get("Name")))
        series = requests.get("{}{}/Users/{}/Items?ParentId={}".format(
            ipaddress, media_server, user_id, item_list.get("Id")), headers=request_header).json()
        season_list = []
        for x in series["Items"]:
            season_list.append(x)
        episode_list = []
        for y in season_list:
            print("   {}".format(y.get("Name")))
            episodes = requests.get("{}{}/Users/{}/Items?ParentId={}".format(
                ipaddress, media_server, user_id, y.get("Id")), headers=request_header).json()
            for z in episodes["Items"]:
                episode_list.append(z)
                if z.get("UserData").get("Played") == 0:
                    print("      [{}] {}".format(episode_list.index(z), z.get("Name")))
                else:
                    print("      [{}] {}".format(episode_list.index(z), z.get("Name")), end="")
                    green_print(" [PLAYED]")
        starting_pos = input("Please enter which episode you want to continue at.\n: ")
        starting_pos = int(re.sub("[^0-9]", "", starting_pos))
        if starting_pos < (len(episode_list) + 1) and not starting_pos < 0:
            print("\nYou've chosen ", end='')
            blue_print(episode_list[starting_pos].get("Name"))
        else:
            print("Are you stupid?!")
            exit()
        playlist(starting_pos)
    green_print("All playback has finished.\nPress [Enter] to search for something else.")
    try:
        input()
    except KeyboardInterrupt:
        requests.post("{}{}/Sessions/Logout".format(
                ipaddress, media_server), headers=request_header)
        exit()
    item_list = choosing_media(head_dict)
    streaming(head_dict, item_list)


def main():
    head_dict = check_information(appname, version)
    item_list = choosing_media(head_dict)
    streaming(head_dict, item_list)


main()
