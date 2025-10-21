# getField() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-getfield.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`getField()`](functions-getfield.html "getField\(\)")

Takes an expression — `source` — and sets the field defined by [_`as`_](functions-getfield.html#query-functions-getfield-as) to the result of the `source` expression. 

Can be used to manipulate fields whose names are not statically known, but computed at runtime. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-getfield.html#query-functions-getfield-as)|  string| optional[a] | `_getField`|  Name of output field.   
[_`source`_](functions-getfield.html#query-functions-getfield-source)|  expression| required |  |  An expression which evaluates the name of the field to read.   
[a] Optional parameters use their default value unless explicitly set.  
  
### [`getField()`](functions-getfield.html "getField\(\)") Function Operation

The function can be used to read fields whose exact name might not be known, by getting the value of a dynamically-named field. This happens when the field name is computed from an expression, so the function works by evaluating this expression as input. 

It can also be used to manipulate fields whose names contain a space or `-` like in: 

logscale
    
    
    deltaTime:= now() - getField("time-in-ms")

### [`getField()`](functions-getfield.html "getField\(\)") Examples

Click + next to an example below to get the full details.

#### Find the First Values in a List of Fields

**Find the first values of a list of fields to normalize data using the[`coalesce()`](functions-coalesce.html "coalesce\(\)") function **

##### Query

logscale
    
    
    coalesce([host, server, host[0].name, "example.com"])

##### Introduction

In this example, [`coalesce()`](functions-coalesce.html "coalesce\(\)") is used to normalize data from different sources — the fields have the same meaning but different names in the input data. 

Example incoming data might look like this: 

host=''  
---  
server='crowdstrike.com'  
host[0].name='crowdstrike.com'  
machine='clienta'  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         coalesce([host, server, host[0].name, "example.com"])

Finds the values of the first three fields host, server, host[0].name and the value of a string `"example.com"` and returns the results in a new field named __coalesce. Notice that the query uses a string literal as the last expression, which serves as a default value, because its value is not null. The first three expressions, on the other hand, are field names. 

In this example, the field names are simple and do not contain unsupported characters. 

If the field names contain unsupported characters, for example a space or an operator like '-', then the field cannot be quoted in LogScale, as it would be interpreted as string literals. In these situations, the [`getField()`](functions-getfield.html "getField\(\)") must be used together with the [`coalesce()`](functions-coalesce.html "coalesce\(\)") function, like in the following example: `coalesce([getField("host-name"), getField("server name"), "example.com"])`

  3. Event Result set.




##### Summary and Results

The query is used to normalize data from different sources by finding the first value of a list of fields that are defined. The [`coalesce()`](functions-coalesce.html "coalesce\(\)") function is useful if, for example, you want to easily pick the first non-null value from the list of prioritized fields and save it as a new field, or if you want to be able to use default (string) value or an expression instead of field name as an argument. 

Sample output from the incoming example data: 

_coalesce| host| server| host[0].name| machine  
---|---|---|---|---  
crowdstrike.com| <no value>| crowdstrike.com|  |   
  
#### Get the Last Element of an Array

****

##### Query

logscale
    
    
    | index := array:length("foo[]")-1
    | fieldName := format("foo[%s]", field=[index])
    | result := getField(fieldName)

##### Introduction

Given an event with an array for field foo[x]: 
    
    
    foo['a','b','c','d']

Looks up the value of the field which is part of an array of elements, using [`getField()`](functions-getfield.html "getField\(\)") in combination with expressions: first build the string with the field, then perform [`getField()`](functions-getfield.html "getField\(\)") in that string to get the result. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         | index := array:length("foo[]")-1

Sets the index as the last element of the array (in this case, `[6]`) 

  3. logscale
         
         | fieldName := format("foo[%s]", field=[index])

Takes the field index and builds the string foo[6] using [`format()`](functions-format.html "format\(\)")

  4. logscale
         
         | result := getField(fieldName)

Provides the value of the field whose name is foo[6]

  5. Event Result set.




##### Summary and Results

The output is displayed as follows, where the last column shows the value of fieldName column (which is foo[3]) as the result: 

@timestamp| @rawstring| @timestamp.nanos| fieldName| foo[0]| foo[1]| foo[2]| foo[3]| index| result  
---|---|---|---|---|---|---|---|---|---  
2024-03-01T08:43:12| {"foo": ["a","b","c","d"]}| 0| foo[3]| a| b| c| d| 3| d  
  
#### Get the Value of a Field Stored in Another Field

****

##### Query

logscale
    
    
    result := getField("foo")

##### Introduction

Given an event with the following fields: 
    
    
    |------------------|
    | foo      | bar   |
    | bar      | 123   |
    | foo      | quux  |
    |------------------|

Do a "direct" lookup where the result is set to the value that is stored in that field, by quoting the string — it takes expressions as input (similar to [`eval()`](functions-eval.html "eval\(\)") and [`test()`](functions-test.html "test\(\)") functions): 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         result := getField("foo")

The result is set to the value that is stored in field foo

  3. Event Result set.




##### Summary and Results

bar| foo| result  
---|---|---  
123| bar| bar  
<no value>| quux| quux  
  
In the same event, using the same query that does not quote the string: 

logscale
    
    
    result := getField(foo)

will get the value of the field which name is stored at foo, so `123` is stored as the result: 

bar| foo| result  
---|---|---  
123| bar| 123  
<no value>| quux| <no value>  
  
(no result is output for `foo=quux` as `quux` does not exist). 

#### Take Field Names as Parameters

****

##### Query

logscale
    
    
    | test(getField(?foo)==?bar)

##### Introduction

Use the function to take a field name as a parameter. 

Given an event with the following fields: 
    
    
    |----------------------|
    | hello      | world   |
    |----------------------|

Test if a field exists on an event with a specific value where both the field and the value are given as parameters. This query: 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         | test(getField(?foo)==?bar)

Tests if the field given by the parameter `?foo (hello)` is equal to the value given by the parameter `?bar (world)`. 

  3. Event Result set.




##### Summary and Results

hello  
---  
world
