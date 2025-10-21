# length() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-length.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`length()`](functions-length.html "length\(\)")

Computes the number of characters in a string field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-length.html#query-functions-length-as)|  string| optional[a] | `_length`|  Name of output field.   
[_`field`_](functions-length.html#query-functions-length-field)[b]| string| required |  |  The name of the input field to length.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-length.html#query-functions-length-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-length.html#query-functions-length-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     length("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     length(field="value")
> 
> These examples show basic structure only.

### [`length()`](functions-length.html "length\(\)") Examples

Click + next to an example below to get the full details.

#### Count Characters in Field

**Count the number of characters in a field using the[`length()`](functions-length.html "length\(\)") function **

##### Query

logscale
    
    
    length(@rawstring)

##### Introduction

In this example, the [`length()`](functions-length.html "length\(\)") function is used to count the number of characters in the @rawstring field and output the result in a field named _length. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         length(@rawstring)

Counts the number of characters in the field @rawstring field and outputs the result in a field named _length. This count includes all visible characters, spaces, and punctuation marks in the log entry. 

Using the [_`as`_](functions-length.html#query-functions-length-as) parameter, it is also possible to define another output field, for example, rawLength, if adding the following: 

`length(@rawstring, as="rawLength")`

  3. Event Result set.




##### Summary and Results

The query is used to make a count of all characters (all visible characters, spaces, and punctuation marks) in a log entry. Making a count of all characters is useful for managing and analyzing, for example, security logs, ensuring complete data capture for threat detection and incident response.
