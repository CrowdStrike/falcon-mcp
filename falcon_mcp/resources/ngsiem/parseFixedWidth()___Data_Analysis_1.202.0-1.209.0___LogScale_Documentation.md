# parseFixedWidth() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parsefixedwidth.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`parseFixedWidth()`](functions-parsefixedwidth.html "parseFixedWidth\(\)")

Parse a fixed width-encoded field into known columns. It can parse values of the form: 

Raw Events

value 1 value 2 value 3, widths [8,8,8]  
---  
value 1value 2value 3, widths [7,7,7]  
  
Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`columns`_](functions-parsefixedwidth.html#query-functions-parsefixedwidth-columns)|  array of strings| required |  |  Names of columns to extract from field.   
[_`field`_](functions-parsefixedwidth.html#query-functions-parsefixedwidth-field)[a]| string| optional[b] | `@rawstring`|  Field that holds the input in fixed width form.   
[_`trim`_](functions-parsefixedwidth.html#query-functions-parsefixedwidth-trim)|  boolean| optional[[b]](functions-parsefixedwidth.html#ftn.table-functions-parsefixedwidth-optparamfn) | `true`|  Remove leading and trailing white-space from fields after extracting.   
[_`widths`_](functions-parsefixedwidth.html#query-functions-parsefixedwidth-widths)|  array of numbers| required |  |  Widths of columns.   
[a] The parameter name [_`field`_](functions-parsefixedwidth.html#query-functions-parsefixedwidth-field) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-parsefixedwidth.html#query-functions-parsefixedwidth-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     parseFixedWidth("value",widths=[10],columns=["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     parseFixedWidth(field="value",widths=[10],columns=["value"])
> 
> These examples show basic structure only.

For a log line like this: 

ini
    
    
    2017-02-22T13:14:01.917+0000 [main thread] INFO statsModule got result="117success 27% 3.14"

Using `parseFixedWidth(result, columns=[count, status, completion, precision, sourcetask], widths=[3,9,4,10,10)` will add these fields: 

accesslog
    
    
    count: 117
    status: success
    completion: 27%
    precision: 3.14

Sourcetask will not get assigned a value, as there were too few columns in the input for that. Values are trimmed after they have been extracted, for example, success will become success from the above example. 

Use the (unnamed) field parameter to specify which field should be parsed. Specify [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) to parse the raw string 

### [`parseFixedWidth()`](functions-parsefixedwidth.html "parseFixedWidth\(\)") Syntax Examples

Fixed width parse the result field from a log line: 

accesslog
    
    
    statsModule got result="117success 27% 3.14

The query: 

logscale
    
    
    parseFixedWidth(result, columns=[count, status,completion, precision, sourcetask], widths=[3,9,4,10,10])

will add the following fields to the event: 

  * count=117

  * status=success

  * completion=27%

  * precision=3.14




sourcetask will not get set as the input is too short. 

### [`parseFixedWidth()`](functions-parsefixedwidth.html "parseFixedWidth\(\)") Examples

Click + next to an example below to get the full details.

#### Parse Fixed Width-encoded Log Lines Fields

**Parse fixed width-encoded field from log lines into columns using the[`parseFixedWidth()`](functions-parsefixedwidth.html "parseFixedWidth\(\)") function **

##### Query

logscale
    
    
    parseFixedWidth(result, columns=[count, status, completion, precision, sourcetask], widths=[3,9,4,10,10])

##### Introduction

A fixed width file can be a very compact representation of numeric data. The file type is fast to parse, because every field is in the same place in every line. A disadvantages of fixed width file is, that it is necessary to describe the length of every field being parsed. 

In this example, the [`parseFixedWidth()`](functions-parsefixedwidth.html "parseFixedWidth\(\)") function is used to parse an accesslog. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         parseFixedWidth(result, columns=[count, status, completion, precision, sourcetask], widths=[3,9,4,10,10])

Parses the fixed width-encoded field in the accesslog and adds the returned values as known columns in the result field. 

  3. Event Result set.




##### Summary and Results

The query is used to parse compact numeric data consisting of fixed width-encoded fields into columns. 

In case a field value is longer than, for example, `10` characters, the parser handles overflow by truncating data that exceeds the specified field width while maintaining the structure of the parsed output. 

As an example, if the original sourcetask value was: `SCAN_FILES_WITH_VERY_LONG_NAME` (29 characters), then the extra characters `_WITH_VERY_LONG_NAME` would be truncated. 

This parsing method is particularly valuable when dealing with structured data that must maintain strict positional formatting and character length requirements.
