# coalesce() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-coalesce.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`coalesce()`](functions-coalesce.html "coalesce\(\)")

Accepts a list of fields and returns the first value that is not null or empty. For example, when accessing a value that may exist in any number of potential fields, a [case](https://library.humio.com/kb/kb-using-case-statements.html) statement could be used to select between the fields to identify the value from the collection of fields. Using [`coalesce()`](functions-coalesce.html "coalesce\(\)") returns the first matching value across the selection of supplied fields. If empty string values should be returned instead of being ignored, the [_`ignoreEmpty`_](functions-coalesce.html#query-functions-coalesce-ignoreempty) parameter can be set to `false` to change the behavior. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-coalesce.html#query-functions-coalesce-as)|  string| optional[a] | `_coalesce`|  The field that contains the selected value, if any non-null value is found.   
[_`expressions`_](functions-coalesce.html#query-functions-coalesce-expressions)[b]| list of expressions| required |  |  The list of expression candidates to select from; the first non-null result from left to right is used.   
[_`ignoreEmpty`_](functions-coalesce.html#query-functions-coalesce-ignoreempty)|  boolean| optional[[a]](functions-coalesce.html#ftn.table-functions-coalesce-optparamfn) | `true`|  If `true`, empty strings are treated as undefined values, that is, they are not selected.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`expressions`_](functions-coalesce.html#query-functions-coalesce-expressions) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`expressions`_](functions-coalesce.html#query-functions-coalesce-expressions) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     coalesce("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     coalesce(expressions="value")
> 
> These examples show basic structure only.

### [`coalesce()`](functions-coalesce.html "coalesce\(\)") Examples

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
