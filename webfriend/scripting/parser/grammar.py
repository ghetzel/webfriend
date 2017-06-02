def generate_grammar(commands):
    return """
Friendscript:
    Shebang?
    blocks *= Block
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

FlowControlBlock:
    ( block=Block | 'break' levels=INT? | 'continue' )
;

LinearExecutionBlock:
    (IfElseBlock | LoopBlock | CommandSequence)
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
        blocks *= Block
    '}'
;

ElseIfStanza:
    'else' statement=IfStanza
;

ElseStanza:
    'else' '{'
        blocks *= Block
    '}'
;

LoopBlock:
    'for' (
        variables+=Variable[','] 'in' ( iterator=Variable | iterator=Command ) |
        initial=Command ';' termination=Expression ';' next=Command |
        termination=Expression
    )? '{'
        blocks *= FlowControlBlock
    '}'
;

Variable:
    ( '$'- name=VariableName | skip?='_' )
;

VariableName[noskipws]:
    /[^\\d\\W][\\w\\.]*\\b/
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
        '->' resultkey=ResultKeyType
    )?
;

ResultKeyType:
    (Variable | 'null')
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
