# Encode Search Query For URL Usage | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-urlencode-search-query.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Encode Search Query For URL Usage

URL encode a search query string using the [`urlEncode()`](https://library.humio.com/data-analysis/functions-urlencode.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    search_query = *
    | urlEncode(field=search_query, as=encoded_search_query)

### Introduction

The [`urlEncode()`](https://library.humio.com/data-analysis/functions-urlencode.html) function can be used to encode text strings so they can be safely included as parameters in URLs. This is particularly useful when you need to pass LogScale queries or other text containing special characters through web URLs. 

The [`urlEncode()`](https://library.humio.com/data-analysis/functions-urlencode.html) function applies URL encoding to convert special characters in strings to their percent-encoded equivalents according to RFC 3986. URL encoding is necessary when processing data passed via HTML forms, as such data may contain special characters (for example `/`, `.`,` #`) that could, for example, have special meanings in URLs, be invalid characters for URLs or be altered during transfer. 

In this example, the [`urlEncode()`](https://library.humio.com/data-analysis/functions-urlencode.html) function is used to encode a search query string that may contain special characters, making it safe for use in URLs. 

Example incoming data might look like this: 

@timestamp| search_query  
---|---  
2025-01-15T10:00:00Z| status=error&severity>3  
2025-01-15T10:01:00Z| host=web-server1 #production  
2025-01-15T10:02:00Z| source=*/apache/access.log  
2025-01-15T10:03:00Z| method=GET&path=/api/v1/users  
2025-01-15T10:04:00Z| error message = Connection refused  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         search_query = *

Filters for all events that contain the field search_query. This ensures that only events with search queries are processed. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | urlEncode(field=search_query, as=encoded_search_query)

URL encodes the content of the search_query field and returns the encoded result in a new field named encoded_search_query. The function replaces special characters with their percent-encoded equivalents, making the string safe for use in URLs. 

  4. Event Result set.




### Summary and Results

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
