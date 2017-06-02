def generate_grammar():
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

ReservedWord:
    (
        'as' |
        'break' |
        'case' |
        'continue' |
        'else' |
        'for' |
        'if' |
        'in' |
        'is' |
        'not' |
        'on' |
        'when'
    )
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
        command=Command ( ';'? condition=Expression )? |
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
        fixedlen=LoopConditionFixedLength |
        iterable=LoopConditionIterable |
        bounded=LoopConditionBounded |
        whiletrue=LoopConditionWhile
    )?
    '{'
        blocks *= FlowControlBlock
    '}'
;

LoopConditionIterable:
    variables+=Variable[','] 'in' ( iterator=Command | iterator=Variable )
;

LoopConditionBounded:
    initial=Command ';' termination=Expression ';' next=Command
;

LoopConditionWhile:
    termination=Expression
;

LoopConditionFixedLength:
    count=IntOrVariable 'times'
;

IntOrVariable:
    (Variable | INT)
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
        id=CommandID options=CommandStanza? |
        options=CommandStanza
    )? (
        '->' resultkey=ResultKeyType
    )? ';'?
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
    ( !ReservedWord | ID | STRING )
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
    !ReservedWord ID+['::']
;
"""
