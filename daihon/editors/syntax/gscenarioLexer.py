# Generated from gscenarioLexer.g4 by ANTLR 4.9
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\7")
        buf.write(",\b\1\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\3\2\3\2\3\2\3\2\3\2\3\3\3\3\3\4\3\4\3\4\3")
        buf.write("\4\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3\6\3\6\3\7\3\7\3\b\3\b")
        buf.write("\3\b\3\b\2\2\t\4\3\6\4\b\2\n\5\f\6\16\7\20\2\4\2\3\3\4")
        buf.write("\2\13\13\"\"\2*\2\4\3\2\2\2\2\6\3\2\2\2\3\b\3\2\2\2\3")
        buf.write("\n\3\2\2\2\3\f\3\2\2\2\3\16\3\2\2\2\3\20\3\2\2\2\4\22")
        buf.write("\3\2\2\2\6\27\3\2\2\2\b\31\3\2\2\2\n\37\3\2\2\2\f$\3\2")
        buf.write("\2\2\16&\3\2\2\2\20(\3\2\2\2\22\23\7/\2\2\23\24\7*\2\2")
        buf.write("\24\25\3\2\2\2\25\26\b\2\2\2\26\5\3\2\2\2\27\30\13\2\2")
        buf.write("\2\30\7\3\2\2\2\31\32\7/\2\2\32\33\7*\2\2\33\34\3\2\2")
        buf.write("\2\34\35\b\4\3\2\35\36\b\4\2\2\36\t\3\2\2\2\37 \7+\2\2")
        buf.write(" !\7/\2\2!\"\3\2\2\2\"#\b\5\4\2#\13\3\2\2\2$%\7\61\2\2")
        buf.write("%\r\3\2\2\2&\'\t\2\2\2\'\17\3\2\2\2()\13\2\2\2)*\3\2\2")
        buf.write("\2*+\b\b\5\2+\21\3\2\2\2\4\2\3\6\7\3\2\t\3\2\6\2\2\t\4")
        buf.write("\2")
        return buf.getvalue()


class gscenarioLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    IN_MACRO = 1

    Macro_start = 1
    Any = 2
    Macro_end = 3
    Split = 4
    Space = 5

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE", "IN_MACRO" ]

    literalNames = [ "<INVALID>",
            "'-('", "')-'", "'/'" ]

    symbolicNames = [ "<INVALID>",
            "Macro_start", "Any", "Macro_end", "Split", "Space" ]

    ruleNames = [ "Macro_start", "Any", "Macro_start_recursive", "Macro_end", 
                  "Split", "Space", "IN_MACRO_Any" ]

    grammarFileName = "gscenarioLexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


