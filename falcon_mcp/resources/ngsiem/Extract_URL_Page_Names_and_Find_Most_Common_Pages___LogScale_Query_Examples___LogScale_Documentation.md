# Extract URL Page Names and Find Most Common Pages | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-regex-extract-url-page-count.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract URL Page Names and Find Most Common Pages

Extract page names from URLs and count their frequency using [`regex()`](https://library.humio.com/data-analysis/functions-regex.html) function with [`top()`](https://library.humio.com/data-analysis/functions-top.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    regex(regex="/.*/(?<url_page>\S+\.page)", field=url)
    | top(url_page, limit=12, rest=others)

### Introduction

The [`regex()`](https://library.humio.com/data-analysis/functions-regex.html) function can be used to extract specific parts of strings using regular expressions with named capture groups. The extracted values are stored in new fields named after the capture groups. 

In this example, the [`regex()`](https://library.humio.com/data-analysis/functions-regex.html) function is used to extract page names from URLs, and then [`top()`](https://library.humio.com/data-analysis/functions-top.html) is used to identify the most frequently accessed pages. 

Example incoming data might look like this: 

@timestamp| url| status_code| user_agent  
---|---|---|---  
2023-08-06T10:00:00Z| https://example.com/products/item1.page| 200| Mozilla/5.0  
2023-08-06T10:01:00Z| https://example.com/about/company.page| 200| Chrome/90.0  
2023-08-06T10:02:00Z| https://example.com/products/item2.page| 404| Safari/14.0  
2023-08-06T10:03:00Z| https://example.com/products/item1.page| 200| Firefox/89.0  
2023-08-06T10:04:00Z| https://example.com/contact/support.page| 200| Chrome/90.0  
2023-08-06T10:05:00Z| https://example.com/about/company.page| 200| Safari/14.0  
2023-08-06T10:06:00Z| https://example.com/products/item3.page| 200| Mozilla/5.0  
2023-08-06T10:07:00Z| https://example.com/products/item1.page| 200| Chrome/90.0  
2023-08-06T10:08:00Z| https://example.com/about/company.page| 200| Firefox/89.0  
2023-08-06T10:09:00Z| https://example.com/products/item2.page| 404| Safari/14.0  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         regex(regex="/.*/(?<url_page>\S+\.page)", field=url)

Extracts the page name including the `.page` extension from the url field using a regular expression with a named capture group url_page. The pattern matches any characters up to the last forward slash (`.*`), followed by any non-whitespace characters (`\S+`) ending with `.page`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | top(url_page, limit=12, rest=others)

Groups the results by the extracted url_page field and counts their occurrences. The [_`limit`_](https://library.humio.com/data-analysis/functions-top.html#query-functions-top-limit) parameter is set to show the top 12 results, and the [_`rest`_](https://library.humio.com/data-analysis/functions-top.html#query-functions-top-rest) parameter combines all remaining values into a group named `others`. 

  4. Event Result set.




### Summary and Results

The query is used to analyze the most frequently accessed pages on a website by extracting page names from URLs and counting their occurrences. 

This query is useful, for example, to identify popular content, monitor user behavior patterns, or detect potential issues with specific pages that receive high traffic. 

Sample output from the incoming example data: 

url_page| _count  
---|---  
item1.page| 3  
company.page| 3  
item2.page| 2  
support.page| 1  
item3.page| 1  
  
Note that the results are automatically sorted in descending order by count, showing the most frequently accessed pages first.
