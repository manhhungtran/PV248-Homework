import os
import re
import sys


class Print:
    def __init__(self):
        self.edition = Edition()
        self.print_id = None
        self.partiture = None

    def format(self):
        partiture = ""
        if (self.partiture):
            partiture = "yes"
        if(not self.partiture):
            partiture = "no"

        print("Print number: {}\n{}\nPartiture: {}\n\n".format(
              self.edition,
              self.edition.toString(),
              partiture))

    def composition(self):
        return self.edition.composition

    def setBooleanByString(self, boolString):
        if(boolString == "no"):
            self.partiture = False
        if(boolString == "yes"):
            self.partiture = True


class Edition:
    def __init__(self):
        self.composition = Composition()
        self.authors = list()
        self.name = None
        self.year = None

    def setEditorsByString(self, editors):
        self.authors.extend(map(getPersonFromString, editors.split(", ")))

    def toString(self):
        return "Edition {}\nEditor: {}\nPublication Year: {}\n{}".format(
            self.name,
            ", ".join(map(lambda x: x.toString(), self.authors)),
            self.year,
            self.composition.toString())


class Composition:
    def __init__(self):
        self.name = None
        self.incipit = None
        self.key = None
        self.genre = None
        self.year = None
        self.voices = list()
        self.authors = list()

    def toString(self):
        return "Title: {}\nIncipit: {}\nKey: {}\nGenre: {}\n Composition Year: {}\n{}\nComposer: {}".format(
            self.name,
            self.incipit,
            self.key,
            self.genre,
            self.year,
            "\n".join(map(lambda x: x.toString(), self.voices)),
            "; ".join(map(lambda x: x.toString(), self.authors))
        )

    def addComposersByString(self, names):
        self.authors.extend(map(getPersonFromString, names.split("; ")))

    def addVoiceByString(self, key, voice):
        v = Voice()
        v.setVoiceByString(key, voice)
        self.voices.append(v)


class Voice:
    def __init__(self):
        self.order = 0
        self.name = None
        self.range = None

    def setVoiceByString(self, key, voice):
        rKey = re.match(r"Voice (\d*)", key)
        rVoice = re.match(r"(.*)--(.*), (.*)", voice)

        if(rVoice is None):
            self.name = voice
            self.order = int(rKey.group(1))
        else:
            self.name = rVoice.group(3)
            self.range = "{}--{}".format(rVoice.group(1), rVoice.group(2))

    def toString(self):
        if(range is None):
            return "Voice {}: {}".format(self.order, self.name)
        return "Voice {}: {}, {}".format(self.order, self.range, self.name)


class Person:
    def __init__(self):
        self.name = None
        self.born = None
        self.died = None

    def toString(self):
        return "{} ({}--{})".format(self.name, self.born, self.died)


def load(filename):
    with open(filename, 'r', encoding="utf8") as f:
        content = f.read()

    blockObjects = content.split("\n\n")
    result = list()

    for blockObject in blockObjects:
        print = Print()

        for key, value in filter(None, map(splitKeyAndValue, blockObject.split("\n"))):
            if(key == "Print Number"):
                print.print_id = int(value)
            elif(key == "Composer"):
                print.composition().addComposersByString(value)
            elif(key == "Title"):
                print.composition().name = value
            elif(key == "Genre"):
                print.composition().genre = value
            elif(key == "Key"):
                print.composition().key = value
            elif(key == "Composition Year"):
                print.composition().year = int(value)
            elif(key == "Publication Year"):
                print.edition.year = int(value)
            elif(key == "Edition"):
                print.edition.name = value
            elif(key == "Editor"):
                print.edition.setEditorsByString(value)
            elif(key == "Partiture"):
                print.setBooleanByString(value)
            elif(key == "Incipit"):
                print.composition().incipit = value
            elif(str(key).startswith("Voice")):
                print.composition().addVoiceByString(key, value)

        result.append(print)

    return result.sort(key=lambda x: x.print_id)


def getPersonFromString(person):
    r = re.match(
        r"(.*) \(((\d*)--(\d*)|\+(\d+)|\*(\d+)|(\d+))\)", person)
    someone = Person()
    if(r is None):
        someone.name = person
    else:
        someone.name = r.group(1)
        if(r.group(3)):
            someone.born = int(r.group(3))
        elif(r.group(6)):
            someone.born = int(r.group(6))
        elif(r.group(7)):
            someone.born = int(r.group(7))

        if(r.group(4)):
            someone.died = int(r.group(4))
        elif(r.group(5)):
            someone.died = int(r.group(5))
    return someone


def splitKeyAndValue(line):
    r = re.compile("(.*): (.*)")
    result = r.match(line)

    if(result is None or not result.group(2)):
        return None, None
    return (result.group(1), result.group(2).strip())
