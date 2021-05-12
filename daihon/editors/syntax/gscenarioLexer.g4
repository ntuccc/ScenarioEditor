lexer grammar gscenarioLexer;

Macro_start : '-(' -> pushMode(IN_MACRO) ;
Comment_start : '/*' -> more, pushMode(COMMENT) ;
Any : . ;

mode IN_MACRO;
Macro_start_recursive : '-(' -> type(Macro_start), pushMode(IN_MACRO) ;
Comment_start_in_macro : '/*' -> more, pushMode(COMMENT) ;
Macro_end : ')-' -> popMode ;
Split : '/' ;
Space : [ \t] ;
IN_MACRO_Any : . -> type(Any) ;

mode COMMENT;
Comment_end : '*/' -> skip, popMode ;
COMMENT_Any : . -> more ;