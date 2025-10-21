# formatDuration() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-formatduration.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`formatDuration()`](functions-formatduration.html "formatDuration\(\)")

Formats a duration into a human readable string. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-formatduration.html#query-functions-formatduration-as)|  string| optional[a] |  |  The output name of the field to set (defaults to the same as the input field).   
[_`field`_](functions-formatduration.html#query-functions-formatduration-field)[b]| string| required |  |  The name of the input field. Must be an integer.   
[_`from`_](functions-formatduration.html#query-functions-formatduration-from)|  long| optional[[a]](functions-formatduration.html#ftn.table-functions-formatduration-optparamfn) | [`ms`](functions-formatduration.html#query-functions-formatduration-from-option-ms)|  Magnitude of the input field.   
|  |  | **Values**  
|  |  | [`d`](functions-formatduration.html#query-functions-formatduration-from-option-d)| Days  
|  |  | [`h`](functions-formatduration.html#query-functions-formatduration-from-option-h)| Hours  
|  |  | [`m`](functions-formatduration.html#query-functions-formatduration-from-option-m)| Minutes  
|  |  | [`ms`](functions-formatduration.html#query-functions-formatduration-from-option-ms)| Milliseconds  
|  |  | [`ns`](functions-formatduration.html#query-functions-formatduration-from-option-ns)| Nanoseconds  
|  |  | [`s`](functions-formatduration.html#query-functions-formatduration-from-option-s)| Seconds  
|  |  | [`us`](functions-formatduration.html#query-functions-formatduration-from-option-us)| Microseconds  
[ _`precision`_](functions-formatduration.html#query-functions-formatduration-precision)|  number| optional[[a]](functions-formatduration.html#ftn.table-functions-formatduration-optparamfn) | `0`|  Number of units to use in the output.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-formatduration.html#query-functions-formatduration-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-formatduration.html#query-functions-formatduration-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     formatDuration("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     formatDuration(field="value")
> 
> These examples show basic structure only.

### [`formatDuration()`](functions-formatduration.html "formatDuration\(\)") Function Operation

Formats a duration into a string. For example, an input event with the field duration with the value `23452553` with a default intepretation of the source value as milliseconds results in the field duration having the value `6h30m52s553ms`. 

logscale
    
    
    formatDuration(duration)

### Important

The value of the field being formatted must be an integer. If you have a floating point input value, the value will not be converted. To fix, use [`round()`](functions-round.html "round\(\)") or [`format()`](functions-format.html "format\(\)") to create an integer value. 

### [`formatDuration()`](functions-formatduration.html "formatDuration\(\)") Examples

Click + next to an example below to get the full details.

#### Format Duration Into Human Readable String

**Format a duration into a human readable string using the[`formatDuration()`](functions-formatduration.html "formatDuration\(\)") function **

##### Query

logscale
    
    
    formatDuration(duration, precision=3)

##### Introduction

In this example, the [`formatDuration()`](functions-formatduration.html "formatDuration\(\)") function is used to format the sequences of decimal numbers into a human readable string with limited precision. Note that the value of the field being formatted must always be an integer. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         formatDuration(duration, precision=3)

Formats a duration into a string. The duration field contains the value in milliseconds. 

For example, an input event with the field duration with the value `23452553` with a default interpretation of the source value as milliseconds, results in the field duration having the value `6h30m52s553ms`. 

The optional _`precision`_ parameter specifies the number of time units to include. In this example, precision equals `3`, which means, that it shows three units: hours, minutes, and seconds. If `precision=2` is used, it may show `6h30m` instead. 

  3. Event Result set.




##### Summary and Results

The query is used to format the sequences of decimal numbers into a human readable string to improve readability of log entries with duration fields. The value of the field being formatted must always be an integer. If not an integer, you can use [`round()`](functions-round.html "round\(\)") or [`format()`](functions-format.html "format\(\)") to create an integer value. 

It is also possible to use the [`formatDuration()`](functions-formatduration.html "formatDuration\(\)") function in combination with [`eval()`](functions-eval.html "eval\(\)") to create a new formatted field: 
    
    
    formatDuration(processingTime, precision=3)
    |eval(formattedDuration = formatDuration(duration))
