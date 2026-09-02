from pathlib import Path
import yaml

current_path = Path(__file__)
config_path = current_path.parent / 'colors.yaml'

with open(config_path, encoding = 'utf-8') as f:
    colors = yaml.safe_load(f)

color_list = []
for color_name in colors.keys():
    if color_name == 'black' or color_name == 'red':
        continue
    color_list.append(tuple(colors[color_name]))