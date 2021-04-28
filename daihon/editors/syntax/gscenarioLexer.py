# Generated from gscenario.g4 by ANTLR 4.9
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\7")
        buf.write("\31\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\3\2\3")
        buf.write("\2\3\2\3\3\3\3\3\3\3\4\3\4\3\5\3\5\3\6\3\6\2\2\7\3\3\5")
        buf.write("\4\7\5\t\6\13\7\3\2\3\4\2\13\13\"\"\2\30\2\3\3\2\2\2\2")
        buf.write("\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\3\r\3")
        buf.write("\2\2\2\5\20\3\2\2\2\7\23\3\2\2\2\t\25\3\2\2\2\13\27\3")
        buf.write("\2\2\2\r\16\7/\2\2\16\17\7*\2\2\17\4\3\2\2\2\20\21\7+")
        buf.write("\2\2\21\22\7/\2\2\22\6\3\2\2\2\23\24\7\61\2\2\24\b\3\2")
        buf.write("\2\2\25\26\t\2\2\2\26\n\3\2\2\2\27\30\13\2\2\2\30\f\3")
        buf.write("\2\2\2\3\2\2")
        return buf.getvalue()


class gscenarioLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    Macro_start = 1
    Macro_end = 2
    Split = 3
    Space = 4
    Any = 5

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'-('", "')-'", "'/'" ]

    symbolicNames = [ "<INVALID>",
            "Macro_start", "Macro_end", "Split", "Space", "Any" ]

    ruleNames = [ "Macro_start", "Macro_end", "Split", "Space", "Any" ]

    grammarFileName = "gscenario.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


