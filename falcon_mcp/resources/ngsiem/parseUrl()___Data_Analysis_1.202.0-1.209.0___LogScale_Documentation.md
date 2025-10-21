# parseUrl() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parseurl.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`parseUrl()`](functions-parseurl.html "parseUrl\(\)")

Extracts URL components from a field. The attributes `url.scheme`, `url.username`, `url.password`, `url.host`, `url.port`, `url.path`, `url.fragment` and `url.query` are added to the event. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-parseurl.html#query-functions-parseurl-as)|  string| optional[a] |  |  Use a prefix for the attributes added to the event.   
[_`field`_](functions-parseurl.html#query-functions-parseurl-field)[b]| string| optional[[a]](functions-parseurl.html#ftn.table-functions-parseurl-optparamfn) | `url`|  The field from which to parse URL components.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-parseurl.html#query-functions-parseurl-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-parseurl.html#query-functions-parseurl-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     parseUrl("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     parseUrl(field="value")
> 
> These examples show basic structure only.

### [`parseUrl()`](functions-parseurl.html "parseUrl\(\)") Function Operation

The [`parseUrl()`](functions-parseurl.html "parseUrl\(\)") uses the Java `java.net.URI` to parse and extract the URL components. See [URI](https://docs.oracle.com/javase/7/docs/api/java/net/URI.html) for more information on the parsing and extraction of URI elements. 

Due to the way the parsing works, it is possible that the parser will mis-identify elements of a URL if the URL is only partial. The class by default looks for the URL scheme first (for example, the portion of a string before the first colon). This can mean that the URLs that are not fully qualified are misidentified. For example, consider the URL: 

HTML
    
    
    site.example.com:80/path/to/examp

Parsing will identify `site.example.com` as url.scheme. Care should be taken to ensure that a fully-qualified URL is supplied to ensure correct parsing of the components. See the Java [URI](https://docs.oracle.com/javase/7/docs/api/java/net/URI.html) page for more information on how the individiaul elements are parsed. 

### [`parseUrl()`](functions-parseurl.html "parseUrl\(\)") Syntax Examples

Within the humio repository, parsing the uri field to aggregate the list of paths used: 

logscale
    
    
    parseUrl(uri)
    | groupBy(uri.path)

Creates the corresponding URI fields which are aggregated and result in output similar to this: 

uri| _count  
---|---  
/graphql| 132  
/api/v1/refresh| 95  
/api/v1/repositories/humio/queryjobs| 30  
/api/v1/repositories/humio/queryjobs/P29-vxBwkHK6nxeDuC4CzOOmc0Oq| 3  
/api/v1/repositories/humio/queryjobs/P7-mHpupr5riWe5XEoRnY8VhicU| 2  
/api/v1/repositories/humio/queryjobs/P7-eaRjXUkTzse6fB3M6kQcbh4m| 2  
/api/v1/repositories/humio/queryjobs/P7-WjVRVoJWmdh9REgpuoGHyoOC| 2  
/api/v1/repositories/humio/queryjobs/P7-VadNjnjvQaeXcfJRhfRb5Uuv| 2  
/api/v1/repositories/humio/queryjobs/P7-GlsGrU405DmI2PPeL33PwT9n| 2  
/api/v1/repositories/humio/queryjobs/P7-Bwg99bEHk6NeBmSU1fSZG0Fa| 2  
/api/v1/repositories/humio/queryjobs/P6-6VusohlK49WisjAYttFIbpfm| 2  
  
Parses the field named endpoint and adds URL components to the event. 

logscale
    
    
    parseUrl(field=endpoint)

Parses the field named endpoint and adds URL components to the event with the field url as a prefix, for example url.path, url.scheme etc. 

logscale
    
    
    url := parseUrl(field=endpoint)

Parses the field named endpoint and adds URL components to the event with apiEndpoint as a prefix, for example apiEndpoint.path, apiEndpoint.scheme etc. 

logscale
    
    
    parseUrl(field=endpoint, as=apiEndpoint)
