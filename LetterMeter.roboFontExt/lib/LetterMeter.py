#!/usr/bin/env python
# -*- coding: utf-8 -*-

from vanilla import *
from AppKit import NSFont, NSColor
from LetterMeterLib import *

placeholderTxt = '''\
Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er
sich in seinem Bett zu einem ungeheuren Ungeziefer verwandelt. Er lag
auf seinem panzerartig harten Rücken und sah, wenn er den Kopf ein wenig
hob, seinen gewölbten, braunen, von bogenförmigen Versteifungen
geteilten Bauch, auf dessen Höhe sich die Bettdecke, zum gänzlichen
Niedergleiten bereit, kaum noch erhalten konnte. Seine vielen, im
Vergleich zu seinem sonstigen Umfang kläglich dünnen Beine flimmerten
ihm hilflos vor den Augen.'''.replace('\n', '')

class LetterMeter(object):

    padding = 10
    buttonWidth = 80
    lineHeight  = 23
    width = 800
    height = 520
    fontName = 'Menlo'
    fontSize = 13.0

    def __init__(self):
        self.w = Window(
                (self.width, self.height), "LetterMeter",
                minSize=(self.width, self.height))

        x = y = p = self.padding
        self.w.analyze = Button((x, y, self.buttonWidth, self.lineHeight),
                "analyze",
                callback=self.analyzeCallback)

        x += self.buttonWidth + p
        self.w.ignoreCase = CheckBox(
                (x, y, 120, self.lineHeight),
                "ignore case",
                value=False)

        # columns
        x = p
        y += self.lineHeight + p
        col1 = TextEditor(
                (0, 0, -0, -0),
                text=placeholderTxt,
                callback=self.setFontCallback,
                readOnly=False)

        col2 = TextEditor((0, 0, -0, -0), readOnly=True)
        col3 = TextEditor((0, 0, -0, -0), readOnly=True)
        col4 = TextEditor((0, 0, -0, -0), readOnly=True)

        # set monospaced font
        font = NSFont.fontWithName_size_(self.fontName, self.fontSize)
        col1._textView.setFont_(font)
        col2._textView.setFont_(font)
        col3._textView.setFont_(font)
        col4._textView.setFont_(font)

        # add panes to dialog
        self.panes = [
            dict(view=col1, identifier="col1"),
            dict(view=col2, identifier="col2"),
            dict(view=col3, identifier="col3"),
            dict(view=col4, identifier="col4"),
        ]

        self.w.splitView = SplitView((x, y, -p, -p), self.panes)

        self.w.open()

    def setFontCallback(self, sender):
        # set monospaced font
        font = NSFont.fontWithName_size_(self.fontName, self.fontSize)
        self.panes[0]['view']._textView.setFont_(font)
        # set colors
        white = NSColor.whiteColor()
        self.panes[0]['view']._textView.setBackgroundColor_(white)
        black = NSColor.blackColor()
        self.panes[0]['view']._textView.setTextColor_(black)

    def analyzeCallback(self, sender):

        text = self.panes[0]['view'].get()
        ignoreCase = self.w.ignoreCase.get()

        if ignoreCase:
            text = text.lower()

        # column 1: letter frequencies
        freq, total = getFrequencies(text)
        txt1  = formatFrequencies(freq, total)
        txt1 += "\n\n"
        txt1 += "total: %s" % total
        self.panes[1]['view'].set(txt1)

        # column 2: letter combinations
        text = stripPunctuation(text)
        freq, total = getLigFrequencies(text)
        txt2 = formatFrequencies(freq, total)
        self.panes[2]['view'].set(txt2)

        # column 3: groups analysis
        freq, total = getGroupFrequencies(text)
        lines = []
        words = text.split()
        wordCount = len(words)
        charCount = sum([len(w) for w in words])
        if len(words):
            avgWordLen = charCount / float(len(words))
        else:
            avgWordLen = 0
        if charCount:
            accuracy = 100 - 100 * (freq.get("<unknown>", 0) / float(charCount))
        else:
            accuracy = 100
        lines.append("%16s %5s" % ("accuracy", "%.1f" % accuracy))
        lines.append("%16s %5s" % ("character count", charCount))
        lines.append("%16s %5s" % ("word count", wordCount))
        lines.append("%16s %5s" % ("avg. word length", "%.1f" % avgWordLen))
        lines.append("\n")
        txt3  = "\n".join(lines)
        txt3 += formatGroups(freq, total)
        txt3 += "\n"
        txt3 += formatFrequencies(freq, total, "%16s %5d %8s %%")
        self.panes[3]['view'].set(txt3)

if __name__ == '__main__':

    LetterMeter()
