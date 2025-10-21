# lowercase() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-lowercase.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`lowercase()`](functions-lowercase.html "lowercase\(\)")

### Deprecated:Deprecated in Query Context

Deprecated when used in query context, meant for use in parsers only. For uses in queries please use the [`lower()`](functions-lower.html "lower\(\)") function. Lower-cases the contents of either or both of the field names or values of a string field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-lowercase.html#query-functions-lowercase-field)[a]| array of strings| required |  |  The name of the input field or fields (in `[]`) to lowercase. Use the special value as the only field `*` for `ALL` fields. When in this mode only the lower-cased fields remain.   
[_`include`_](functions-lowercase.html#query-functions-lowercase-include)|  string| optional[b] | [`values`](functions-lowercase.html#query-functions-lowercase-include-option-values)|  What to lowercase.   
|  |  | **Values**  
|  |  | [`both`](functions-lowercase.html#query-functions-lowercase-include-option-both)| Convert both the values and field names to lowercase  
|  |  | [`fields`](functions-lowercase.html#query-functions-lowercase-include-option-fields)| Convert the field names to lowercase  
|  |  | [`values`](functions-lowercase.html#query-functions-lowercase-include-option-values)| Convert the values of the fields to lowercase  
[ _`locale`_](functions-lowercase.html#query-functions-lowercase-locale)|  string| optional[[b]](functions-lowercase.html#ftn.table-functions-lowercase-optparamfn) |  |  The name of the locale to use, as ISO 639 language and an optional ISO 3166 country, such as `da`, `da_DK` or `en_US`. When not specified, uses the system locale.   
[a] The parameter name [_`field`_](functions-lowercase.html#query-functions-lowercase-field) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-lowercase.html#query-functions-lowercase-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     lowercase(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     lowercase(field=["value"])
> 
> These examples show basic structure only.

### [`lowercase()`](functions-lowercase.html "lowercase\(\)") Syntax Examples

With an event with a field `Bar=CONTENTS`, you get `contents` in the `Bar` field: 

logscale
    
    
    lowercase("Bar")

With an event with a field `BAR=CONTENTS`, you get `CONTENTS` in the `bar` field, while `BAR` is still `CONTENTS`. 

logscale
    
    
    lowercase("BaR", include="values")

With an event with a field `BAR=CONTENTS`, you get `contents` in the `bar` field, while `BAR` is still `CONTENTS`. 

logscale
    
    
    lowercase(field=["foo","bar"], include="both")

With an event with a field `BAR=CONTENTS`, you get `contents` in the `bar` field, while `BAR` is no longer present. 

logscale
    
    
    lowercase(field="*", include="both")
