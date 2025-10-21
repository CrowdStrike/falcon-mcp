# Operators | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-operators.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

## Operators

The documentation covers LogScale operators and their usage in comparing field values across strings, numbers, and regular expressions, including detailed explanations of string comparison operators (=, !=, like), numeric operators (<, >, =, etc.), and logical operators (and, or, not). The guide also explains how operators interact with tag fields, provides examples of combining filters with Boolean operators, and demonstrates how to negate filter function expressions for more efficient querying. 

Operators allow for comparisons on field values. Comparison operators work on strings, numbers, or regular expressions. 

When using operators: 

  * The left-hand-side of the operator is interpreted as a field name. If you write `200 = statuscode`, LogScale tries to find a field named `200` and test if its value is `statuscode`. The value must much exactly, including the case. 

  * For more flexibility with filtering, use the [`wildcard()`](functions-wildcard.html "wildcard\(\)") function. 

  * If the specified field is not present in an event, then the comparison always fails — unless it is `!=`. You can use this behavior to match events that do not have a given field, using either `not (foo = *)` or the equivalent `foo != *` to find events that do not have the field `foo`. 

  * To compare two fields, rather than a field and a value, use the [`test()`](functions-test.html "test\(\)") function. When using [`test()`](functions-test.html "test\(\)") to care to quote the field and values correction using double quotes to select what is a field and what is a value. 

The [`test()`](functions-test.html "test\(\)") function uses eval expression syntax that is also available in other functions, including [`eval()`](functions-eval.html "eval\(\)"), [`if()`](functions-if.html "if\(\)"), and [`coalesce()`](functions-coalesce.html "coalesce\(\)"). Also, in the evaluated short hand: 

logscale Syntax
        
        field := evalExpression.

For more information on eval syntax, see [Expressions](syntax-expressions.html "Expressions"). 




### Comparison Operators on Strings

For string operators, the syntax assumes the value on the right of the operator is a string. For example: 

logscale Syntax
    
    
    class like "Bucket"

The [`like`](syntax-operators.html#syntax-operators-string-comparison "Comparison Operators on Strings") operator also supports wildcards, so: 

logscale Syntax
    
    
    class like "foo*bar"

Will find entries that begin with `foo` and end with `bar`. 

Operator |  Case Sensitive |  Description   
---|---|---  
[`=`](syntax-operators.html#summary_syntax-operators) |  Yes |  Field is equal to the entire declared string. Also achieveable using [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters").   
`!=` |  Yes |  Field does not equal the entire declared string. Also achieveable using [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters").   
[`like`](syntax-operators.html#syntax-operators-string-comparison "Comparison Operators on Strings") |  Yes |  Field is contains the declared string. Also achieveable using [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters").   
  
The [`like`](syntax-operators.html#syntax-operators-string-comparison "Comparison Operators on Strings") operator filters for fields containing the string, but remains case sensitive. The [`like`](syntax-operators.html#syntax-operators-string-comparison "Comparison Operators on Strings") operator query: 

logscale Syntax
    
    
    class like "Bucket"

Is therefore equivalent to: 

logscale Syntax
    
    
    class like "*Bucket*"

Is therefore equivalent to: 

logscale Syntax
    
    
    class = *Bucket*

Or 

logscale Syntax
    
    
    class like /Bucket/

Or 

logscale Syntax
    
    
    class = /Bucket/

### Comparison Operators on Numbers

Numerical operators can be used to filter on a numerical value. The LogScale will attempt to convert the value to a number before comparison, reporting an error if the value cannot be converted. To compare two numerical values, use the [`test()`](functions-test.html "test\(\)"). For example: 

logscale Syntax
    
    
    statuscode = "404"

If statuscode is a numeric value, the string will be converted to a number before comparison. 

Query |  Description   
---|---  
`statuscode < 400` |  Less than   
`statuscode <= 400` |  Less than or equal to   
`statuscode = 400` |  Equal to   
`statuscode != 400` |  Not equal to   
`statuscode >= 400` |  Greater than or equal to   
`statuscode > 400` |  Greater than   
`400 = statuscode` |  The field 400 is equal to `statuscode`.   
`400 > statuscode` |  This comparison generates an error. You can only perform a comparison between numbers. In this example, `statuscode` is not a number, and `400` is the name of a field.   
  
#### Filtering on Tag Fields

Tag fields are used to define the datasources for a given event, and have an impact on the storage and performance of queries. For more information, see [Datasources](https://library.humio.com/logscale-architecture/training-arch-op-datasources.html). When filtering on a tag field, filters behave in the same way as regular [Query Filters](syntax-filters.html "Query Filters"). This is recommended to decrease the query time by reducing the amount of data to be searched. 

Due to the performance implications, filtering on tag fields should be placed first in the query to query the data. For more information on running queries and selecting fields for filtering, see [Multi-line queries](writing-queries-usage-best-practice.html#writing-queries-usage-best-practice-multiline "Multi-line queries") ). 

See the [Parsing Event Tags](parsers-tagging.html "Parsing Event Tags") documentation for more on tags. 

### Logical Operators

You can combine filters using the `and`, `or`, `not` Boolean operators, and group them with parentheses. `!` can also be used as an alternative to unary `not`. 

### Important

In CQL, `OR` binds closer than `AND` in queries. This is different to most other programming languages and environments, but has been designed to aid the execution of queries where filtering (i.e. selecting between values) is the primary activity. 

Examples 

Query |  Description   
---|---  
`foo and user=bar` |  Match events with `foo` in any field and a user field matching `bar`.   
`foo bar` |  Since the `and` operator is implicit, you do not need to include it in this simple type of query.   
`statuscode=404 and (method=GET or method=POST)` |  Match events with `404` in their `statuscode` field, and either `GET` or `POST` in their `method` field.   
`foo not bar` |  This query is equivalent to the query `foo` and (`not bar`).   
`!bar` |  This query is equivalent to the query `not bar`.   
`not foo bar` |  This query is equivalent to the query (not foo) and bar. This is because the `not` operator has a higher priority than `and` and `or`.   
`foo and not bar or baz` |  This query is equivalent to the query `foo and ((not bar) or baz)`  
`foo or not bar and baz` |  This query is equivalent to the query `(foo or (not bar)) and baz`.   
`foo not statuscode=200` |  This query is equivalent to the query `foo and statuscode!=200`.   
  
### Negating the Result of Filter Functions

The `not` and `!` operators can also be used to negate filter function expressions, which is syntactically more clean than passing in an explicit `negate=true` argument. Examples of this are 

logscale Syntax
    
    
    ...
    | !cidr(ip, subnet="127.0.0/16")
    | ...
    ...
    | !in(field, values=[a, b, c])
    | ...
    ...
    | !regex("xxx")
    | ...
