# -*- coding: utf-8 -*-

import sys
import time

from AutomataTheory import *


def main():
    inp = "(01*1)*1"
    if len(sys.argv) > 1:
        inp = sys.argv[1]
    print("Регулярное выражение: ", inp)
    nfaObj = NFAfromRegex(inp)
    nfa = nfaObj.get_nfa()
    dfaObj = DFAfromNFA(nfa)
    dfa = dfaObj.get_dfa()
    minDFA = dfaObj.get_minimised_dfa()
    print("\nNFA: ")
    nfaObj.display_nfa()
    print("\nDFA: ")
    dfaObj.display_dfa()
    print("\nМинимизированный DFA: ")
    dfaObj.display_minimised_dfa()
    if is_installed("dot"):
        draw_graph(dfa, "dfa")
        draw_graph(nfa, "nfa")
        draw_graph(minDFA, "mdfa")
        print("\nГрафики были построены в папке проекта")
        print()
        minDFA.get_dot_file()


if __name__ == '__main__':
    t = time.time()
    try:
        main()
    except BaseException as e:
        print("\nОшибка:", e)
    print("\nВремя выполнения: ", time.time() - t, "секунд")
