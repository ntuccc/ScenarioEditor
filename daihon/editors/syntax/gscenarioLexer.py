# Generated from gscenario.g4 by ANTLR 4.9
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\6")
        buf.write("\25\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\3\2\3\2\3\2\3")
        buf.write("\3\3\3\3\3\3\4\3\4\3\5\3\5\2\2\6\3\3\5\4\7\5\t\6\3\2\2")
        buf.write("\2\24\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2")
        buf.write("\3\13\3\2\2\2\5\16\3\2\2\2\7\21\3\2\2\2\t\23\3\2\2\2\13")
        buf.write("\f\7/\2\2\f\r\7*\2\2\r\4\3\2\2\2\16\17\7+\2\2\17\20\7")
        buf.write("/\2\2\20\6\3\2\2\2\21\22\7\61\2\2\22\b\3\2\2\2\23\24\13")
        buf.write("\2\2\2\24\n\3\2\2\2\3\2\2")
        return buf.getvalue()


class gscenarioLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    Macro_start = 1
    Macro_end = 2
    Split = 3
    Any = 4

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'-('", "')-'", "'/'" ]

    symbolicNames = [ "<INVALID>",
            "Macro_start", "Macro_end", "Split", "Any" ]

    ruleNames = [ "Macro_start", "Macro_end", "Split", "Any" ]

    grammarFileName = "gscenario.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


