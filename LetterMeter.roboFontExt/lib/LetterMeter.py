#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from importlib import reload
# import LetterMeter_lib
# reload(LetterMeter_lib)

from vanilla import *
from AppKit import NSFont, NSColor
from LetterMeter_lib import *

placeholder_txt = '''\
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
    button_width = 80
    line_height  = 23
    width = 800
    height = 520
    font_name = 'Menlo'
    font_size = 13.0

    def __init__(self):
        self.w = Window(
                (self.width, self.height), "LetterMeter",
                minSize=(self.width, self.height),
                # maxSize=(1200, 800),
            )
        x = y = p = self.padding
        self.w.analyze = Button((x, y, self.button_width, self.line_height),
                "analyze",
                callback=self.analyze_callback
            )
        x += self.button_width + p
        self.w.ignore_case = CheckBox(
                (x, y, 120, self.line_height),
                "ignore case",
                value=False,
            )
        # columns
        x = p
        y += self.line_height + p
        col_1 = TextEditor(
                (0, 0, -0, -0),
                text=placeholder_txt,
                callback=self.set_font_callback,
                readOnly=False
            )
        col_2 = TextEditor((0, 0, -0, -0), readOnly=True)
        col_3 = TextEditor((0, 0, -0, -0), readOnly=True)
        col_4 = TextEditor((0, 0, -0, -0), readOnly=True)
        # set monospaced font
        font = NSFont.fontWithName_size_(self.font_name, self.font_size)
        col_1._textView.setFont_(font)
        col_2._textView.setFont_(font)
        col_3._textView.setFont_(font)
        col_4._textView.setFont_(font)
        # add panes to dialog
        self.panes = [
            dict(view=col_1, identifier="col_1"),
            dict(view=col_2, identifier="col_2"),
            dict(view=col_3, identifier="col_3"),
            dict(view=col_4, identifier="col_4"),
        ]
        self.w.split_view = SplitView((x, y, -p, -p), self.panes)
        # open window
        self.w.open()

    def set_font_callback(self, sender):
        # set monospaced font
        font = NSFont.fontWithName_size_(self.font_name, self.font_size)
        self.panes[0]['view']._textView.setFont_(font)
        # set colors
        white = NSColor.whiteColor()
        self.panes[0]['view']._textView.setBackgroundColor_(white)
        black = NSColor.blackColor()
        self.panes[0]['view']._textView.setTextColor_(black)

    def analyze_callback(self, sender):

        text = self.panes[0]['view'].get()
        ignore_case = self.w.ignore_case.get()

        if ignore_case:
            text = text.lower()

        # column 1: letter frequencies
        freq, total = getFrequencies(text)
        txt_1  = formatFrequencies(freq, total)
        txt_1 += "\n\n"
        txt_1 += "total: %s" % total
        self.panes[1]['view'].set(txt_1)

        # column 2: letter combinations
        text = stripPunctuation(text)
        freq, total = getLigFrequencies(text)
        txt_2 = formatFrequencies(freq, total)
        self.panes[2]['view'].set(txt_2)

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
        txt_3  = "\n".join(lines)
        txt_3 += formatGroups(freq, total)
        txt_3 += "\n"
        txt_3 += formatFrequencies(freq, total, "%16s %5d %8s %%")
        self.panes[3]['view'].set(txt_3)

if __name__ == '__main__':

    LetterMeter()
