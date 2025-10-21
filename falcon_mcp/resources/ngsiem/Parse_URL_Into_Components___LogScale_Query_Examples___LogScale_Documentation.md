# Parse URL Into Components | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-parseuri-url-components.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Parse URL Into Components

Extract individual components from a URL string using the parseUri() [`parseUri()`](https://library.humio.com/data-analysis/functions-parseuri.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    parseUri(field="url")

### Introduction

The [`parseUri()`](https://library.humio.com/data-analysis/functions-parseuri.html) function can be used to parse a URL string and extract its individual components into separate fields. This is useful for analyzing URL structures, monitoring web traffic patterns, and securing web applications by inspecting URL components. 

In this example, the [`parseUri()`](https://library.humio.com/data-analysis/functions-parseuri.html) function is used to break down a URL into its constituent parts, such as scheme, hostname, port, path, and query parameters. 

Example incoming data might look like this: 

#fields @timestamp| url  
---|---  
1683000000000000000| https://admin:password123@api.example.com:8443/v2/users?active=true&role=admin#section1  
1683000001000000000| http://user:pass@test.domain.com/path/to/resource?param=value  
1683000002000000000| https://api.service.com:443/api/v1/data  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
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




### Summary and Results

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

The parsed URL components can be effectively visualized in a table using the [`table()`](https://library.humio.com/data-analysis/functions-table.html) function: `| table([ ["URL Components", "Values"], ["URL", url], ["Scheme", url.scheme], ["Username", url.username], ["Password", url.password], ["Hostname", url.hostname], ["Port", url.port], ["Path", url.path], ["Query", url.query], ["Fragment", url.fragment] ])`.
