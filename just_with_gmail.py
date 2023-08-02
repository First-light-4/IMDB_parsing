import json


def open_info(filename):
    with open(f"{filename}.json") as file:
        lines = json.load(file)
    return lines

def get_just_name_mail():
    name_info = {}
    for name, info in open_info('casting_director').items():
        if 'mail' in info['info']:
            print(name.split('\n')[0])
            print(info['info'].split('mailto:')[1])
            name_info[name.split('\n')[0]] = info['info'].split('mailto:')[1]
    return name_info


if __name__ == '__main__':
    get_just_name_mail()

