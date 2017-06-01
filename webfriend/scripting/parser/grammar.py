def generate_grammar(commands):
    return """
AutomationScript:
    Shebang?
    blocks += Block
;

Shebang:
    /^#!.*$/
;

Comment:
    ( /#.*$/ )
;

Block:
    (LinearExecutionBlock | EventHandlerBlock)
;

LinearExecutionBlock:
    (IfElseBlock | CommandSequence)
;

Expression:
    negate?='not'? (
        command=Command ( ';' condition=Expression )? |
        lhs=ExpressionSegment ( operator=Operator rhs=ExpressionSegment )?
    )
;

ExpressionSegment:
    (variable=Variable | value=ScalarType)
;

IfElseBlock:
    if_expr      = IfStanza
    elseif_expr *= ElseIfStanza
    else_expr    = ElseStanza?
;

IfStanza:
    'if' expression=Expression '{'
        blocks += Block
    '}'
;

ElseIfStanza:
    'else' statement=IfStanza
;

ElseStanza:
    'else' '{'
        blocks += Block
    '}'
;

Variable:
    '$'- name=ID
;

Operator:
    ( '==' | '!=' | '<' | '>=' | '<=' | '>' | '=~' | 'in' | 'not' 'in' )
;

EventHandlerBlock:
    'on' pattern=STRING? isolated?='isolated'? '{'
        blocks += LinearExecutionBlock
    '}'
;

CommandSequence:
    commands += Command
;

Command:
    name=CommandName (
        id=CommandID options=CommandStanza? | options=CommandStanza
    )? (
        '->' resultkey=Variable
    )?
;

CommandID:
    (variable=Variable | value=ScalarType)
;

CommandStanza:
    '{'
        options *= KeyValuePair[','] ','?
    '}'
;

KeyValuePair:
    name=KeyType ':' values += Type
;

KeyType:
    ( ID | STRING )
;

ScalarType:
    ( STRING | INT | FLOAT | BOOL )
;

Type:
    (Variable | ScalarType | Object | Array | 'null')
;

Object:
    '{'
        items *= KeyValuePair[','] ','?
    '}'
;

Array:
    '['
        values *= Type[','] ','?
    ']'
;

CommandName:
    (\n        """ + ' | \n        '.join(["'{}'".format(c) for c in commands]) + """\n    )
;
"""
