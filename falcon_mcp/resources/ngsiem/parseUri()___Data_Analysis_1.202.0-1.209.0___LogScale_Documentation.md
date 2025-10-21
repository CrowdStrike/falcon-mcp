# parseUri() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parseuri.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`parseUri()`](functions-parseuri.html "parseUri\(\)")

This function extracts URI components from an input field and adds them as attributes to the event. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`defaultBase`_](functions-parseuri.html#query-functions-parseuri-defaultbase)|  string| optional[a] |  |  A scheme and authority prefix or `//`, used as the base to resolve the input as a URI reference. Valid values are of the form `//` or `scheme://` where `scheme` is a [URI scheme](https://datatracker.ietf.org/doc/html/rfc3986#section-3.1) .   
[_`field`_](functions-parseuri.html#query-functions-parseuri-field)[b]| string| required |  |  The name of the input field that contains the value to analyze.   
[_`prefix`_](functions-parseuri.html#query-functions-parseuri-prefix)|  string| optional[[a]](functions-parseuri.html#ftn.table-functions-parseuri-optparamfn) | `input field name`|  An optional prefix for the field names for the components that are added to the event. It is an error to provide an empty prefix.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-parseuri.html#query-functions-parseuri-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-parseuri.html#query-functions-parseuri-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     parseUri("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     parseUri(field="value")
> 
> These examples show basic structure only.

### [`parseUri()`](functions-parseuri.html "parseUri\(\)") Function Operation

This function is most useful for interpreting partial URIs like `www.example.com/path`: instead of requiring fully valid URIs, [`parseUri()`](functions-parseuri.html "parseUri\(\)") accepts a "base" (for example, [_`defaultBase=http://`_](functions-parseuri.html#query-functions-parseuri-defaultbase)) used to extract the hostname, port, path, query, and fragment parts. 

if the input URI has no authority component, the event is left unchanged, similar to the [`parseUrl()`](functions-parseurl.html "parseUrl\(\)") behavior — `example.com` is interpreted as the scheme and it won't find a hostname or path (because it is trying to interpret the input as a URI): that's where providing the "base" can override such behavior. 

If a base is used with a full URI, it is ignored; for example, consider this value in the url field: 

HTML
    
    
    ftp://example.com/path

The query: 

logscale
    
    
    parseUri(field="url", defaultBase="http://")

will extract url.scheme=ftp and not url.scheme=http. 

See [`parseUri()` Syntax Examples](functions-parseuri.html#functions-parseuri-syntax-examples "parseUri\(\) Syntax Examples") for more examples. 

This function is more lenient in what it considers a URI than the specification requires and matches mostly on the structure of the input (with some restrictions); this is by design to make the functionality useful in different contexts. 

### Note

This function does no normalization/decoding on the components (like percent-encoding or path normalization). This is intended to process the actual parts of the input as they were in the logs. 

The fields added to the event are listed in table here below — they are only added if the input can be parsed as a URI itself or resolved to a URI reference by providing the [_`defaultBase`_](functions-parseuri.html#query-functions-parseuri-defaultbase) parameter. The `url.` prefix is replaced by the input field name or the specified target field name. 

**Attribute** |  **Description**  
---|---  
url.scheme |  The scheme in input value, if found. Otherwise, the scheme found in the base, if a base argument is provided and has a scheme.   
url.hostname |  The hostname, if found.   
url.username |  The username, if found   
url.password |  The password, if found.   
url.port |  The port in the authority, if found.   
url.path |  The path, if found in the input. It can be empty.   
url.query |  The query component, if found in the input.   
url.fragment |  The fragment component, if found in the input.   
  
Unless noted otherwise, the field for a component is not added if the component is not present in the input value. 

Values are provided as found in the input, for example, without normalization (does not apply to scheme and port, which can't be normalized). 

### [`parseUri()`](functions-parseuri.html "parseUri\(\)") Syntax Examples

  * Input: 

HTML
        
        example.com:8080/foo

Query: 

logscale
        
        parseUri(field="url", defaultBase="http://")

Output: 
        
        host=example.com
        path=/foo
        port=8080
        scheme=http

  * Input: 

HTML
        
        example.com:8080/foo

Query: 

logscale
        
        parseUri(field="url")

Output: 
        
        scheme=example.com
        path=8080/foo

  * Input: 

HTML
        
        ftp://example.com:8080/foo

Query: 

logscale
        
        parseUri(field="url", defaultBase="http://")

Output: 
        
        host=example.com
        path=/foo
        port=8080
        scheme=ftp




### [`parseUri()`](functions-parseuri.html "parseUri\(\)") Examples

Click + next to an example below to get the full details.

#### Parse URL Into Components

**Extract individual components from a URL string using the parseUri()[`parseUri()`](functions-parseuri.html "parseUri\(\)") function **

##### Query

logscale
    
    
    parseUri(field="url")

##### Introduction

In this example, the [`parseUri()`](functions-parseuri.html "parseUri\(\)") function is used to break down a URL into its constituent parts, such as scheme, hostname, port, path, and query parameters. 

Example incoming data might look like this: 

#fields @timestamp| url  
---|---  
1683000000000000000| https://admin:password123@api.example.com:8443/v2/users?active=true&role=admin#section1  
1683000001000000000| http://user:pass@test.domain.com/path/to/resource?param=value  
1683000002000000000| https://api.service.com:443/api/v1/data  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         parseUri(field="url")

Parses the URL string in the url field and creates new fields with the following components: 

     * url.scheme \- The protocol (for example, http, https) 

     * url.username \- The username if present in the URL 

     * url.password \- The password if present in the URL 

     * url.hostname \- The domain name or IP address 

     * url.port \- The port number if specified 

     * url.path \- The path component of the URL 

     * url.query \- The query string parameters 

     * url.fragment \- The fragment identifier (after #) 

  3. Event Result set.




##### Summary and Results

The query is used to decompose URLs into their individual components for detailed analysis and processing. 

This query is useful, for example, to analyze web traffic patterns, monitor API usage, detect security issues in URLs, or extract specific URL components for further processing. 

Sample output from the incoming example data: 

#fields @timestamp| url| url.scheme| url.username| url.password| url.hostname| url.port| url.path| url.query| url.fragment  
---|---|---|---|---|---|---|---|---|---  
1683000000000000000| https://admin:password123@api.example.com:8443/v2/users?active=true&role=admin#section1| https| admin| password123| api.example.com| 8443| /v2/users| active=true&role=admin| section1  
1683000001000000000| http://user:pass@test.domain.com/path/to/resource?param=value| http| user| pass| test.domain.com| <no value>| /path/to/resource| param=value| <no value>  
1683000002000000000| https://api.service.com:443/api/v1/data| https| <no value>| <no value>| api.service.com| 443| /api/v1/data| <no value>| <no value>  
  
Note that fields are only created for components that are present in the URL. If a component is missing (such as port or query parameters), no corresponding field will be created for that event. 

After parsing the URL, you can use these individual components for filtering, analysis, or creating alerts based on specific URL patterns or components. 

The parsed URL components can be effectively visualized in a table using the [`table()`](functions-table.html "table\(\)") function: `| table([ ["URL Components", "Values"], ["URL", url], ["Scheme", url.scheme], ["Username", url.username], ["Password", url.password], ["Hostname", url.hostname], ["Port", url.port], ["Path", url.path], ["Query", url.query], ["Fragment", url.fragment] ])`.
