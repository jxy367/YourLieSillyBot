from pysubs2 import *
import os
import unidecode
from operator import itemgetter


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


def add_words(old_string: str):
    new_string = unidecode.unidecode(old_string).lower()

    while "{" in new_string:
        start = new_string.find("{")
        end = new_string.find("}")
        new_string = new_string.replace(new_string[start:end+1], "")

    new_string = new_string.replace("\\N", " ")
    new_string = new_string.replace("\\n", " ")
    new_string = new_string.replace("*", " ")
    new_string = new_string.replace("?", " ")
    new_string = new_string.replace("!", " ")
    new_string = new_string.replace(".", " ")
    new_string = new_string.replace('"', " ")
    new_string = new_string.replace(",", " ")
    new_string = new_string.replace("-", " ")
    new_string = new_string.replace("/", " ")
    new_string = new_string.replace(":", " ")
    new_string = new_string.replace("[", " ")
    new_string = new_string.replace("]", " ")

    for character in new_string:
        if not character.isprintable():
            new_string = new_string.replace(character, "")

    split_string = new_string.split(" ")
    for part in split_string:
        if "'" in part:
            split_word = part.split("'")
            if part in ["don't", "it's", "i'm", "that's", "shouldn't", "i'll", "aren't", "i've", "you'd", "he's",
                        "isn't", "they're", "you're", "we're", "haven't", "wouldn't", "it'll", "should've", "what's",
                        "won't", "let's", "she's", "you've", "they'd", "would've", "he'd", "who'll", "how'd",
                        "might've", "there'll", "could've", "she'd", "where'd", "didn't", "i'd", "wasn't", "hasn't",
                        "doesn't", "couldn't", "hadn't", "weren't"]:
                increment(part)
            elif split_word[0] == "":
                x = 0
            elif is_english_word(split_word[0]):  # Contraction
                if split_word[0] in ["window", "mother", "ball", "when", "client", "millions", "tomorrow", "women",
                                     "year", "here", "auditorium", "beethoven", "score", "panel", "nurse", "where",
                                     "piano", "students", "mind", "guy", "wallpaper", "mom", "mozart", "kid",
                                     "deduction", "violinist", "nobody", "baby", "skin", "anyone", "dad", "someone's",
                                     "tournament", "water", "one", "chopin", "else", "moon", "maiden", "ankle",
                                     "how", "competition", "instructor", "heart", "person", "everyone", "clock",
                                     "haydn", "season", "nothing", "tempo", "japan", "something", "promoters", "love",
                                     "savior", "show", "name", "playing", "lifestyle", "today", "man", "demon", "boy",
                                     "posture", "festival", "enemy", "writer", "brother", "december", "room",
                                     "everything", "family", "composer", "predecessors", "troublemaker", "snowball",
                                     "final", "sky", "impression", "wits", "dude", "everybody", "san", "someone"]:
                    increment(split_word[0])
                else:
                    increment(part)
                #print(part + ": " + str(word_frequency_dictionary[part]))
            else:
                x = 0
                #print(part)
        elif "" == part:
            x = 0
        else:
            if part in ["i", "melodica", "karaoke", "gonna", "caneles", "um", "anime", "gotta", "email", "taiyaki",
                        "sensei", "beatdown", "wuss", "wanna", "snarky", "wimp", "yum", "tengu", "senpai", "texted",
                        "canele", "popsicle", "babysitter", "dumbfounded", "smartass", "onigiri", "lolicon", "gotcha",
                        "robotic", "dodgeball", "vibe", "poof", "dreamboat", "internet", ]:
                increment(part)
            elif is_english_word(part):
                increment(part)
                #print(part + ": " + str(word_frequency_dictionary[part]))
            else:
                x = 0
                #print(part)


def increment(word):
    if word in word_frequency_dictionary.keys():
        word_frequency_dictionary[word] += 1
    else:
        word_frequency_dictionary[word] = 1


def is_english_word(word):
    return word.lower() in english_words


with open("EnglishWords.txt") as word_file:
    english_words = set(word.strip().lower() for word in word_file)

new_subtitle_file = open("YourLieSubtitlesV2.txt", 'w')
num_yl_episodes = 22
word_frequency_dictionary = {}


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
        add_words(text)

for key in word_frequency_dictionary.keys():
    new_subtitle_file.write(key + ":" + str(word_frequency_dictionary[key]) + "\n")

#for key, value in sorted(word_frequency_dictionary.items(), key=itemgetter(1), reverse = True):
#    print(key, value)

new_subtitle_file.close()
