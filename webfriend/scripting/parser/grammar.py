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
        sequence=CommandSequence
    '}'
;

ElseIfStanza:
    'else' statement=IfStanza
;

ElseStanza:
    'else' '{'
        sequence = CommandSequence
    '}'
;

Variable:
    '$'- name=ID
;

OutputVariable:
    ( Variable | STRING )
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
        '->' resultkey=OutputVariable
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
    name=ID ':' values += Type
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
