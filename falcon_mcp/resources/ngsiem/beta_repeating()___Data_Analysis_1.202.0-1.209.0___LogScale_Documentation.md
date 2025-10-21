# beta:repeating() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-beta-repeating.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`beta:repeating()`](functions-beta-repeating.html "beta:repeating\(\)")

### Important

This is a beta feature, and may not work as expected and may be removed from the product without warning 

Marks the live query the function is used in as repeating. 

A repeating query is a live query that is implemented by making repeated historical queries. This can be useful when combined with functions not supported in live queries, such as [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)"), [`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)"), or certain applications of join when joining on the same repository. 

When the query snapshot cache is enabled, the historical queries made by a repeating query will reuse previous results and will therefore not be as much work for LogScale to execute as a regular historical query. When this happens, the update interval will be adjusted to the nearest time-bucket. 

This function has no effect if used in a historical query. 

This function is in beta and the behavior may change in future versions of LogScale. 

The feature RepeatingQueries must be enabled for this function to be available. This feature can be enabled by making the following GraphQL mutation as root from the API explorer at `$YOUR_LOGSCALE_URL/docs/api-explorer`: 

graphql
    
    
    mutation {
      enableFeature(feature: RepeatingQueries)
    }

### Note

If this feature is disabled, then any alert, dashboard, or saved query using [`beta:repeating()`](functions-beta-repeating.html "beta:repeating\(\)") will fail. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-beta-repeating.html#query-functions-beta-repeating-as)|  string| optional[a] |  |  The name of the output field.   
[_`interval`_](functions-beta-repeating.html#query-functions-beta-repeating-interval)[b]| long| optional[[a]](functions-beta-repeating.html#ftn.table-functions-beta-repeating-optparamfn) |  |  The time interval between successive historical queries. The time span is defined as a [Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax"). If not specified, a default interval is selected.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`interval`_](functions-beta-repeating.html#query-functions-beta-repeating-interval) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`interval`_](functions-beta-repeating.html#query-functions-beta-repeating-interval) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     beta:repeating("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     beta:repeating(interval="value")
> 
> These examples show basic structure only.

### [`beta:repeating()`](functions-beta-repeating.html "beta:repeating\(\)") Syntax Examples

Repeat a query every 5 min: 

logscale
    
    
    beta:repeating(5m)
