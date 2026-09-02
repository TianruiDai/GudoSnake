from pathlib import Path
import sys
import yaml


def _config_path():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "color" / "colors.yaml"
    return Path(__file__).parent / "colors.yaml"


with open(_config_path(), encoding="utf-8") as f:
    colors = yaml.safe_load(f)

color_list = []
for color_name in colors.keys():
    if color_name == 'black' or color_name == 'red':
        continue
    color_list.append(tuple(colors[color_name]))