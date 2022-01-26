# coding=UTF-8

from os import popen


class Automata:
    """Базовый класс для конечного автомата"""

    def __init__(self, language=set(['0', '1'])):
        self.states = set()
        self.startstate = None
        self.finalstates = []
        self.transitions = dict()
        self.language = language

    @staticmethod
    def epsilon():
        return ":e:"

    def set_start_state(self, state):
        self.startstate = state
        self.states.add(state)

    def add_final_states(self, state):
        if isinstance(state, int):
            state = [state]
        for s in state:
            if s not in self.finalstates:
                self.finalstates.append(s)

    def add_transition(self, fromstate, tostate, input):
        if isinstance(input, str):
            input = set([input])
        self.states.add(fromstate)
        self.states.add(tostate)
        if fromstate in self.transitions:
            if tostate in self.transitions[fromstate]:
                self.transitions[fromstate][tostate] = self.transitions[fromstate][tostate].union(input)
            else:
                self.transitions[fromstate][tostate] = input
        else:
            self.transitions[fromstate] = {tostate: input}

    def add_transition_dict(self, transitions):
        for fromstate, tostates in transitions.items():
            for state in tostates:
                self.add_transition(fromstate, state, tostates[state])

    def get_transitions(self, state, key):
        if isinstance(state, int):
            state = [state]
        trstates = set()
        for st in state:
            if st in self.transitions:
                for tns in self.transitions[st]:
                    if key in self.transitions[st][tns]:
                        trstates.add(tns)
        return trstates

    def get_e_close(self, findstate):
        allstates = set()
        states = set([findstate])
        while len(states) != 0:
            state = states.pop()
            allstates.add(state)
            if state in self.transitions:
                for tns in self.transitions[state]:
                    if Automata.epsilon() in self.transitions[state][tns] and tns not in allstates:
                        states.add(tns)
        return allstates

    def display(self):
        print("Состояния:", self.states)
        print("Начальное состояние: ", self.startstate)
        print("Финальные состояния: ", self.finalstates)
        print("Переходы: ")
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                for char in tostates[state]:
                    print
                    "  ", fromstate, "->", state, "on '" + char + "'",
            print

    def get_print_text(self):
        text = "Язык: {" + ", ".join(self.language) + "}\n"
        text += "Состояния: {" + ", ".join(map(str, self.states)) + "}\n"
        text += "Начальное состояние: " + str(self.startstate) + "\n"
        text += "Окончательные состояния: {" + ", ".join(map(str, self.finalstates)) + "}\n"
        text += "Переходы состояний:\n"
        linecount = 5
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                for char in tostates[state]:
                    text += "    " + str(fromstate) + " -> " + str(state) + " на '" + char + "'\n"
                    linecount += 1
        return [text, linecount]

    def new_build_from_number(self, startnum):
        translations = {}
        for i in list(self.states):
            translations[i] = startnum
            startnum += 1
        rebuild = Automata(self.language)
        rebuild.set_start_state(translations[self.startstate])
        rebuild.add_final_states(translations[self.finalstates[0]])
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                rebuild.add_transition(translations[fromstate], translations[state], tostates[state])
        return [rebuild, startnum]

    def new_build_from_equivalent_states(self, equivalent, pos):
        rebuild = Automata(self.language)
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                rebuild.add_transition(pos[fromstate], pos[state], tostates[state])
        rebuild.set_start_state(pos[self.startstate])
        for s in self.finalstates:
            rebuild.add_final_states(pos[s])
        return rebuild

    def get_dot_file(self):
        dotFile = "digraph DFA {\nrankdir=LR\n"
        if len(self.states) != 0:
            dotFile += "root=s1\nstart [shape=point]\nstart->s%d\n" % self.startstate
            for state in self.states:
                if state in self.finalstates:
                    dotFile += "s%d [shape=doublecircle]\n" % state
                else:
                    dotFile += "s%d [shape=circle]\n" % state
            for fromstate, tostates in self.transitions.items():
                for state in tostates:
                    for char in tostates[state]:
                        dotFile += 's%d->s%d [label="%s"]\n' % (fromstate, state, char)
        dotFile += "}"
        return dotFile


