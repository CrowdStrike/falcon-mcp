# default() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-default.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`default()`](functions-default.html "default\(\)")

Creates a field with the name of the parameter _`field`_ setting its value to _`value`_. If the field already exists on an event the field keeps its existing value. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-default.html#query-functions-default-field)|  string or array| required |  |  The field or fields to set the default value for. An array of multiple field names can be passed to this parameter.   
[_`replaceEmpty`_](functions-default.html#query-functions-default-replaceempty)|  boolean| optional[a] | `false`|  If the field's value is the empty string, override the value with the default.   
[_`value`_](functions-default.html#query-functions-default-value)[b]| string| required |  |  Default value to assign to [_`field`_](functions-default.html#query-functions-default-field), if not already set.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`value`_](functions-default.html#query-functions-default-value) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`value`_](functions-default.html#query-functions-default-value) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     default("value",field="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     default(value="value",field="value")
> 
> These examples show basic structure only.

### [`default()`](functions-default.html "default\(\)") Examples

Click + next to an example below to get the full details.

#### Set Default Values for Fields - Example 1

**Set default values for field using the[`default()`](functions-default.html "default\(\)") function so it can be used in a calculation with [`eval()`](functions-eval.html "eval\(\)") **

##### Query

logscale
    
    
    default(field=[minutes, seconds, hours], 0)

##### Introduction

Setting default values of fields is necessary, if the fields are to be used in calculations with the [`eval()`](functions-eval.html "eval\(\)") function. If not set to a value so the field is considered to be present, the event would be discarded during eval step. In this example, an array is set as the _`field`_ parameter. This allows setting the same default value for multiple fields with a single command. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         default(field=[minutes, seconds, hours], 0)

Sets the default value of the fields minutes, seconds and hours to `0` so it can be used in a calculation. It ensures, that all time-related fields have a numeric value. 

If the fields did not have a value, the event would be discarded during the eval step because [`eval()`](functions-eval.html "eval\(\)") requires all used fields to be present. 

  3. Event Result set.




##### Summary and Results

The query is used to enable calculation of the fields with the [`eval()`](functions-eval.html "eval\(\)") function. The query ensures that all events have consistent minutes, seconds, and hours fields for further processing or analysis. Otherwise, if the field is not set to a value, the event is not parsed. The use of the [`default()`](functions-default.html "default\(\)") function is important for data normalization and preparation in log analysis, ensuring consistent and complete data sets for further processing and analysis. For example, in a security event log, ensuring that all events have a message can be crucial for quick triage. 

#### Set Default Values for Fields - Example 2

**Set default values for field using the[`default()`](functions-default.html "default\(\)") function so it can be used in a calculation with [`eval()`](functions-eval.html "eval\(\)") **

##### Query

logscale
    
    
    default(field=[url, uri, link], "localhost")

##### Introduction

Setting default values of fields is necessary, if the fields are to be used in calculations with the [`eval()`](functions-eval.html "eval\(\)") function. If not set to a value so the field is considered to be present, the event would be discarded during eval step because [`eval()`](functions-eval.html "eval\(\)") requires all used fields to be present. In this example, an array is set as the _`field`_ parameter. This allows setting the same default value for multiple fields with a single command. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         default(field=[url, uri, link], "localhost")

Sets the default value of the fields url, uri and link in an array to _`localhost`_. It ensures, that URL-related fields always have a value. 

  3. Event Result set.




##### Summary and Results

The query is used to enable calculation of the fields with the [`eval()`](functions-eval.html "eval\(\)") function. The query ensures that all events will have consistent url, uri, and link fields for further processing or analysis. Otherwise, if the field is not set to a value, the event is not parsed. The use of the [`default()`](functions-default.html "default\(\)") function is important for data normalization and preparation in log analysis, ensuring consistent and complete data sets for further processing and analysis. For example, in a security event log, ensuring that all events have a message can be crucial for quick triage. 

#### Set Default Values for Fields - Example 3

**Set default values for a field and replace empty values with relevant default value**

##### Query

logscale
    
    
    default(field=message, value="N/A", replaceEmpty=true)

##### Introduction

Setting default values of fields is necessary, if the fields are to be used in calculations with the [`eval()`](functions-eval.html "eval\(\)") function. If not set to a value so the field is considered to be present, the event would be discarded during eval step. 

In LogScale, empty values are by default kept as the field does indeed exist when it has the empty value. 

This examples shows how to set _`replaceEmpty`_ to `true` to replace empty values with the default as well. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         default(field=message, value="N/A", replaceEmpty=true)

Replaces an empty value in the field message with the default value `"N/A"` by setting _`replaceEmpty`_ to `true`. 

  3. Event Result set.




##### Summary and Results

The query is used to replace empty values in a field to a defined default value. If not setting a default value for empty values, the event would be discharded during further eval steps because [`eval()`](functions-eval.html "eval\(\)") requires all used fields to be present. The use of the [`default()`](functions-default.html "default\(\)") function is important for data normalization and preparation in log analysis, ensuring consistent and complete data sets for further processing and analysis. For example, in a security event log, ensuring that all events have a message can be crucial for quick triage.
