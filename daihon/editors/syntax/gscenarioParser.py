# Generated from gscenario.g4 by ANTLR 4.9
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\t")
        buf.write("\64\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\3\2\5\2\f\n\2\3\2")
        buf.write("\3\2\5\2\20\n\2\7\2\22\n\2\f\2\16\2\25\13\2\3\3\3\3\3")
        buf.write("\3\7\3\32\n\3\f\3\16\3\35\13\3\3\4\3\4\7\4!\n\4\f\4\16")
        buf.write("\4$\13\4\3\4\3\4\7\4(\n\4\f\4\16\4+\13\4\3\4\3\4\3\5\6")
        buf.write("\5\60\n\5\r\5\16\5\61\3\5\3\61\2\6\2\4\6\b\2\3\4\2\4\4")
        buf.write("\7\7\2\66\2\13\3\2\2\2\4\26\3\2\2\2\6\36\3\2\2\2\b/\3")
        buf.write("\2\2\2\n\f\5\b\5\2\13\n\3\2\2\2\13\f\3\2\2\2\f\23\3\2")
        buf.write("\2\2\r\17\5\6\4\2\16\20\5\b\5\2\17\16\3\2\2\2\17\20\3")
        buf.write("\2\2\2\20\22\3\2\2\2\21\r\3\2\2\2\22\25\3\2\2\2\23\21")
        buf.write("\3\2\2\2\23\24\3\2\2\2\24\3\3\2\2\2\25\23\3\2\2\2\26\33")
        buf.write("\5\2\2\2\27\30\7\6\2\2\30\32\5\2\2\2\31\27\3\2\2\2\32")
        buf.write("\35\3\2\2\2\33\31\3\2\2\2\33\34\3\2\2\2\34\5\3\2\2\2\35")
        buf.write("\33\3\2\2\2\36\"\7\3\2\2\37!\7\7\2\2 \37\3\2\2\2!$\3\2")
        buf.write("\2\2\" \3\2\2\2\"#\3\2\2\2#%\3\2\2\2$\"\3\2\2\2%)\5\4")
        buf.write("\3\2&(\7\7\2\2\'&\3\2\2\2(+\3\2\2\2)\'\3\2\2\2)*\3\2\2")
        buf.write("\2*,\3\2\2\2+)\3\2\2\2,-\7\5\2\2-\7\3\2\2\2.\60\t\2\2")
        buf.write("\2/.\3\2\2\2\60\61\3\2\2\2\61\62\3\2\2\2\61/\3\2\2\2\62")
        buf.write("\t\3\2\2\2\t\13\17\23\33\")\61")
        return buf.getvalue()


class gscenarioParser ( Parser ):

    grammarFileName = "gscenario.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'-('", "<INVALID>", "')-'", "'/'", "<INVALID>", 
                     "'*/'", "'/*'" ]

    symbolicNames = [ "<INVALID>", "Macro_start", "Any", "Macro_end", "Split", 
                      "Space", "Comment_end", "Comment_start" ]

    RULE_text = 0
    RULE_text_in_macro = 1
    RULE_macro = 2
    RULE_plaintext = 3

    ruleNames =  [ "text", "text_in_macro", "macro", "plaintext" ]

    EOF = Token.EOF
    Macro_start=1
    Any=2
    Macro_end=3
    Split=4
    Space=5
    Comment_end=6
    Comment_start=7

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class TextContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def plaintext(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(gscenarioParser.PlaintextContext)
            else:
                return self.getTypedRuleContext(gscenarioParser.PlaintextContext,i)


        def macro(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(gscenarioParser.MacroContext)
            else:
                return self.getTypedRuleContext(gscenarioParser.MacroContext,i)


        def getRuleIndex(self):
            return gscenarioParser.RULE_text

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitText" ):
                return visitor.visitText(self)
            else:
                return visitor.visitChildren(self)




    def text(self):

        localctx = gscenarioParser.TextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_text)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 9
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 8
                self.plaintext()


            self.state = 17
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==gscenarioParser.Macro_start:
                self.state = 11
                self.macro()
                self.state = 13
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                if la_ == 1:
                    self.state = 12
                    self.plaintext()


                self.state = 19
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Text_in_macroContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def text(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(gscenarioParser.TextContext)
            else:
                return self.getTypedRuleContext(gscenarioParser.TextContext,i)


        def Split(self, i:int=None):
            if i is None:
                return self.getTokens(gscenarioParser.Split)
            else:
                return self.getToken(gscenarioParser.Split, i)

        def getRuleIndex(self):
            return gscenarioParser.RULE_text_in_macro

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitText_in_macro" ):
                return visitor.visitText_in_macro(self)
            else:
                return visitor.visitChildren(self)




    def text_in_macro(self):

        localctx = gscenarioParser.Text_in_macroContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_text_in_macro)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 20
            self.text()
            self.state = 25
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==gscenarioParser.Split:
                self.state = 21
                self.match(gscenarioParser.Split)
                self.state = 22
                self.text()
                self.state = 27
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MacroContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Macro_start(self):
            return self.getToken(gscenarioParser.Macro_start, 0)

        def text_in_macro(self):
            return self.getTypedRuleContext(gscenarioParser.Text_in_macroContext,0)


        def Macro_end(self):
            return self.getToken(gscenarioParser.Macro_end, 0)

        def Space(self, i:int=None):
            if i is None:
                return self.getTokens(gscenarioParser.Space)
            else:
                return self.getToken(gscenarioParser.Space, i)

        def getRuleIndex(self):
            return gscenarioParser.RULE_macro

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMacro" ):
                return visitor.visitMacro(self)
            else:
                return visitor.visitChildren(self)




    def macro(self):

        localctx = gscenarioParser.MacroContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_macro)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 28
            self.match(gscenarioParser.Macro_start)
            self.state = 32
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,4,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 29
                    self.match(gscenarioParser.Space) 
                self.state = 34
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

            self.state = 35
            self.text_in_macro()
            self.state = 39
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==gscenarioParser.Space:
                self.state = 36
                self.match(gscenarioParser.Space)
                self.state = 41
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 42
            self.match(gscenarioParser.Macro_end)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PlaintextContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Any(self, i:int=None):
            if i is None:
                return self.getTokens(gscenarioParser.Any)
            else:
                return self.getToken(gscenarioParser.Any, i)

        def Space(self, i:int=None):
            if i is None:
                return self.getTokens(gscenarioParser.Space)
            else:
                return self.getToken(gscenarioParser.Space, i)

        def getRuleIndex(self):
            return gscenarioParser.RULE_plaintext

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPlaintext" ):
                return visitor.visitPlaintext(self)
            else:
                return visitor.visitChildren(self)




    def plaintext(self):

        localctx = gscenarioParser.PlaintextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_plaintext)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45 
            self._errHandler.sync(self)
            _alt = 1+1
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1+1:
                    self.state = 44
                    _la = self._input.LA(1)
                    if not(_la==gscenarioParser.Any or _la==gscenarioParser.Space):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 47 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