class BuildAutomata:
    """Класс для инициализации эпсилон-NFA автомата"""

    @staticmethod
    def basic_struct(inp):
        state1 = 1
        state2 = 2
        basic = Automata()
        basic.set_start_state(state1)
        basic.add_final_states(state2)
        basic.add_transition(1, 2, inp)
        return basic

    @staticmethod
    def plus_struct(a, b):
        [a, m1] = a.new_build_from_number(2)
        [b, m2] = b.new_build_from_number(m1)
        state1 = 1
        state2 = m2
        plus = Automata()
        plus.set_start_state(state1)
        plus.add_final_states(state2)
        plus.add_transition(plus.startstate, a.startstate, Automata.epsilon())
        plus.add_transition(plus.startstate, b.startstate, Automata.epsilon())
        plus.add_transition(a.finalstates[0], plus.finalstates[0], Automata.epsilon())
        plus.add_transition(b.finalstates[0], plus.finalstates[0], Automata.epsilon())
        plus.add_transition_dict(a.transitions)
        plus.add_transition_dict(b.transitions)
        return plus

    @staticmethod
    def dot_struct(a, b):
        [a, m1] = a.new_build_from_number(1)
        [b, m2] = b.new_build_from_number(m1)
        state1 = 1
        state2 = m2 - 1
        dot = Automata()
        dot.set_start_state(state1)
        dot.add_final_states(state2)
        dot.add_transition(a.finalstates[0], b.startstate, Automata.epsilon())
        dot.add_transition_dict(a.transitions)
        dot.add_transition_dict(b.transitions)
        return dot

    @staticmethod
    def star_struct(a):
        [a, m1] = a.new_build_from_number(2)
        state1 = 1
        state2 = m1
        star = Automata()
        star.set_start_state(state1)
        star.add_final_states(state2)
        star.add_transition(star.startstate, a.startstate, Automata.epsilon())
        star.add_transition(star.startstate, star.finalstates[0], Automata.epsilon())
        star.add_transition(a.finalstates[0], star.finalstates[0], Automata.epsilon())
        star.add_transition(a.finalstates[0], a.startstate, Automata.epsilon())
        star.add_transition_dict(a.transitions)
        return star


class DFAfromNFA:
    """Класс для конвертации из NFA в DFA и последующей минимизации DFA"""

    def __init__(self, nfa):
        self.build_dfa(nfa)
        self.minimise()

    def get_dfa(self):
        return self.dfa

    def get_minimised_dfa(self):
        return self.minDFA

    def display_dfa(self):
        self.dfa.display()

    def display_minimised_dfa(self):
        self.minDFA.display()

    def build_dfa(self, nfa):
        allstates = dict()
        eclose = dict()
        count = 1
        state1 = nfa.get_e_close(nfa.startstate)
        eclose[nfa.startstate] = state1
        dfa = Automata(nfa.language)
        dfa.set_start_state(count)
        states = [[state1, count]]
        allstates[count] = state1
        count += 1
        while len(states) != 0:
            [state, fromindex] = states.pop()
            for char in dfa.language:
                trstates = nfa.get_transitions(state, char)
                for s in list(trstates)[:]:
                    if s not in eclose:
                        eclose[s] = nfa.get_e_close(s)
                    trstates = trstates.union(eclose[s])
                if len(trstates) != 0:
                    if trstates not in allstates.values():
                        states.append([trstates, count])
                        allstates[count] = trstates
                        toindex = count
                        count += 1
                    else:
                        toindex = [k for k, v in allstates.iteritems() if v == trstates][0]
                    dfa.add_transition(fromindex, toindex, char)
        for value, state in allstates.iteritems():
            if nfa.finalstates[0] in state:
                dfa.add_final_states(value)
        self.dfa = dfa

    def accepts_string(self, string):
        current_state = self.dfa.startstate
        for ch in string:
            if ch == ":e:":
                continue
            st = list(self.dfa.get_transitions(current_state, ch))
            if len(st) == 0:
                return False
            current_state = st[0]
        if current_state in self.dfa.finalstates:
            return True
        return False

    """Метод минимизации DFA"""
    def minimise(self):
        states = list(self.dfa.states)
        n = len(states)
        unchecked = dict()
        count = 1
        distinguished = []
        equivalent = dict(zip(range(len(states)), [{s} for s in states]))
        pos = dict(zip(states, range(len(states))))
        for i in range(n - 1):
            for j in range(i + 1, n):
                if not ([states[i], states[j]] in distinguished or [states[j], states[i]] in distinguished):
                    eq = 1
                    toappend = []
                    for char in self.dfa.language:
                        s1 = self.dfa.get_transitions(states[i], char)
                        s2 = self.dfa.get_transitions(states[j], char)
                        if len(s1) != len(s2):
                            eq = 0
                            break
                        if len(s1) > 1:
                            raise BaseException("Обнаружено множество переходов в DFA!")
                        elif len(s1) == 0:
                            continue
                        s1 = s1.pop()
                        s2 = s2.pop()
                        if s1 != s2:
                            if [s1, s2] in distinguished or [s2, s1] in distinguished:
                                eq = 0
                                break
                            else:
                                toappend.append([s1, s2, char])
                                eq = -1
                    if eq == 0:
                        distinguished.append([states[i], states[j]])
                    elif eq == -1:
                        s = [states[i], states[j]]
                        s.extend(toappend)
                        unchecked[count] = s
                        count += 1
                    else:
                        p1 = pos[states[i]]
                        p2 = pos[states[j]]
                        if p1 != p2:
                            st = equivalent.pop(p2)
                            for s in st:
                                pos[s] = p1
                            equivalent[p1] = equivalent[p1].union(st)
        newFound = True
        while newFound and len(unchecked) > 0:
            newFound = False
            toremove = set()
            for p, pair in unchecked.items():
                for tr in pair[2:]:
                    if [tr[0], tr[1]] in distinguished or [tr[1], tr[0]] in distinguished:
                        unchecked.pop(p)
                        distinguished.append([pair[0], pair[1]])
                        newFound = True
                        break
        for pair in unchecked.values():
            p1 = pos[pair[0]]
            p2 = pos[pair[1]]
            if p1 != p2:
                st = equivalent.pop(p2)
                for s in st:
                    pos[s] = p1
                equivalent[p1] = equivalent[p1].union(st)
        if len(equivalent) == len(states):
            self.minDFA = self.dfa
        else:
            self.minDFA = self.dfa.new_build_from_equivalent_states(equivalent, pos)


