from collections import Counter
import re
import sys

def getExtractedRelatedData(fileName, regex):
    r = re.compile(regex, re.IGNORECASE)
    return map(extractValue, filter(r.match, open(fileName, 'r', encoding="utf8")))

def extractValue(line):
    return re.match(r"(?:.*): (.*)", line).group(1)

def getComposers(names):
    return map(getComposer, names.split("; "))

def getComposer(fullName):
    names = re.split(', | ', fullName)
    
    if(not names[1:]):
        return filterOutYear(names[0])
    return (names[0] + ", " + "".join(map(getNameInitials, names[1:]))).strip()

def filterOutYear(input):
    result = ''
    for value in input.split():
        if(value.startswith("(") and value[1].isdigit()):
            continue
        result += value
    return result

def getNameInitials(name):
    if(not name or name.startswith("(")):
        return ''
    return name[0].upper() + ". "

def getCenturies(input):
    reYear = re.compile(r".*(\d{4}).*")
    reOrder = re.compile(r".*(\d{2})th.*")
    result = list()
    for candidate in input:
        year = reYear.match(candidate)
        if(year is not None):
            result.append(getCenturyString(getCentury(year.group(1))))
        century = reOrder.match(candidate)
        if(century is not None):
            result.append(getCenturyString(century.group(1)))
    return result
    
def getCentury(year):
    if (int(year) % 100 == 0):
        century = int(year) // 100
    else:
        century = (int(year) // 100) + 1
    return str(century)

def getCenturyString(century):
    lastDigit = re.search(r"\d{1}$", century).group(0)
    if (lastDigit == '1' and int(century) != 11):
        return century + "st century"
    elif (lastDigit == '2' and int(century) != 12):
        return century + "nd century"
    elif (lastDigit == '3' and int(century) != 13):
        return century + "rd century"
    else:
        return century + "th century"

def getAgregatedStats(data):
    stats = Counter()
    for d in filter(None, data):
        stats[d] += 1
    return stats    

def printStats(stats):
    for key, value in stats.items():
        print("%s: %d" % (key, value))

# MAIN 
def main(fileName, regex):
    regex = regex.lower()
    stats = list()
    
    if(regex == "composer"):
        regex = r"Composer: (.*)"
        data = getExtractedRelatedData(fileName, regex)
        for composers in data:
            stats.extend(getComposers(composers))

    elif(regex == "century"):
        regex = r"Composition Year: (.*)"
        data = getExtractedRelatedData(fileName, regex)
        stats.extend(getCenturies(data))

    stats = getAgregatedStats(stats)
    printStats(stats)

if __name__ == "__main__":
    filename = sys.argv[1]
    regex = sys.argv[2]
    main(filename, regex)