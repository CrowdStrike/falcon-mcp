# urlEncode() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-urlencode.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Sep 29, 2025

## [`urlEncode()`](functions-urlencode.html "urlEncode\(\)")

URL encodes the contents of a string field. The [`urlEncode()`](functions-urlencode.html "urlEncode\(\)") function converts special characters like parentheses, pipes, and spaces into their URL-safe percent-encoded equivalents. By default, the encoded result is returned in a new field named _urlencode. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-urlencode.html#query-functions-urlencode-as)|  string| optional[a] | `_urlencode`|  Name of output field.   
[_`field`_](functions-urlencode.html#query-functions-urlencode-field)[b]| string| required |  |  Name of input field that contains the value for URL encoding.   
[_`type`_](functions-urlencode.html#query-functions-urlencode-type)|  string| optional[[a]](functions-urlencode.html#ftn.table-functions-urlencode-optparamfn) |  |  Type of encoding.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-urlencode.html#query-functions-urlencode-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-urlencode.html#query-functions-urlencode-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     urlEncode("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     urlEncode(field="value")
> 
> These examples show basic structure only.

### [`urlEncode()`](functions-urlencode.html "urlEncode\(\)") Syntax Examples

This example shows how to URL encode a LogScale query string so it can be safely included in a URL parameter. 

logscale
    
    
    urlEncode(bar)

If input was `bar := "tail(1) | count()"`, it would return: 
    
    
    "_urlencode"
    "tail%281%29+%7C+count%28%29"

This example shows how to URL encode an email address so it can be safely included in a URL parameter. 

logscale
    
    
    urlEncode(bar)

If input was `bar := "example@example.com"`, it would return: 
    
    
    "_urlencode"
    "example%40example.com"

This example shows how to URL encode a field containing a string so it can be safely included in a URL parameter. 

logscale
    
    
    urlEncode(bar)

If input was `bar := "Title with spaces/special characters!"`, it would return: 
    
    
    "_urlencode"
    "Title+with+spaces%2Fspecial+characters%21"

### [`urlEncode()`](functions-urlencode.html "urlEncode\(\)") Examples

Click + next to an example below to get the full details.

#### Encode Search Query For URL Usage

**URL encode a search query string using the[`urlEncode()`](functions-urlencode.html "urlEncode\(\)") function **

##### Query

logscale
    
    
    search_query = *
    | urlEncode(field=search_query, as=encoded_search_query)

##### Introduction

In this example, the [`urlEncode()`](functions-urlencode.html "urlEncode\(\)") function is used to encode a search query string that may contain special characters, making it safe for use in URLs. 

Example incoming data might look like this: 

@timestamp| search_query  
---|---  
2025-01-15T10:00:00Z| status=error&severity>3  
2025-01-15T10:01:00Z| host=web-server1 #production  
2025-01-15T10:02:00Z| source=*/apache/access.log  
2025-01-15T10:03:00Z| method=GET&path=/api/v1/users  
2025-01-15T10:04:00Z| error message = Connection refused  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         search_query = *

Filters for all events that contain the field search_query. This ensures that only events with search queries are processed. 

  3. logscale
         
         | urlEncode(field=search_query, as=encoded_search_query)

URL encodes the content of the search_query field and returns the encoded result in a new field named encoded_search_query. The function replaces special characters with their percent-encoded equivalents, making the string safe for use in URLs. 

  4. Event Result set.




##### Summary and Results

The query is used to convert search query strings containing special characters into URL-safe format. URL encoding replaces special characters with a percent sign (`%`) followed by a two-digit hexadecimal code that represents the character. 

URL encoding is essential when constructing URLs with dynamic parameters, ensuring that user input does not break URL structure or cause parsing issues in web applications, APIs, and search systems. 

This query is useful, for example, to prepare search queries for use in API calls, URL parameters, or when generating links to LogScale dashboards with specific search criteria. 

Sample output from the incoming example data: 

search_query| encoded_search_query  
---|---  
status=error&severity>3| status%3Derror%26severity%3E3  
host=web-server1 #production| host%3Dweb-server1%20%23production  
source=*/apache/access.log| source%3D%2A%2Fapache%2Faccess.log  
method=GET&path=/api/v1/users| method%3DGET%26path%3D%2Fapi%2Fv1%2Fusers  
error message = Connection refused| error%20message%20%3D%20Connection%20refused  
  
Note that special characters such as spaces, ampersands (`&`), equals signs (`=`), forward slashes (`/`), and hash symbols (`#`) are converted to their percent-encoded equivalents.
