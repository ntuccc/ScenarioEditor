grammar gscenario;

text : plaintext? ( macro plaintext? )* ;
text_in_macro : text ( Split text )* ;
macro : Macro_start text_in_macro Macro_end ;
plaintext : Any+? ;
Macro_start : '-(' ;
Macro_end : ')-' ;
Split : '/' ;
Any : . ;