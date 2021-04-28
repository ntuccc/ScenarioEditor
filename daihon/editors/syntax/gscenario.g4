grammar gscenario;

text : plaintext? ( macro plaintext? )* ;
text_in_macro : text ( Split text )* ;
macro : Macro_start Space* text_in_macro Space* Macro_end ;
plaintext : (Any | Split | Space)+? ;
Macro_start : '-(' ;
Macro_end : ')-' ;
Split : '/' ;
Space : [ \t] ;
Any : . ;