import os
import re
import sys
import operator


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

        edition = self.edition.toString()
        if(edition.strip()):
            edition = "\n" + edition

        print("Print Number: {}{}\nPartiture: {}\n".format(
              self.print_id,
              edition,
              partiture))

    def composition(self):
        return self.edition.composition

    def setBooleanByString(self, boolString):
        if(boolString == "no"):
            self.partiture = False
        elif(boolString == "yes"):
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
        return "Edition: {}\nEditor: {}\nPublication Year: {}\n{}".format(
            self.name or "",
            ", ".join(map(lambda x: x.toString(), self.authors)),
            self.year or "",
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
        voices = "\n".join(map(lambda x: x.toString(), self.voices))
        if(voices.strip()):
            voices = "\n" + voices
        return "Title: {}\nIncipit: {}\nKey: {}\nGenre: {}\nComposition Year: {}\nComposer: {}{}".format(
            self.name or "",
            self.incipit or "",
            self.key or "",
            self.genre or "",
            self.year or "",
            "; ".join(map(lambda x: x.toString(), self.authors)),
            voices
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
        rKey = re.match(r"voice (\d*)", key)
        rVoice = re.match(r"(.*)--(.*)(;|,) (.*)", voice)

        if(rVoice is None):
            self.name = voice
            self.order = int(rKey.group(1))
        else:
            self.name = rVoice.group(4)
            self.range = "{}--{}".format(rVoice.group(1), rVoice.group(2))

    def toString(self):
        if(self.range is None):
            return "Voice {}: {}".format(self.order, self.name)
        return "Voice {}: {}, {}".format(self.order, self.range, self.name)


class Person:
    def __init__(self):
        self.name = None
        self.born = None
        self.died = None

    def toString(self):
        if(self.born is not None or self.died is not None):
            return "{} ({}--{})".format(self.name or "", self.born or "", self.died or "")
        return self.name or ""


def load(filename):
    content = open(filename, 'r', encoding="utf-8").read()

    if not content:
        return ""

    blockObjects = content.split("\n\n")
    result = list()

    for blockObject in blockObjects:
        print = Print()

        for key, value in filter(None, map(splitKeyAndValue, blockObject.split("\n"))):
            if key is None:
                continue

            key = key.lower()
            if(key == "print number"):
                print.print_id = int(value)
            elif(key == "composer"):
                print.composition().addComposersByString(value)
            elif(key == "title"):
                print.composition().name = value
            elif(key == "genre"):
                print.composition().genre = value
            elif(key == "key"):
                print.composition().key = value
            elif(key == "composition year"):
                if(value.isdigit()):
                    print.composition().year = int(value)
            elif(key == "publication year"):
                if(value.isdigit()):
                    print.edition.year = int(value)
            elif(key == "edition"):
                print.edition.name = value
            elif(key == "editor"):
                print.edition.setEditorsByString(value)
            elif(key == "partiture"):
                print.setBooleanByString(value)
            elif(key == "incipit"):
                print.composition().incipit = value
            elif(str(key).startswith("voice")):
                print.composition().addVoiceByString(key, value)

        if(print.print_id is not None):
            result.append(print)

    return sorted(result, key=operator.attrgetter('print_id'))


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
