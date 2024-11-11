import json
import os
import py_common.log as log  # type: ignore
from py_common.util import scraper_args  # type: ignore
import sys

dirAddFriends = "/data/addfriends/"
dirModelArchive = dirAddFriends + "model-archive/"


def postprocess(obj, _):
    return obj


def findModelArchiveJsons(name: str) -> list[str]:
    result = []

    for dirpath, _, filenames in os.walk(dirModelArchive):
        for filename in [f for f in filenames if name in f]:
            filepath = os.path.join(dirpath, filename)
            result.append(filepath)

    return result


def searchPerformer(name: str):
    # perform scraping here - using name for the query
    res = findModelArchiveJsons(name)

    # fill in the output
    data = []

    # example shown for a single found performer
    for jsonFile in res:
        with open(jsonFile) as f:
            jsonData = json.load(f)
            jsonData = jsonData["site"]
            filePath = jsonFile.split(dirModelArchive)[1]

            p = {}
            p["name"] = jsonData["site_name"]
            p["disambiguation"] = filePath
            data.append(p)
            f.close()

    return data


def scrapePerformer(input):
    # Get the json file
    jsonFile = dirModelArchive + input["disambiguation"]

    ret = {}

    with open(jsonFile) as f:
        jsonData = json.load(f)
        jsonData = jsonData["site"]

        # Basic
        ret["name"] = jsonData["site_name"]
        ret["details"] = jsonData["news"]

        # Images - profile
        profileImg = (
            "https://static.addfriends.com/images/friends/"
            + jsonData["site_url"]
            + ".jpg"
        )
        ret["images"] = [profileImg]

        # Images - slider
        i = 1
        while i < 7:
            img = (
                "https://addfriends.com/"
                + jsonData["site_url"]
                + "-slide-"
                + str(i)
                + ".jpg"
            )
            ret["images"].append(img)
            i += 1

        # Tags
        ret["tags"] = []
        for tag in jsonData["tags"]:
            ret["tags"].append({"name": tag["hash_tag"]})

        # URLs
        urlAddFriends = "https://addfriends.com/" + jsonData["site_url"]
        urlSnapchat = "https://snapchat.com/add/" + jsonData["free_snapchat"]
        ret["urls"] = [urlAddFriends, urlSnapchat]

        f.close()

    return ret


def main_scraper():
    op, args = scraper_args()
    result = None
    match op, args:
        case "performer-by-fragment", args:
            # Get the affiliated file
            result = scrapePerformer(args)
        case "performer-by-name", {"name": name} if name:
            result = searchPerformer(name)
        case _:
            log.error(f"Operation: {op}, arguments: {json.dumps(args)}")
            sys.exit(1)

    print(json.dumps(result))


if __name__ == "__main__":
    main_scraper()
