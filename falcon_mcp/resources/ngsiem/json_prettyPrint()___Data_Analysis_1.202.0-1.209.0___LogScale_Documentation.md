# json:prettyPrint() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-json-prettyprint.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`json:prettyPrint()`](functions-json-prettyprint.html "json:prettyPrint\(\)")

'Pretty prints' a JSON field. The function formats a JSON field for improved readability. This can be an expensive operation. 

It is recommended to apply [`json:prettyPrint()`](functions-json-prettyprint.html "json:prettyPrint\(\)") after filtering your data at the end of the query. This prevents unnecessary formatting of data that will be discarded. 

Default behaviour is as follows: 

  * If the field does not contain valid JSON, the unmodified input value is stored in the output field. 

  * If no field is specified, the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field will be formatted. 




Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-json-prettyprint.html#query-functions-json-prettyprint-as)|  string| optional[a] |  |  The name of the field to store the output in.   
[_`field`_](functions-json-prettyprint.html#query-functions-json-prettyprint-field)[b]| string| optional[[a]](functions-json-prettyprint.html#ftn.table-functions-json-prettyprint-optparamfn) | `@rawstring`|  The name of the field to format.   
[_`step`_](functions-json-prettyprint.html#query-functions-json-prettyprint-step)|  number| optional[[a]](functions-json-prettyprint.html#ftn.table-functions-json-prettyprint-optparamfn) | `2`|  The indentation in number of characters, minimum 2 spaces.   
[_`strict`_](functions-json-prettyprint.html#query-functions-json-prettyprint-strict)|  boolean| optional[[a]](functions-json-prettyprint.html#ftn.table-functions-json-prettyprint-optparamfn) | `false`|  If set to true only valid JSON input produce a value in the output field. By default invalid JSON is copied to the output field unmodified.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-json-prettyprint.html#query-functions-json-prettyprint-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-json-prettyprint.html#query-functions-json-prettyprint-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     json:prettyPrint("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     json:prettyPrint(field="value")
> 
> These examples show basic structure only.

### [`json:prettyPrint()`](functions-json-prettyprint.html "json:prettyPrint\(\)") Examples

Click + next to an example below to get the full details.

#### Format JSON

**Format JSON in @rawstring field using the [`json:prettyPrint()`](functions-json-prettyprint.html "json:prettyPrint\(\)") function **

##### Query

logscale
    
    
    #type=json
    | account=123
    | json:prettyPrint()

##### Introduction

In this example, the [`json:prettyPrint()`](functions-json-prettyprint.html "json:prettyPrint\(\)") function is used to format the @rawstring field. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #type=json

Filters for events with the `JSON` type. 

  3. logscale
         
         | account=123

Filters for events related to account 123. 

It is recommended to filter the event set as much as possible before using the [`json:prettyPrint()`](functions-json-prettyprint.html "json:prettyPrint\(\)") function to prevent unnecessary formatting of discarded data. 

  4. logscale
         
         | json:prettyPrint()

Formats the `JSON` content for improved readability. Without a specified field, it formats the @rawstring field. 

Note that if input is not valid JSON, it returns unmodified values. To prevent this, you can set a [_`strict`_](functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter. For an example of usage, see [Format Only Valid JSON](https://library.humio.com/examples/examples-jsonprettyprint-strict.html). 

  5. Event Result set.




##### Summary and Results

The query is used to make JSON data more readable in the results. Formatting JSON in the @rawstring field after filtering the data is very important as it is a resource-intensive operation. 

Note that without the [_`strict`_](functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter set to `true`, the [`json:prettyPrint()`](functions-json-prettyprint.html "json:prettyPrint\(\)") function attempts to format even invalid JSON, which might lead to unexpected results. 

#### Format Only Valid JSON

**Format only JSON data that is considered valid using the[`json:prettyPrint()`](functions-json-prettyprint.html "json:prettyPrint\(\)") function **

##### Query

logscale
    
    
    formattedJson := json:prettyPrint(field=message, strict=true)

##### Introduction

In this example, the [`json:prettyPrint()`](functions-json-prettyprint.html "json:prettyPrint\(\)") function is used to format the message field as JSON with the [_`strict`_](functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter set to `true` to only process valid JSON. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         formattedJson := json:prettyPrint(field=message, strict=true)

Uses the [_`field`_](functions-json-prettyprint.html#query-functions-json-prettyprint-field) parameter to specify the message field as the source of JSON data and the [_`strict`_](functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter set to `true` to only process valid JSON. 

Formats the valid JSON data for improved readability and assigns the results to a new field named formattedJson. 

Note that if the JSON in the message field is invalid, the formattedJson field will not be created for that event. This is because the [_`strict`_](functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter is set to `true`. 

  3. Event Result set.




##### Summary and Results

The query is used to make valid JSON data more readable in the results. 

Without [_`strict`_](functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter set to `true`, the [`json:prettyPrint()`](functions-json-prettyprint.html "json:prettyPrint\(\)") function attempts to format even invalid JSON, which might lead to unexpected results.
