from pysubs2 import *
import os
import unidecode


def search(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def replace_special(old_string: str):
    new_string = unidecode.unidecode(old_string)
    if "*" in old_string:
        return ""

    while "{" in new_string:
        start = new_string.find("{")
        end = new_string.find("}")
        new_string = new_string.replace(new_string[start:end+1], "")

    new_string = new_string.replace("\\N", " ")
    #new_string = new_string.replace("?", " ")
    #new_string = new_string.replace("!", " ")
    #new_string = new_string.replace(".", " ")
    #new_string = new_string.replace('"', " ")

    for character in new_string:
        if not character.isprintable():
            new_string = new_string.replace(character, "")

    #for character in new_string:
    #    if not character.isalpha():
    #        if character != "'":
    #            new_string = new_string.replace(character, ' ')
    return new_string


new_subtitle_file = open("YourLieSubtitles.txt", 'w')
num_yl_episodes = 22

for i in range(1, num_yl_episodes + 1):
    if i < 10:
        episode_num = str(0) + str(i)
    else:
        episode_num = str(i)
    start_dir = 'Subtitles'
    file_name = 'YourLieInApril' + episode_num + '.ass'
    ugh_path = search(file_name, start_dir)
    subs = SSAFile.load(path=ugh_path)
    for line in subs:
        text = line.text
        text = text.strip()
        text = replace_special(text)
        if text != "":
            new_subtitle_file.write(text + '\n')

new_subtitle_file.close()
