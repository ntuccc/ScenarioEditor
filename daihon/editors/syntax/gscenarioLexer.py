# Generated from gscenarioLexer.g4 by ANTLR 4.9
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\t")
        buf.write("K\b\1\b\1\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6")
        buf.write("\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\3\2")
        buf.write("\3\2\3\2\3\2\3\2\3\3\3\3\3\3\3\3\3\3\3\3\3\4\3\4\3\5\3")
        buf.write("\5\3\5\3\5\3\5\3\5\3\6\3\6\3\6\3\6\3\6\3\6\3\7\3\7\3\7")
        buf.write("\3\7\3\7\3\b\3\b\3\t\3\t\3\n\3\n\3\n\3\n\3\13\3\13\3\13")
        buf.write("\3\13\3\13\3\13\3\f\3\f\3\f\3\f\2\2\r\5\3\7\t\t\4\13\2")
        buf.write("\r\2\17\5\21\6\23\7\25\2\27\b\31\2\5\2\3\4\3\4\2\13\13")
        buf.write("\"\"\2H\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\3\13\3\2\2")
        buf.write("\2\3\r\3\2\2\2\3\17\3\2\2\2\3\21\3\2\2\2\3\23\3\2\2\2")
        buf.write("\3\25\3\2\2\2\4\27\3\2\2\2\4\31\3\2\2\2\5\33\3\2\2\2\7")
        buf.write(" \3\2\2\2\t&\3\2\2\2\13(\3\2\2\2\r.\3\2\2\2\17\64\3\2")
        buf.write("\2\2\219\3\2\2\2\23;\3\2\2\2\25=\3\2\2\2\27A\3\2\2\2\31")
        buf.write("G\3\2\2\2\33\34\7/\2\2\34\35\7*\2\2\35\36\3\2\2\2\36\37")
        buf.write("\b\2\2\2\37\6\3\2\2\2 !\7\61\2\2!\"\7,\2\2\"#\3\2\2\2")
        buf.write("#$\b\3\3\2$%\b\3\4\2%\b\3\2\2\2&\'\13\2\2\2\'\n\3\2\2")
        buf.write("\2()\7/\2\2)*\7*\2\2*+\3\2\2\2+,\b\5\5\2,-\b\5\2\2-\f")
        buf.write("\3\2\2\2./\7\61\2\2/\60\7,\2\2\60\61\3\2\2\2\61\62\b\6")
        buf.write("\3\2\62\63\b\6\4\2\63\16\3\2\2\2\64\65\7+\2\2\65\66\7")
        buf.write("/\2\2\66\67\3\2\2\2\678\b\7\6\28\20\3\2\2\29:\7\61\2\2")
        buf.write(":\22\3\2\2\2;<\t\2\2\2<\24\3\2\2\2=>\13\2\2\2>?\3\2\2")
        buf.write("\2?@\b\n\7\2@\26\3\2\2\2AB\7,\2\2BC\7\61\2\2CD\3\2\2\2")
        buf.write("DE\b\13\b\2EF\b\13\6\2F\30\3\2\2\2GH\13\2\2\2HI\3\2\2")
        buf.write("\2IJ\b\f\3\2J\32\3\2\2\2\5\2\3\4\t\7\3\2\5\2\2\7\4\2\t")
        buf.write("\3\2\6\2\2\t\4\2\b\2\2")
        return buf.getvalue()


class gscenarioLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    IN_MACRO = 1
    COMMENT = 2

    Macro_start = 1
    Any = 2
    Macro_end = 3
    Split = 4
    Space = 5
    Comment_end = 6
    Comment_start = 7

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE", "IN_MACRO", "COMMENT" ]

    literalNames = [ "<INVALID>",
            "'-('", "')-'", "'/'", "'*/'" ]

    symbolicNames = [ "<INVALID>",
            "Macro_start", "Any", "Macro_end", "Split", "Space", "Comment_end", 
            "Comment_start" ]

    ruleNames = [ "Macro_start", "Comment_start", "Any", "Macro_start_recursive", 
                  "Comment_start_in_macro", "Macro_end", "Split", "Space", 
                  "IN_MACRO_Any", "Comment_end", "COMMENT_Any" ]

    grammarFileName = "gscenarioLexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


