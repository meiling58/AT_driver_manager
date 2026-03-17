
import json
import csv
import os


def get_path():
    # create a folder name data on the up a level if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.getcwd()), "../data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def save_json(data, path=f"{get_path()}/ollama_library.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_csv(data, path=f"{get_path()}/ollama_library.csv"):
    if data:
        keys = data[0].keys()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
