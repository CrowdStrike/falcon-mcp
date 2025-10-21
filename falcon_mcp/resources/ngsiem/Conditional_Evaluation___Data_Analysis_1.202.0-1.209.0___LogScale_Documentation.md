# Conditional Evaluation | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-conditional.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

## Conditional Evaluation

LogScale provides conditional evaluation capabilities through Case Statements and Match Statements, allowing developers to define alternative flows and handle different scenarios in their queries. Case Statements enable multiple test expressions with corresponding results using a semicolon-separated clause structure, while Match Statements offer a switch-like operation that checks conditions against the same field using filters and regular expressions, both supporting default/wildcard clauses for handling unmatched events. 

In LogScale the streaming style is not well-suited for procedural-style conditions. However, there are a few ways to do conditional evaluation: 

  * [Case Statements](syntax-conditional.html#syntax-conditional-case "Case Statements")

  * [Match Statements](syntax-conditional.html#syntax-conditional-match "Match Statements")




### Case Statements

Using [`case`](syntax-conditional.html#syntax-conditional-case "Case Statements") statements, you can define alternative flows in your queries. It is similar to [`case`](syntax-conditional.html#syntax-conditional-case "Case Statements") or `cond` you might know from many other functional programming languages. 

The syntax looks like this: 

logscale Syntax
    
    
    case {
      pipeline1
    | ... ;
      pipeline2
    | ... ;
      pipeline3
    | ... ;
      *
    | ...
    }

Each clause in the pipeline is terminated by a semicolon. For each clause within the [`case`](syntax-conditional.html#syntax-conditional-case "Case Statements") statement, if the expression for this clause returns events, then the clause is considered to have matched. 

Typically, each clause takes the form of one or more test expressions followed by one or more results. For example, a single test and result: 

logscale
    
    
    src="client-side"
    | type:="client"

The first statement tests for a field value, the second creates a new field. 

OR for a multiple statement test: 

logscale
    
    
    src="client-side"
    | ip != "127.0.0.1" 
    | type:="local"

In this example we are testing both the field src and ip. 

The pipeline is considered to have matched if the pipeline returns events. If the test returns true and a value is set, then the clause has matched. If no clauses match, then events are dropped. 

You can add a wildcard or default clause that will be used if no other clauses match by using an asterisk in the pipeline: 

logscale Syntax
    
    
    case { ... ;
    *
    | DEFAULT }

The default matches all events in the "default case", performing similar to the `else` part of an if-statement. If you do not add a wildcard clause, any events that do not match any of the explicit clauses will be dropped. 

#### Conditional Case Example

Let's say we have logs from multiple sources that all have a field named `time`, and we want to group those hosts by a type identifying what host group to produce percentiles of the time fields, but one for each kind of source. 

First, we try to match some text that distinguishes the different types of line. Then we can create a new field `type` and assign a value that we can use to group by. 

logscale
    
    
    time=*
    | case { 
      src="client-side"
    | type := "client";
      src="frontend-server"
    | ip != 192.168.1.1
    | type := "frontend";
    *
    | type := "server"
    }
    | groupBy(type, function=percentile(time))

Within the [`case`](syntax-conditional.html#syntax-conditional-case "Case Statements") statement, there are three separate clauses: 

  * logscale Syntax
        
        src="client-side"
        | type := "client";

When the src field contains `client-side`, set the type field to `client`. 

  * logscale Syntax
        
        src="frontend-server"
        | ip != 192.168.1.1
        | type := "frontend";

When the src field contains `frontend-server` and provided that the ip is not `192.168.1.1`, set the type field to `frontend`. 

  * logscale Syntax
        
        *
        | type := "server"

If no other clause matches, set type to `server`. 




#### Catch-All Clause

The `*` clause captures any output that has not matched a previous clause, and can be used either to ignore that information (resulting in no action or output) or to apply a default operation or value. For example, in the sample below the `client` field is being used to determine whether the IP address is `localhost` and setting the `local` field accordingly: 

logscale
    
    
    case { client = "::1"
    | local := "true";
           client = "127.0.0.1"
    | local := "true";
           *
    | local := "false"}

The `*` clause in this instance sets `local` to `false` for any non-matching value. 

However, the following is also valid: 

logscale
    
    
    case { client = "::1"
    | local := "true";
           client = "127.0.0.1"
    | local := "true";
           * }

The above ensures that the non-matching clauses are not processed, but does not create the field unless we have identified a local value. 

The following example demonstrates a base match and default response example when looking at the Event_SimpleName field: 

logscale
    
    
    Event_SimpleName match{
    /.*Network.*/ => network_tag := "Network";
    * => new_tag := "Other"}

### Match Statements

If you are looking for the [`match()`](functions-match.html "match\(\)") function, see [`match()`](functions-match.html "match\(\)")

Using `match` statements, you can describe alternative flows in your queries where the conditions all check the same field. It is similar to the `switch` operation you might recognize from many other programming languages. The matches on the field support the filters listed in [Field Filters](syntax-filters.html#syntax-filters-field "Field Filters") and in [Regular Expression Filters](syntax-filters.html#syntax-filters-regex "Regular Expression Filters"). 

The syntax looks like this: 

logscale Syntax
    
    
    field match {
      value => expression
    | expression... ;
      /regex/ => expression
    | ...;
      * => expression
    | ...
    }

You write a sequence of filter and pipeline clauses to run when the filter matches, separated by a semicolon (`;`). LogScale will apply each clause from top to bottom until one returns a value (matches the input). 

You can use some functions as selectors (in addition to string patterns). More specifically, those functions which test a single field (and do not transform the event). 

You can add a wildcard clause `match { ... ; * => * }` which matches all events as the "default case", essentially the `else` part of an `if-` statement. If you do not add a wildcard clause, then any events that do not match any of the explicit clauses will be dropped. You cannot use the empty clause — you must explicitly write `*` to match all. 

As opposed to how a regular field test would work — where `x=*` checks for existence and `x=true` checks that `x` matches the string `true` — in the match (for case statements) the guards `*` and `true` are equivalent and matches everything. 

Because `*` no longer has the same meaning as in field tests, `x match { ** => *}` and `x match { * => *}` are not equivalent since the first checks for existence and the latter accepts everything. 

This also means that `"*"` and `*` are not equivalent either, and `"*"` and `"**"` are equivalent. 

Since, as in case statements, the guards `*` and `true` match anything, the existence of a field can be checked using a quote glob `"*"` or two consecutive globs `**`. 

The syntax looks like this: 

logscale Syntax
    
    
    field match {
      value => expression
    | expression... ;
      /regex/ => expression
    | ...;
      in(values=[1, 2, 3]) => expression
    | ...; // match if in(field=field, values=[1, 2, 3]) does
      "*" => expression
    | ...; // match if the field exists
      * => expression
    | ... // match all events
    }

`match` statements accept any "pure" [Filtering Query Functions](functions-filter.html "Filtering Query Functions") (filter functions that do not mutate) that has a _`field`_ parameter, for example: 

logscale Syntax
    
    
    x match { in(values=[5, 56, 567]) => *;}

#### Conditional Match Example

Let's say we have logs from multiple sources that all have a field that holds the time spent on some operation, but in different fields and units. We want to get percentiles of the time fields all in the same unit and in one field. 

logscale
    
    
    logtype match {
        "accesslog" => time:=response_time ;     // Access log is in seconds.
        /server_\d+/ => time:=server_time*1000 ; // These servers log in millis
      }
    | groupBy(logtype, function=percentile(time))

#### Setting a Field's Default Value

You can use the function [`default()`](functions-default.html "default\(\)") to set the value of a missing or empty field or use the function ` coalesce()` to select the first defined value from a list of expressions.
