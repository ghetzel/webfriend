from __future__ import absolute_import

FRIENDSCRIPT_GRAMMAR = r'''
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
        'if' |
        'in' |
        'is' |
        'loop' |
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
    destinations+=Variable[','] op=AssignmentOperator sources+=Expression[',']
;

Directive:
    (
        is_unset?='unset' variables+=Variable[',']
    )
;

Operator:
    (
        power='**'      |
        multiply='*'    |
        divide='/'      |
        modulus='%'     |
        add='+'         |
        subtract='-'    |
        bitwise_and='&' |
        bitwise_or='|'  |
        bitwise_not='~' |
        bitwise_xor='^'
    )
;

AssignmentOperator:
    (
        eq='='          |
        multi_eq='*='   |
        div_eq='/='     |
        plus_eq='+='    |
        minus_eq='-='   |
        and_eq='&='     |
        or_eq='|='      |
        append='<<'
    )
;

Expression:
    lhs=ValueYielding (operator=Operator rhs=Expression)?
;

ValueYielding:
    ( Type | Variable )
;

ConditionalExpression:
    negate?='not'? (
        assignment=Assignment ';' condition=ConditionalExpression |
        command=Command ( ';' condition=ConditionalExpression )? |
        lhs=Expression operator=MatchOperator rhs=RegularExpression |
        lhs=Expression ( operator=ComparisonOperator rhs=Expression )?
    )
;

ComparisonOperator:
    ( '==' | '!=' | '>=' | '<=' | '<' | '>' | 'in' | 'not' 'in' )
;

MatchOperator:
    ( '!~' | '=~' )
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
    (
        '$'- parts+=VariableName['.'] |
        skip?='_'
    )
;

VariableName[noskipws]:
    key=/[^\d\W][\w]*\b/ ( '[' index=VariableIndex ']' )?
;

VariableIndex:
    ( Variable | INT | String )
;

EventHandlerBlock:
    'on' pattern=String? isolated?='isolated'? '{'
        blocks *= LinearExecutionBlock
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
    name=KeyType ':' values+=Expression
;

KeyType:
    ( !ReservedWord | ID | String )
;

Type:
    ( Object | Array | RegularExpression | ScalarType | Null )
;

Null:
    'null'
;

ScalarType:
    ( NUMBER | BOOL | String )
;

String[noskipws]:
    ( StringLiteral | StringInterpolated | Heredoc )
;

StringLiteral:
    /'[^\']*'/
;

StringInterpolated:
    /"[^\"]*"/
;

Heredoc:
    /begin(.|\n)*?(?!\n\s*end\s+)end/
;

RegularExpression:
    '/'- pattern=/[^\/]+/ '/' options*=/[ilmsu]/
;

Object:
    '{'
        items *= KeyValuePair[','] ','?
    '}'
;

Array:
    '['
        values *= Expression[','] ','?
    ']'
;

CommandName:
    !ReservedWord ID+['::']
;
'''
