import os

def readGroups():
    baseFolder = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(baseFolder, 'resources', "CharacterGroups.txt")
    groups = {}
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        items = line.split("\t")
        if len(items) > 1:
            char = chr(int(items[0], 16))
            charGroups = []
            for g in items[2:]:
                g = g.strip()
                if not g:
                    continue
                charGroups.append(g)
            groups[char] = charGroups
    return groups

def addSpecialGroup(groups):
    for k, v in groups.items():
        if "ascender" in v or "descender" in v:
            v.append("asc_or_desc")
        if "ascender" in v and "descender" in v:
            v.append("asc_and_desc")
        if "right_round" in v or "left_round" in v:
            v.append("round")
        if "right_square" in v or "left_square" in v:
            v.append("square")
        if "right_diagonal" in v or "left_diagonal" in v:
            v.append("diagonal")
        if "right_open" in v or "left_open" in v:
            v.append("open")

groups = readGroups()
addSpecialGroup(groups)
if 0:
    longest = 0
    for gg in groups.values():
        for g in gg:
            longest = max(longest, len(g))

def stripPunctuation(s):
    from unicodedata import category
    l = []
    for c in s:
        if category(c)[:1] not in "PS":
            l.append(c)
        else:
            l.append(" ")
    return "".join(l)

def getGroupFrequencies(text):
    unknown = ["<unknown>"]
    d = {}
    total = 0
    for c in text:
        if not c.strip():
            continue
        for g in groups.get(c, unknown):
            try:
                d[g] += 1
            except KeyError:
                d[g] = 1
        total += 1  # total _chars_, not total groups
    return d, total

def getFrequencies(text):
    d = {}
    total = 0
    for c in text:
        if not c.strip():
            continue
        try:
            d[c] += 1
        except KeyError:
            d[c] = 1
        total += 1
    return d, total

def getLigFrequencies(text, nChars=3):
    words = text.split()
    d = {}
    total = 0
    for word in words:
        for i in range(len(word) - nChars + 1):
            lig = word[i:i+nChars]
            try:
                d[lig] += 1
            except KeyError:
                d[lig] = 1
            total += 1
    return d, total

def formatFrequencies(d, total, format="%s %5d %8s %%", lastKey=None):
    d = d.copy()
    if lastKey is not None:
        if lastKey in d:
            lastValue = d[lastKey]
            del d[lastKey]
        else:
            lastValue = 0
    freq = [(v, k) for k, v in d.items()]
    freq.sort()
    freq.reverse()
    if lastKey is not None:
        freq.append((lastValue, lastKey))
    if not total:
        total = 1
    lines = [format % (k, v, "%.1f" % (100.0 * v / total)) for v, k in freq]
    return "\n".join(lines)

"""
output sketch from Peter B:

Accuracy                   99%
Total glyphs            23,200
Total words              4,345
Average length of word     5.2
-------------------------------------
Consonants               58.6%   799
Vowels                   38.2%   455
-------------------------------------
Descenders               18.2%    85
Ascenders                12.2%    55
Both                     22.2%   135
-------------------------------------
Accented                 12.2%    55
-------------------------------------
Round                    44.2%   600
Square                   44.2%   600
Diagonal                 44.2%   600
Open                     44.2%   600
-------------------------------------
   left_square           52.8 %  896
    left_round           38.4 %  651
  right_square           38.0 %  645
   right_round           33.4 %  566
    right_open           19.6 %  332
"""

def subset(d, keys, names=None):
    if names is None:
        names = keys
    else:
        assert len(keys) == len(names)
    sub = {}
    for k, n in zip(keys, names):
        sub[n] = d.get(k, 0)
    return sub

def formatGroups(freq, total):
    hbar = "-" * 32
    format = "%16s %5d %8s %%"
    lines = []

    lines.append(hbar)

    d = subset(freq, ["vowel", "consonant"], ["vowels", "consonants"])
    lines.append(formatFrequencies(d, total, format))
    lines.append(hbar)

    d = subset(freq, ["ascender", "descender", "asc_or_desc", "asc_and_desc"],
        ["ascenders", "descenders", "asc or desc", "asc and desc"])
    lines.append(formatFrequencies(d, total, format))
    lines.append(hbar)

    d = subset(freq, ["accented"])
    lines.append(formatFrequencies(d, total, format))
    lines.append(hbar)

    d = subset(freq, ["round", "square", "diagonal", "open"])
    lines.append(formatFrequencies(d, total, format))
    lines.append(hbar)

    return "\n".join(lines)
