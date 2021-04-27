# Generated from gscenario.g4 by ANTLR 4.9
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .gscenarioParser import gscenarioParser
else:
    from gscenarioParser import gscenarioParser

# This class defines a complete listener for a parse tree produced by gscenarioParser.
class gscenarioListener(ParseTreeListener):

    # Enter a parse tree produced by gscenarioParser#text.
    def enterText(self, ctx:gscenarioParser.TextContext):
        pass

    # Exit a parse tree produced by gscenarioParser#text.
    def exitText(self, ctx:gscenarioParser.TextContext):
        pass


    # Enter a parse tree produced by gscenarioParser#text_in_macro.
    def enterText_in_macro(self, ctx:gscenarioParser.Text_in_macroContext):
        pass

    # Exit a parse tree produced by gscenarioParser#text_in_macro.
    def exitText_in_macro(self, ctx:gscenarioParser.Text_in_macroContext):
        pass


    # Enter a parse tree produced by gscenarioParser#macro.
    def enterMacro(self, ctx:gscenarioParser.MacroContext):
        pass

    # Exit a parse tree produced by gscenarioParser#macro.
    def exitMacro(self, ctx:gscenarioParser.MacroContext):
        pass


    # Enter a parse tree produced by gscenarioParser#plaintext.
    def enterPlaintext(self, ctx:gscenarioParser.PlaintextContext):
        pass

    # Exit a parse tree produced by gscenarioParser#plaintext.
    def exitPlaintext(self, ctx:gscenarioParser.PlaintextContext):
        pass



del gscenarioParser