class NFAfromRegex:
    """Класс для построения Эпсилон-NFA из регулярного выражения"""

    def __init__(self, regex):
        self.star = '*'
        self.plus = '+'
        self.dot = '.'
        self.openingBracket = '('
        self.closingBracket = ')'
        self.operators = [self.plus, self.dot]
        self.regex = regex
        self.alphabet = [chr(i) for i in range(65, 91)]
        self.alphabet.extend([chr(i) for i in range(97, 123)])
        self.alphabet.extend([chr(i) for i in range(48, 58)])
        self.build_nfa()

    def get_nfa(self):
        return self.nfa

    def display_nfa(self):
        self.nfa.display()

    def build_nfa(self):
        language = set()
        self.stack = []
        self.automata = []
        previous = "::e::"
        for char in self.regex:
            if char in self.alphabet:
                language.add(char)
                if previous != self.dot and (previous in self.alphabet or previous in [self.closingBracket, self.star]):
                    self.add_operator_to_stack(self.dot)
                self.automata.append(BuildAutomata.basic_struct(char))
            elif char == self.openingBracket:
                if previous != self.dot and (previous in self.alphabet or previous in [self.closingBracket, self.star]):
                    self.add_operator_to_stack(self.dot)
                self.stack.append(char)
            elif char == self.closingBracket:
                if previous in self.operators:
                    raise BaseException("Произошла ошибка на символе '%s' после символа '%s'" % (char, previous))
                while (1):
                    if len(self.stack) == 0:
                        raise BaseException("Ошибка при обработке '%s'. Стек пуст" % char)
                    o = self.stack.pop()
                    if o == self.openingBracket:
                        break
                    elif o in self.operators:
                        self.process_operator(o)
            elif char == self.star:
                if previous in self.operators or previous == self.openingBracket or previous == self.star:
                    raise BaseException("Error processing '%s' after '%s'" % (char, previous))
                self.process_operator(char)
            elif char in self.operators:
                if previous in self.operators or previous == self.openingBracket:
                    raise BaseException("Error processing '%s' after '%s'" % (char, previous))
                else:
                    self.add_operator_to_stack(char)
            else:
                raise BaseException("Символ '%s' не разрешён!" % char)
            previous = char
        while len(self.stack) != 0:
            op = self.stack.pop()
            self.process_operator(op)
        if len(self.automata) > 1:
            print(self.automata)
            raise BaseException("Не удалось обработать регулярное выражение")
        self.nfa = self.automata.pop()
        self.nfa.language = language

    def add_operator_to_stack(self, char):
        while (1):
            if len(self.stack) == 0:
                break
            top = self.stack[len(self.stack) - 1]
            if top == self.openingBracket:
                break
            if top == char or top == self.dot:
                op = self.stack.pop()
                self.process_operator(op)
            else:
                break
        self.stack.append(char)

    def process_operator(self, operator):
        if len(self.automata) == 0:
            raise BaseException("Error processing operator '%s'. Stack is empty" % operator)
        if operator == self.star:
            a = self.automata.pop()
            self.automata.append(BuildAutomata.star_struct(a))
        elif operator in self.operators:
            if len(self.automata) < 2:
                raise BaseException("Error processing operator '%s'. Inadequate operands" % operator)
            a = self.automata.pop()
            b = self.automata.pop()
            if operator == self.plus:
                self.automata.append(BuildAutomata.plus_struct(b, a))
            elif operator == self.dot:
                self.automata.append(BuildAutomata.dot_struct(b, a))


def draw_graph(automata, file=""):
    f = popen(r"dot -Tpng -o graph%s.png" % file, 'w')
    try:
        f.write(automata.get_dot_file())
    except:
        raise BaseException("Произошла ошибка при генерации изображения")
    finally:
        f.close()


def is_installed(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program) or is_exe(program + ".exe"):
            return True
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file) or is_exe(exe_file + ".exe"):
                return True
    return False
