import json
import os
import py_common.log as log
from py_common.util import scraper_args
import sys
from py_common.types import PerformerSearchResult, ScrapedPerformer

# Constants
dirAddFriends = "/data/addfriends/"
dirModelArchive = dirAddFriends + "model-archive/"


def searchPerformer(name: str) -> list[PerformerSearchResult]:
    """
    Find JSON files in the model-archive folder that include the performer's
    name, and return data to display in the results list.
    """

    # Search for files
    files = []
    for dirpath, _, filenames in os.walk(dirModelArchive):
        for filename in [f for f in filenames if name in f]:
            filepath = os.path.join(dirpath, filename)
            files.append(filepath)

    # Create the results page data
    res = []
    for jsonFile in files:
        with open(jsonFile) as f:
            jsonData = json.load(f)
            jsonData = jsonData["site"]
            filePath = jsonFile.split(dirModelArchive)[1]

            p: PerformerSearchResult = {}
            p["name"] = jsonData["site_name"]
            p["disambiguation"] = filePath
            res.append(p)
            f.close()

    return res


def scrapePerformer(args: PerformerSearchResult) -> ScrapedPerformer:
    """
    Return all available performer data from the found model-archive file as
    Stash performer data.
    """

    # Get the json file
    jsonFile = dirModelArchive + args["disambiguation"]
    ret: ScrapedPerformer = {}

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
            result = scrapePerformer(args)
        case "performer-by-name", {"name": name} if name:
            result = searchPerformer(name)
        case _:
            log.error(f"Operation: {op}, arguments: {json.dumps(args)}")
            sys.exit(1)

    print(json.dumps(result))


if __name__ == "__main__":
    main_scraper()
