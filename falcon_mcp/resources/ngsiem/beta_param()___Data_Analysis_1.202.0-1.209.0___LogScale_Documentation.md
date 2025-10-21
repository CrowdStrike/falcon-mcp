# beta:param() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-beta-param.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`beta:param()`](functions-beta-param.html "beta:param\(\)")

Reads the given parameter and assigns value to a field in the event. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-beta-param.html#query-functions-beta-param-as)|  string| required |  |  The name of the output field.   
[_`parameter`_](functions-beta-param.html#query-functions-beta-param-parameter)[a]| string| required |  |  The name of the parameter to read.   
[a] The parameter name [_`parameter`_](functions-beta-param.html#query-functions-beta-param-parameter) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`parameter`_](functions-beta-param.html#query-functions-beta-param-parameter) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     beta:param("value",as="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     beta:param(parameter="value",as="value")
> 
> These examples show basic structure only.
