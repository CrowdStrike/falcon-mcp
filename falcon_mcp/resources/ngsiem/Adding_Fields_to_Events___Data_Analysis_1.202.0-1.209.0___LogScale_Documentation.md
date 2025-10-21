# Adding Fields to Events | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

## Adding Fields to Events

The documentation explains how to add new fields in LogScale through two primary methods: regular expression-based field extraction and function-based field creation using 'as' parameters. Additional topics covered include eval syntax for numeric computations, assignment operators for simplified field creation, and field operators for filtering specific fields with functions, providing users with comprehensive options for field manipulation and data processing. 

New fields can be created in two ways: 

  * [Regular Expression-based Field Extraction](syntax-fields.html#syntax-fields-extracting "Regular Expression-based Field Extraction")

  * [_`as`_ Parameters](syntax-fields.html#syntax-fields-from-functions "as Parameters")




### Regular Expression-based Field Extraction

You can extract new fields from your text data using regular expressions and then test their values. This lets you access data that LogScale did not parse when it indexed the data. 

For example, if your log entries contain text such as `... disk_free=2000 ...`, then you can use a query like the following to find the entries that have less than 1000 free disk space. 

logscale
    
    
    regex("disk_free=(?<space>[0-9]+)")
    | space < 1000

The first line uses regular expressions to extract the value after the equals sign and assign it to the field space, and then filter the events where the extracted field is greater than `1000`. 

The named capturing groups (`(?<FIELDNAME>)` are used to extract fields in regular expressions. This combines two principles, the usage of grouping in regular expressions using `()`, and explicit field creation. 

The same result can be obtained written using the regex literal syntax: 

logscale
    
    
    @rawstring=/disk_free=(?<space>[0-9]+)/
    | space < 1000

You can apply repeat to field extraction to yield one event for each match of the regular expression. This allows processing multiple values for a named field, or a field name that matches a pattern, as in this example: 

logscale
    
    
    regex("value[^=]*=(?<someBar>\\S+)", repeat=true)
    | groupBy(someBar)

On an input event with a field value of: 

accesslog
    
    
    type=foo value=bar1 valueExtra=bar2 value=bar3

the [`groupBy()`](functions-groupby.html "groupBy\(\)") sees all three bar values. 

### Warning

In order to use field-extraction this way, the regular expression must be a top-level expression, that is, `|` between bars `|`. The following query does not work: 

Invalid Example for Demonstration - DO NOT USE 

logscale
    
    
    // DON'T DO THIS - THIS DOES NOT WORK
    type=FOO or /disk_free=(?<space>[0-9]+)/
    | space < 1000

### Note

Since regular expressions require additional processing, it is recommended to do as much simple filtering (text or field matching) as possible earlier in the query chain before applying the regular expression function. 

### [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") Parameters

Fields can also be added by functions. Most functions set their result in a field that has the function name prefixed with a _ by default. For example the [`count()`](functions-count.html "count\(\)") puts its result in a field _count. 

Most functions that produce fields have a parameter called `as`. By setting this parameter you can specify the name of the output field, for example: 

logscale
    
    
    count(as=cnt)

Assigns the result of the [`count()`](functions-count.html "count\(\)") to the field named `cnt` (instead of the default `_count`). 

Many functions can be used to generate new fields using the [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") argument. For example [`concat()`](functions-concat.html "concat\(\)"): 

logscale
    
    
    concat([aidValue, cidValue], as=checkMe2)

Combines the aidValue and cidValue into a single string. 

The [`format()`](functions-format.html "format\(\)") can be used to format information and values into a new value, for example, formatting two fields with a comma separator for use with a table: 

logscale Syntax
    
    
    format(format="%s,%s", field=[a, b], as="combined")
    | table(combined)

See also the [Assignment Operator](syntax-fields.html#syntax-fields-assignment-operator "Assignment Operator") for shorthand syntax for assigning results to a field. 

### Eval Syntax

The function [`eval()`](functions-eval.html "eval\(\)") can assign fields while doing numeric computations on the input. 

The `:=` syntax is short for eval. Use `|` between assignments. 

logscale Syntax
    
    
    ...
    | foo := a + b
    | bar := a / b
    | ...

This is short for the following: 

logscale Syntax
    
    
    ...
    | eval(foo = a + b)
    | eval(bar = a / b)
    | ...

### Assignment Operator

You can use the operator `:=` with functions that take an `as` parameter. When what is on the right hand side of the assignment is a [Function Call](https://library.humio.com/lql-grammar/syntax-grammar-guide-subset.html#syntax-grammar-guide-subset-function-call), the assignment is rewritten to specify the `as=` argument which, by convention, is the output field name. For example: 

logscale Syntax
    
    
    ...
    | foo := min(x)
    | bar := max(x)
    | ...

The above is short for this: 

logscale Syntax
    
    
    ...
    | min(x, as=foo)
    | max(x, as=bar)
    | ...

### Field Operator

The field operator filters a specific field with any function that has the _`field`_ parameter, so that: 

logscale Syntax
    
    
    ...
    | ip_addr =~ cidr(subnet="127.0.0.1/24")
    | ...

Is synonymous with: 

logscale Syntax
    
    
    ...
    | cidr(subnet="127.0.0.1/24", field=ip_addr)
    | ...

This works with many functions, including [`regex()`](functions-regex.html "regex\(\)") and [`replace()`](functions-replace.html "replace\(\)").
