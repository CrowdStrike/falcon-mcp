# Expressions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-expressions.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

## Expressions

The documentation explains LogScale's expression language capabilities, including basic values, operators, and functions that allow users to perform computations and comparisons with strings, numeric values, and boolean data. The content covers essential expression components like literal values, field references, comparison operators, numerical operations, and specialized functions such as if(), coalesce(), and text:contains(), while emphasizing that LogScale treats all values as strings that are interpreted based on their context. 

Some LogScale functions and constructs allow writing expressions instead of simple values or field names, for example, to perform computations. The most common places where expressions are used are the [`test()`](functions-test.html "test\(\)") function and the [`eval()`](functions-eval.html "eval\(\)") function and the syntactic short-hand `field := expression`, but there are other functions that take expressions as arguments, like [`coalesce()`](functions-coalesce.html "coalesce\(\)"), [`if()`](functions-if.html "if\(\)"), [`getField()`](functions-getfield.html "getField\(\)"), and [`text:contains()`](functions-text-contains.html "text:contains\(\)"). For more information about syntax rules of expressions, see also [Grammar Subset](https://library.humio.com/lql-grammar/syntax-grammar-guide-subset.html). 

### Basic Expressions and Values

LogScale's expression language can be used to compute and compare strings that represent text, numeric, and boolean values. Values can be stored in fields on the current event or used as arguments to functions that support expressions, like [`text:contains()`](functions-text-contains.html "text:contains\(\)") or [`if()`](functions-if.html "if\(\)"). 

It is important to keep in mind that in LogScale there are no types associated with values at runtime, values are basically strings that are interpreted in the context they are used. For example, the query fragment `a := "2" | b := 4 / lower(a)` results in b having the value `2`, and `a := "2" | b := format("%s%s", field=[a, a]) + 1` results in b having the value `23`. 

The basic expressions are literal strings, like `"some test"`, literal booleans like `false`, and literal numbers, like `1`, `0.5`, which evaluate to that value. 

The values of fields in the event can be referred to by the field name, for example `field`. If the event does not contain a field of that name, the expression produces the special value null. This null value is handled specially; for example, the expression `field > 3`, where the field does not exist, produces a null value, and assigning the null value to a new field in an statement like `result := field > 3` will not create (or overwrite) the field. 

### Note

The strings `"true"` and `"false"`, as well as the bare words `true` and `false`, while they are technically just strings, are interpreted as boolean values in expression contexts, for example when using the function [`if()`](functions-if.html "if\(\)"). 

### Operators

Expressions can be combined using comparison, numerical and logical operators, and put into parentheses. Using operators with values of the wrong type, for example subtracting strings, does not create a compile-time error, but usually produces a null value at runtime. 

The numerical comparison operators are `<`, `>`, `<=` and `>=` compare numerical values and produce either `true` or `false`. If the operands are not numbers, no value is produced: 

`"a" > 3` |  Comparing a string to a number, result is null.   
---|---  
`1 > 3` |  Comparing two numbers, result is false.   
`field > 3` |  Comparing the value in a field to a number, result is true/false if the field exists and has a numeric value, null otherwise.   
  
The numerical operators `+`, `-`, `/`, `*`, `%` take one or two values and compute the corresponding numerical operation if both operands are numbers; otherwise, a null value is produced: 

`"a" / 2` |  Dividing a string and a number, result is null.   
---|---  
`4 / 2` |  Dividing two numbers, result is is a number.   
`field / 2` |  Dividing the value of the field to a number, result is a number if the field exists and has a numeric value, null otherwise.   
  
The general comparison operators `==` and `!=` compare two values and produce `true` or `false`, if both values are non-null: 

`"a" == 2` |  Comparing two values of different types, result is false.   
---|---  
`1 != 2` |  Comparing two numbers, result is true.   
`field == 2` |  Comparing the value of the field to a number, result is a true/false if the field exists, null otherwise.   
  
Logical negation `!`, computes the logical negation of a boolean value, or whether a numerical value is equal to `0`. If the value is neither a boolean nor a numeric value, the result is null: 

`!false, !true` |  Negation of literal boolean value, result is true and false, respectively.   
---|---  
`!field` |  Negation of value in field field, result is true if the field contains a numeric value or `true`/`false`, otherwise it is null.   
`!0, !1` |  Negation of numeric values, result is true and false, respectively   
  
There are currently no operators for logical `AND` and `OR`. 

### Functions

Functions that calculate a single field and filter functions can also be used in expressions, where they evaluate to the value of that field, or true or false for filter functions. However, function arguments are not automatically accepting expressions, even in the context of an expression. 

For example, to calculate the cosine of a number we need to write `n := 1 | c := math:cos(n)`, because the cosine function expects a field name; the expression `c := math:cos(1)` computes the cosine of the value in the field named 1. 

Some CQL functions, like [`coalesce()`](functions-coalesce.html "coalesce\(\)"), [`if()`](functions-if.html "if\(\)"), [`getField()`](functions-getfield.html "getField\(\)"), and [`text:contains()`](functions-text-contains.html "text:contains\(\)"), support expressions as arguments, but most functions take field or array names; the type of the parameter in the documentation will be "expression", if expressions are supported. 

The function if is particularly useful in expressions, as it can be used to conditionally compute other expressions inside an expression. 

#### [`if()`](functions-if.html "if\(\)") Function

The [`if()`](functions-if.html "if\(\)") supports a typical `if...then...else` conditional statement. However, unlike a [`case`](syntax-conditional.html#syntax-conditional-case "Case Statements") or `match` statement, the [`if()`](functions-if.html "if\(\)") can be embedded into other functions and expressions. 

The [`if()`](functions-if.html "if\(\)") supports statements like the one below where a comparison is being made between timestamps to determine the time of an error: 

logscale
    
    
    errortime := if((@ingesttimestamp > @timestamp), then=@timestamp, else=@ingesttimestamp) / 1000

For more information and examples, see [`if()`](functions-if.html "if\(\)"). 

For information about other usage of statements, see [Conditional Evaluation](syntax-conditional.html "Conditional Evaluation"). 

### Field Names in Expressions

In most places in a query, it is clear from the context whether a value or the name of a field is expected. In these cases, the name of a field can be written with or without quotation marks, meaning the same. For example, `math:cos("fieldName")` means the same as `math:cos(fieldName)`, because the argument to the function is defined as a string denoting a field name, and not an expression. 

However, some field names cannot be written unquoted, because they are not bare words in the LogScale language; for example `host-name` or `host/name` need quotes when used in places where field names are expected. These two formats work: 

logscale
    
    
    host.name=*, host[0]=*
    "host-name"=*

But the following will result in a syntax error: 

logscale
    
    
    host-name=*

In this example, and more complex naming and quoting, where the double quote is required in the context of the function parameter, use the backtick (```) to quote the name. For example: 

logscale
    
    
    array:contains(array="`filters.not-values`[]", value="9847598475")

### Note

The exact details of which names need quoting are complicated. The following table contains the allowed symbols marked with UnquotedFieldName: [Character Table](https://library.humio.com/lql-grammar/syntax-grammar-guide-appendix-c.html). 

In expressions, on the other hand, quotation marks always mean a string value, while unquoted field names always mean the value of that field. To use the value of a field with such a name in an expression, the function [`getField()`](functions-getfield.html "getField\(\)") can be used with the quoted name, like `coalesce([host, getField("host-name")])`. This works because [`getField()`](functions-getfield.html "getField\(\)") takes an expression and reads the value of the field with that name. Alternatively, if not using [`getField()`](functions-getfield.html "getField\(\)"), you can copy or rename the field before using it in an expression.
