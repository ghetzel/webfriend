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
        'unset' |
        'when'
    )
;

FlowControlWord:
    ( is_break?='break' levels=INT? | is_continue?='continue' levels=INT? )
;

Block:
    (FlowControlWord | EventHandlerBlock | LinearExecutionBlock ) ';'?
;

LinearExecutionBlock:
    ( Assignment | Directive | Expression | IfElseBlock | LoopBlock | CommandSequence )
;

Assignment:
    destinations+=Variable[','] '=' sources+=VariableOrType[',']
;

Directive:
    (
        is_unset?='unset' variables+=Variable[',']
    )
;

NumericOperator:
    (
        add='+' |
        subtract='-' |
        multiply='*' |
        divide='/' |
        modulus='%' |
        power='**'
    )
;

LogicOperator:
    (
        bitwise_and='&' |
        bitwise_or='|' |
        bitwise_not='^'
    )
;

AssignmentOperator:
    (
        plus_eq='+=' |
        minus_eq='-=' |
        multi_eq='*=' |
        div_eq='/=' |
        and_eq='&=' |
        or_eq='|='
    )
;

Operator:
    ( NumericOperator | LogicOperator | AssignmentOperator )
;

Expression:
    lhs=Variable operator=Operator rhs=VariableOrType
;

ConditionalExpression:
    negate?='not'? (
        assignment=Assignment ';' condition=ConditionalExpression |
        command=Command ( ';' condition=ConditionalExpression )? |
        lhs=VariableOrType ( operator=Operator rhs=VariableOrType )?
    )
;

IfElseBlock:
    if_expr      = IfStanza
    elseif_expr *= ElseIfStanza
    else_expr    = ElseStanza?
;

IfStanza:
    'if' expression=ConditionalExpression '{'
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
    'loop' (
        fixedlen=LoopConditionFixedLength |
        iterable=LoopConditionIterable |
        bounded=LoopConditionBounded |
        truthy=LoopConditionTruthy
    )?
    '{'
        blocks *= Block
    '}'
;

LoopConditionIterable:
    variables+=Variable[','] 'in' ( iterator=Command | iterator=Variable )
;

LoopConditionBounded:
    initial=Command ';' termination=ConditionalExpression ';' next=Command
;

LoopConditionTruthy:
    termination=ConditionalExpression
;

LoopConditionFixedLength:
    'count' count=IntOrVariable
;

IntOrVariable:
    (Variable | NUMBER)
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
    commands += Command[/;|$/]
;

Command:
    name=CommandName (
        id=CommandID options=CommandStanza? |
        options=CommandStanza
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
    name=KeyType ':' values+=VariableOrType
;

KeyType:
    ( !ReservedWord | ID | STRING )
;

VariableOrType:
    (Variable | Type)
;

ScalarType:
    ( NUMBER | BOOL | STRING )
;

Type:
    (ScalarType | Object | Array | 'null')
;

Object:
    '{'
        items *= KeyValuePair[','] ','?
    '}'
;

Array:
    '['
        values *= VariableOrType[','] ','?
    ']'
;

CommandName:
    !ReservedWord ID+['::']
;
"""
