import pytest
from das.my_metta_lex import MettaLex

lex_test_data = """
    (: Evaluation Type)
    (: Predicate Type)
    (: Reactome Type)
    (: Concept Type)
    (: "Predicate:has_name" Predicate)
    (: "Reactome:R-HSA-164843" Reactome)
    (: "Concept:2-LTR circle formation" Concept)
    (
        Evaluation
        "Predicate:has_name"
        (
            Evaluation
            "Predicate:has_name"
            {"Reactome:R-HSA-164843" "Concept:2-LTR circle formation"}
        )
    )"""

def test_lexer():
    wrap = MettaLex()
    wrap.build()
    expected_tokens = [
        "EXPRESSION_OPENNING", 
        "TYPE_DEFINITION_MARK", 
        "EXPRESSION_NAME", 
        "BASIC_TYPE", 
        "EXPRESSION_CLOSING", 
        "EXPRESSION_OPENNING", 
        "TYPE_DEFINITION_MARK", 
        "EXPRESSION_NAME", 
        "BASIC_TYPE", 
        "EXPRESSION_CLOSING", 
        "EXPRESSION_OPENNING", 
        "TYPE_DEFINITION_MARK", 
        "EXPRESSION_NAME", 
        "BASIC_TYPE", 
        "EXPRESSION_CLOSING", 
        "EXPRESSION_OPENNING", 
        "TYPE_DEFINITION_MARK", 
        "EXPRESSION_NAME", 
        "BASIC_TYPE", 
        "EXPRESSION_CLOSING", 
        "EXPRESSION_OPENNING", 
        "TYPE_DEFINITION_MARK", 
        "ATOM_NAME", 
        "EXPRESSION_NAME", 
        "EXPRESSION_CLOSING", 
        "EXPRESSION_OPENNING", 
        "TYPE_DEFINITION_MARK", 
        "ATOM_NAME", 
        "EXPRESSION_NAME", 
        "EXPRESSION_CLOSING", 
        "EXPRESSION_OPENNING", 
        "TYPE_DEFINITION_MARK", 
        "ATOM_NAME", 
        "EXPRESSION_NAME", 
        "EXPRESSION_CLOSING", 
        "EXPRESSION_OPENNING", 
        "EXPRESSION_NAME", 
        "ATOM_NAME", 
        "EXPRESSION_OPENNING", 
        "EXPRESSION_NAME", 
        "ATOM_NAME", 
        "SET_OPENNING", 
        "ATOM_NAME", 
        "ATOM_NAME", 
        "SET_CLOSING", 
        "EXPRESSION_CLOSING", 
        "EXPRESSION_CLOSING", 
        "EOF"
    ]

    wrap.lexer.input(lex_test_data)
    for expected_token in expected_tokens:
        token = wrap.lexer.token()
        assert token.type == expected_token
    assert not wrap.lexer.token()