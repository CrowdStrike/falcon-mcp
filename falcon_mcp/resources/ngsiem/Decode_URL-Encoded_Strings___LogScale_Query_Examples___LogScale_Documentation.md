# Decode URL-Encoded Strings | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-urldecode-default-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Decode URL-Encoded Strings

Decode URL-Encoded Web Request Parameters using the [`urlDecode()`](https://library.humio.com/data-analysis/functions-urldecode.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    request_url = *
    | urlDecode(field=request_url)
    | status_code=200

### Introduction

The [`urlDecode()`](https://library.humio.com/data-analysis/functions-urldecode.html) function can be used to decode URL-encoded strings. URL decoding takes the encoded URL and converts the percent-encoded characters back to their original form. This is necessary when processing user input or retrieving data from a URL. 

In this example, the [`urlDecode()`](https://library.humio.com/data-analysis/functions-urldecode.html) function is used to decode URL-encoded parameters from web requests to analyze user interactions. When used without specifying an output field, the decoded result is automatically stored in a field named _urldecode. 

Example incoming data might look like this: 

@timestamp| request_url| status_code| bytes_sent| response_time  
---|---|---|---|---  
1683000000000| /products?category=electronics&filter=price%3E100%20AND%20brand%3DApple| 200| 2048| 0.23  
1683000001000| /search?q=wireless%20headphones%20with%20noise%20cancelling| 200| 1536| 0.15  
1683000002000| /products?id=12345&return_url=%2Fcart%3Fcheckout%3Dtrue| 500| 512| 1.45  
1683000003000| /search?q=bluetooth%20speakers%20under%20%24100| 200| 1024| 0.  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         request_url = *

Filters for events containing the request_url field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | urlDecode(field=request_url)

Decodes the URL-encoded values in the request_url field, and returns the result in the default output field _urldecode. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | status_code=200

Filters to include only successful requests with status code `200`. 

  5. Event Result set.




### Summary and Results

The query is used to decode URL-encoded web request parameters to analyze user behavior and application patterns. 

This query is useful, for example, to monitor user search patterns, analyze product filtering preferences, or troubleshoot issues with specific URL parameters. 

Sample output from the incoming example data: 

@timestamp| _urldecode| bytes_sent| request_url| response_time| status_code  
---|---|---|---|---|---  
1.683E+12| /products?category=electronics&filter=price>100 AND brand=Apple| 2048| /products?category=electronics&filter=price%3E100%20AND%20brand%3DApple| 0.23| 200  
1.683E+12| /search?q=wireless headphones with noise cancelling| 1536| /search?q=wireless%20headphones%20with%20noise%20cancelling| 0.15| 200  
1.683E+12| /search?q=bluetooth speakers under $100| 1024| /search?q=bluetooth%20speakers%20under%20%24100| 0.18| 200  
  
Note that special characters (>, $, spaces) are properly decoded and failed requests (`status_code != 200`) are excluded.
