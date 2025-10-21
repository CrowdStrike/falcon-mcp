# writeJson() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-writejson.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`writeJson()`](functions-writejson.html "writeJson\(\)")

Writes data as a JSON object, and includes field values optionally. The specified fields will be formatted as JSON and assigned to the field specified in [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters"), defaults to _json. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-writejson.html#query-functions-writejson-as)|  string| optional[a] | `_json`|  Name of output field.   
[_`field`_](functions-writejson.html#query-functions-writejson-field)[b]| array of strings| optional[[a]](functions-writejson.html#ftn.table-functions-writejson-optparamfn) | `@rawstring`|  Values and fields that should be converted to JSON. Accepts either a value or array of values. Values are interpreted as prefix matches, unless a globbing pattern with * is given (see following example).   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-writejson.html#query-functions-writejson-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-writejson.html#query-functions-writejson-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     writeJson(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     writeJson(field=["value"])
> 
> These examples show basic structure only.

### [`writeJson()`](functions-writejson.html "writeJson\(\)") Syntax Examples

  * Multiple fields can be included. Given events where: 

json
        
        a.b.c=5,
        a.b.e[0]=6,
        a.d=7,
        a.f.g=8

use the query function to call: 

logscale
        
        writeJson(["a.b.c", "a.b.e[0]", "a.d", "a.f.g"])

It will write the following JSON to each event, respectively: 

json
        
        {"a":{"b":{"c":5}}},
        {"a":{"b":{"e":[6]}}},
        {"a":{"d":7}},
        {"a":{"f":{"g":8}}}

  * Arguments passed to the field parameter are interpreted as prefix matches. For example, the query: 

logscale
        
        writeJson(field=["a.b"])

matches: 

json
        
        a.b.c
         a.bc
         a.b[0]
         a.b!
        …

  * Array-glob patterns can be passed to the field parameter. For example, the query: 

logscale
        
        writeJson(field=["a.b[*]"])

matches all fields in the event and it also matches anything else that starts with a: 

json Syntax
        
        a.b[0]
        a.b[0]c
        a.b[0].c
        a.b[0][0]
        a.b[0]!
        ...
        a.b[1]c
        a.b[1].c
        a.b[1][0]
        a.b[1]!
        …




### [`writeJson()`](functions-writejson.html "writeJson\(\)") Examples

Click + next to an example below to get the full details.

#### Convert Fields to JSON Format

**Convert values and fields to JSON format using the[`writeJson()`](functions-writejson.html "writeJson\(\)") function **

##### Query

logscale
    
    
    writeJson(["a.b.c", "a.b.e[0]", "a.d", "a.f.g"])

##### Introduction

In this example, the [`writeJson()`](functions-writejson.html "writeJson\(\)") function is used to create a nested JSON structure from an array of field paths. The function handles both regular nested fields and array indexing. 

Example incoming data might look like this: 

@timestamp| a.b.c| a.b.e[0]| a.d| a.f.g  
---|---|---|---|---  
2023-06-15T10:30:00Z| value1| value2| value3| value4  
2023-06-15T10:30:01Z| test1| test2| test3| test4  
2023-06-15T10:30:02Z| data1| data2| data3| data4  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         writeJson(["a.b.c", "a.b.e[0]", "a.d", "a.f.g"])

Creates a JSON structure from the specified field paths and returns the JSON formatted results in a new field named _json. 

In this example, the [`writeJson()`](functions-writejson.html "writeJson\(\)") function: 

     * Takes an array of field paths as input. 

     * Handles nested field paths using dot notation. 

     * Supports array indexing with square bracket notation. 

     * Maintains the hierarchical relationship between fields in the resulting JSON. 

  3. Event Result set.




##### Summary and Results

The query is used to transform flat field references into a structured JSON object, preserving the hierarchical relationships between fields. 

This query is useful, for example, to reconstruct nested data structures from flattened fields, to prepare data for external systems that expect nested JSON or to create structured views of related fields 

Sample output from the incoming example data: 

_json| a.b.c| a.b.e[0]| a.d| a.f.g  
---|---|---|---|---  
{"a":{"b":{"c":"value1","e":["value2"]},"d":"value3","f":{"g":"value4"}}}| value1| value2| value3| value4  
{"a":{"b":{"c":"test1","e":["test2"]},"d":"test3","f":{"g":"test4"}}}| test1| test2| test3| test4  
{"a":{"b":{"c":"data1","e":["data2"]},"d":"data3","f":{"g":"data4"}}}| data1| data2| data3| data4
