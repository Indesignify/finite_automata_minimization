# -*- coding: utf-8 -*-

import time

import sys

try:
    from Tkinter import *
    import tkFont
except ImportError as err:
    print "Ошибка: %s. Для корректного отображения графического интерфейса в системе должна быть установлена библиотека Tkinter." % err.message
    sys.exit(1)

from AutomataTheory import *

dotFound = is_installed("dot")
if dotFound:
    try:
        from PIL import Image, ImageTk
    except ImportError as err:
        print "Внимание: {}. Библиотека PIL требуется для корректного отображения изображений.".format(err.message)
        dotFound = False
else:
    print "Внимание: для корректного отображения изображений требуется программное обеспечение GraphViz."


class AutomataGUI:
    def __init__(self, root, dotFound):
        self.root = root
        self.init_ui()
        self.selectedButton = 0
        self.dotFound = dotFound
        startRegex = "0+1*0"
        self.regexVar.set(startRegex)
        self.handle_build_regex_button()

    def init_ui(self):
        self.root.title("Конечный автомат из регулярного выражения")
        ScreenSizeX = self.root.winfo_screenwidth()
        ScreenSizeY = self.root.winfo_screenheight()
        ScreenRatioX = 0.7
        ScreenRatioY = 0.8
        self.FrameSizeX = int(ScreenSizeX * ScreenRatioX)
        self.FrameSizeY = int(ScreenSizeY * ScreenRatioY)
        print self.FrameSizeY, self.FrameSizeX
        FramePosX = (ScreenSizeX - self.FrameSizeX) / 2
        FramePosY = (ScreenSizeY - self.FrameSizeY) / 2
        padX = 10
        padY = 10
        self.root.geometry("%sx%s+%s+%s" % (self.FrameSizeX, self.FrameSizeY, FramePosX, FramePosY))
        self.root.resizable(width=False, height=False)

        parentFrame = Frame(self.root, width=int(self.FrameSizeX - 2 * padX), height=int(self.FrameSizeY - 2 * padY))
        parentFrame.grid(padx=padX, pady=padY, stick=E + W + N + S)

        regexFrame = Frame(parentFrame)
        enterRegexLabel = Label(regexFrame,
                                text="Введите регулярное выражение (разрешены операторы +, . и *):")
        self.regexVar = StringVar()
        self.regexField = Entry(regexFrame, width=80, textvariable=self.regexVar)
        buildRegexButton = Button(regexFrame, text="Построить", width=10, command=self.handle_build_regex_button)
        enterRegexLabel.grid(row=0, column=0, sticky=W)
        self.regexField.grid(row=1, column=0, sticky=W)
        buildRegexButton.grid(row=1, column=1, padx=5)

        testStringFrame = Frame(parentFrame)
        testStringLabel = Label(testStringFrame, text="Введите строку для распознавания: ")
        self.testVar = StringVar()
        self.testStringField = Entry(testStringFrame, width=80, textvariable=self.testVar)
        testStringButton = Button(testStringFrame, text="Проверка", width=10, command=self.handle_test_string_button)
        testStringLabel.grid(row=0, column=0, sticky=W)
        self.testStringField.grid(row=1, column=0, sticky=W)
        testStringButton.grid(row=1, column=1, padx=5)

        self.statusLabel = Label(parentFrame)

        buttonGroup = Frame(parentFrame)
        self.timingLabel = Label(buttonGroup, text="Загрузка...", width=50, justify=LEFT)
        nfaButton = Button(buttonGroup, text="NFA", width=15, command=self.handle_nfa_button)
        dfaButton = Button(buttonGroup, text="DFA", width=15, command=self.handle_dfa_button)
        minDFAButton = Button(buttonGroup, text="Минимизированный DFA", width=30, command=self.handle_min_dfa_button)
        self.timingLabel.grid(row=0, column=0, sticky=W)
        nfaButton.grid(row=0, column=1)
        dfaButton.grid(row=0, column=2)
        minDFAButton.grid(row=0, column=3)

        automataCanvasFrame = Frame(parentFrame, height=100, width=100)
        self.cwidth = int(self.FrameSizeX - (2 * padX + 20))
        self.cheight = int(self.FrameSizeY * 0.6)
        self.automataCanvas = Canvas(automataCanvasFrame, bg='#FFFFFF', width=self.cwidth, height=self.cheight,
                                     scrollregion=(0, 0, self.cwidth, self.cheight))
        hbar = Scrollbar(automataCanvasFrame, orient=HORIZONTAL)
        hbar.pack(side=BOTTOM, fill=X)
        hbar.config(command=self.automataCanvas.xview)
        vbar = Scrollbar(automataCanvasFrame, orient=VERTICAL)
        vbar.pack(side=RIGHT, fill=Y)
        vbar.config(command=self.automataCanvas.yview)
        self.automataCanvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvasitems = []
        self.automataCanvas.pack()

        self.bottomLabel = Label(parentFrame,
                                 text="Работа выполнена Михаилом Куликовым и Даниилом Чхеидзе в рамках курса \"Теория формальных языков и трансляций\"")

        regexFrame.grid(row=0, column=0, sticky=W, padx=(50, 0))
        testStringFrame.grid(row=1, column=0, sticky=W, padx=(50, 0))
        self.statusLabel.grid(row=2, column=0, sticky=W, padx=(50, 0))
        buttonGroup.grid(row=3, column=0)
        automataCanvasFrame.grid(row=4, column=0, sticky=E + W + N + S)
        self.bottomLabel.grid(row=5, column=0, sticky=W, pady=10)

    def handle_build_regex_button(self):
        t = time.time()
        try:
            inp = self.regexVar.get().replace(' ', '')
            if inp == '':
                self.statusLabel.config(text="Обнаружено пустое регулярное выражение!")
                return
            self.create_automata(inp)
        except BaseException as e:
            self.statusLabel.config(text="Ошибка: %s" % e)
        self.timingLabel.configure(text="Операция выполнена за " + "%.4f" % (time.time() - t) + " секунд")
        self.display_automata()

    def handle_test_string_button(self):
        t = time.time()
        inp = self.testVar.get().replace(' ', '')
        if inp == '':
            inp = [':e:']
        if self.dfaObj.accepts_string(inp):
            self.statusLabel.config(text="Принимает :)")
        else:
            self.statusLabel.config(text="Не принимает :|")
        self.timingLabel.configure(text="Операция выполнена за " + "%.4f" % (time.time() - t) + " секунд")

    def handle_nfa_button(self):
        self.selectedButton = 0
        self.display_automata()

    def handle_dfa_button(self):
        self.selectedButton = 1
        self.display_automata()

    def handle_min_dfa_button(self):
        self.selectedButton = 2
        self.display_automata()

    def create_automata(self, input):
        print u"Регулярное выражение: ", input
        nfaObj = NFAfromRegex(input)
        self.nfa = nfaObj.get_nfa()
        self.dfaObj = DFAfromNFA(self.nfa)
        self.dfa = self.dfaObj.get_dfa()
        self.minDFA = self.dfaObj.get_minimised_dfa()
        if self.dotFound:
            draw_graph(self.dfa, "dfa")
            draw_graph(self.nfa, "nfa")
            draw_graph(self.minDFA, "mdfa")
            dfafile = "graphdfa.png"
            nfafile = "graphnfa.png"
            mindfafile = "graphmdfa.png"
            self.nfaimagefile = Image.open(nfafile)
            self.dfaimagefile = Image.open(dfafile)
            self.mindfaimagefile = Image.open(mindfafile)
            self.nfaimg = ImageTk.PhotoImage(self.nfaimagefile)
            self.dfaimg = ImageTk.PhotoImage(self.dfaimagefile)
            self.mindfaimg = ImageTk.PhotoImage(self.mindfaimagefile)

    def display_automata(self):
        for item in self.canvasitems:
            self.automataCanvas.delete(item)
        if self.selectedButton == 0:
            header = "Эпсилон-NFA"
            automata = self.nfa
            if self.dotFound:
                image = self.nfaimg
                imagefile = self.nfaimagefile
        elif self.selectedButton == 1:
            header = "DFA"
            automata = self.dfa
            if self.dotFound:
                image = self.dfaimg
                imagefile = self.dfaimagefile
        elif self.selectedButton == 2:
            header = "Минимизированный DFA"
            automata = self.minDFA
            if self.dotFound:
                image = self.mindfaimg
                imagefile = self.mindfaimagefile
        font = tkFont.Font(family="times", size=20)
        (w, h) = (font.measure(header), font.metrics("linespace"))
        headerheight = h + 10
        itd = self.automataCanvas.create_text(10, 10, text=header, font=font, anchor=NW)
        self.canvasitems.append(itd)
        [text, linecount] = automata.get_print_text()
        font = tkFont.Font(family="times", size=13)
        (w, h) = (font.measure(text), font.metrics("linespace"))
        textheight = headerheight + linecount * h + 20
        itd = self.automataCanvas.create_text(10, headerheight + 10, text=text, font=font, anchor=NW)
        self.canvasitems.append(itd)
        if self.dotFound:
            itd = self.automataCanvas.create_image(10, textheight, image=image, anchor=NW)
            self.canvasitems.append(itd)
            totalwidth = imagefile.size[0] + 10
            totalheight = imagefile.size[1] + textheight + 10
        else:
            totalwidth = self.cwidth + 10
            totalheight = textheight + 10
        if totalheight < self.cheight:
            totalheight = self.cheight
        if totalwidth < self.cwidth:
            totalwidth = self.cwidth
        self.automataCanvas.config(scrollregion=(0, 0, totalwidth, totalheight))


def main():
    global dotFound
    root = Tk()
    app = AutomataGUI(root, dotFound)
    root.mainloop()


if __name__ == '__main__':
    main()
