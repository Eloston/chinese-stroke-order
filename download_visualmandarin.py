#!/usr/bin/env python3

# Download all stroke order diagrams from visualmandarin.com
# Runs in the current directory

import pathlib
from bs4 import BeautifulSoup
import json
import urllib.request
import shutil

CHARACTER_PAGES = [
    "http://www.visualmandarin.com/tools/chinese-stroke-order/a-c",
    "http://www.visualmandarin.com/tools/chinese-stroke-order/d-f",
    "http://www.visualmandarin.com/tools/chinese-stroke-order/g-j",
    "http://www.visualmandarin.com/tools/chinese-stroke-order/k-m",
    "http://www.visualmandarin.com/tools/chinese-stroke-order/n-p",
    "http://www.visualmandarin.com/tools/chinese-stroke-order/q-s",
    "http://www.visualmandarin.com/tools/chinese-stroke-order/t-x",
    "http://www.visualmandarin.com/tools/chinese-stroke-order/y-z"
]

def get_character_to_id_dict():
    '''
    Returns a dictionary containing the following key -> value pairs:
        (character) -> id
    '''
    character_to_id_dict = dict()

    for url in CHARACTER_PAGES:
        print("Downloading " + url)
        with urllib.request.urlopen(urllib.request.Request(url)) as response:
            response_encoding = response.headers["Content-Type"].split("charset=")[1]
            response_data = response.read().decode(response_encoding)
            print("Parsing " + url)
            soup = BeautifulSoup(response_data, "lxml")
            for anchor_tag in soup.find_all(attrs={"class": "calligraphy", "href": True}):
                character_to_id_dict[list(anchor_tag)[0][0]] = anchor_tag["href"].split("/")[-1]
    return character_to_id_dict

def download_stroke_diagram_by_id(character_id, diagram_directory):
    '''
    Download the stroke order diagram image to diagram_directory for character identified by character_id
    Returns a pathlib.Path pointing to the image file
    '''
    stroke_url = "http://www.visualmandarin.com/tools/chinese-stroke-order/showStroke?vocabId=" + character_id
    print("Downloading " + stroke_url)
    with urllib.request.urlopen(urllib.request.Request(stroke_url)) as response:
        response_encoding = response.headers["Content-Type"].split("charset=")[1]
        response_data = response.read().decode(response_encoding)
        print("Parsing " + stroke_url)
        soup = BeautifulSoup(response_data, "lxml")
        image_tag = soup.find(id="strokeImage")
        download_path = diagram_directory / pathlib.Path(image_tag["src"].split("/")[-1])
        if not download_path.is_file():
            print("Downloading " + image_tag["src"])
            with urllib.request.urlopen(urllib.request.Request(image_tag["src"])) as response:
                with download_path.open("wb") as file_obj:
                    shutil.copyfileobj(response, file_obj)
        return download_path

if __name__ == "__main__":
    json_index = pathlib.Path("visualmandarin_index.json")
    diagram_directory = pathlib.Path("visualmandarin_diagrams")
    json_char_to_id = pathlib.Path("visualmandarin_char_to_id.json")

    if not diagram_directory.is_dir():
        diagram_directory.mkdir()

    if json_char_to_id.is_file():
        print("Loading existing character to id dictionary from JSON file")
        with json_char_to_id.open("r") as file_obj:
            character_to_id_dict = json.load(file_obj)
    else:
        print("Downloading new character to id dictionary")
        character_to_id_dict = get_character_to_id_dict()
        with json_char_to_id.open("w") as file_obj:
            json.dump(character_to_id_dict, file_obj)

    character_to_image_path_dict = dict()

    print("Downloading stroke order diagrams")

    for character in character_to_id_dict.keys():
        file_path = download_stroke_diagram_by_id(character_to_id_dict[character], diagram_directory)
        character_to_image_path_dict[character] = str(file_path)

    with json_index.open("w") as file_obj:
        json.dump(character_to_image_path_dict, file_obj)
