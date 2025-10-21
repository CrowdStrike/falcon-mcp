# Find Most Common URLs Returning 404 Errors | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-top-error-urls-count.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Most Common URLs Returning 404 Errors

Identify frequently failing URLs using filtering with the [`top()`](https://library.humio.com/data-analysis/functions-top.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    statuscode = "404"
    | top(url, limit=20)

### Introduction

The [`top()`](https://library.humio.com/data-analysis/functions-top.html) function can be used to count and rank the most frequent values in a field, helping identify patterns and common occurrences in the data. 

In this example, the [`top()`](https://library.humio.com/data-analysis/functions-top.html) function is used to identify the most common URLs that are returning HTTP 404 (Not Found) errors. 

Example incoming data might look like this: 

@timestamp| url| statuscode| client_ip| user_agent  
---|---|---|---|---  
2023-08-06T10:00:00Z| /products/old-item.html| 404| 192.168.1.100| Mozilla/5.0  
2023-08-06T10:01:00Z| /about/team.html| 200| 192.168.1.101| Chrome/90.0  
2023-08-06T10:02:00Z| /products/old-item.html| 404| 192.168.1.102| Safari/14.0  
2023-08-06T10:03:00Z| /blog/2022/post1.html| 404| 192.168.1.103| Firefox/89.0  
2023-08-06T10:04:00Z| /contact.html| 200| 192.168.1.104| Chrome/90.0  
2023-08-06T10:05:00Z| /products/old-item.html| 404| 192.168.1.105| Safari/14.0  
2023-08-06T10:06:00Z| /images/banner.jpg| 404| 192.168.1.106| Mozilla/5.0  
2023-08-06T10:07:00Z| /blog/2022/post1.html| 404| 192.168.1.107| Chrome/90.0  
2023-08-06T10:08:00Z| /products/old-item.html| 404| 192.168.1.108| Firefox/89.0  
2023-08-06T10:09:00Z| /images/banner.jpg| 404| 192.168.1.109| Safari/14.0  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         statuscode = "404"

Filters the events to include only those where the statuscode field equals `404`, representing HTTP Not Found errors. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | top(url, limit=20)

Groups the filtered results by the url field and counts their occurrences. The [_`limit`_](https://library.humio.com/data-analysis/functions-top.html#query-functions-top-limit) parameter is set to show the top 20 most frequent URLs. If no [_`rest`_](https://library.humio.com/data-analysis/functions-top.html#query-functions-top-rest) parameter is specified, any additional URLs beyond the limit are excluded from the results. 

  4. Event Result set.




### Summary and Results

The query is used to identify which URLs most frequently return 404 errors, helping to pinpoint broken links or missing resources on a website. 

This query is useful, for example, to prioritize which broken links to fix first, identify outdated links in external references, or detect potential website structure issues after content migration. 

Sample output from the incoming example data: 

url| _count  
---|---  
/products/old-item.html| 4  
/blog/2022/post1.html| 2  
/images/banner.jpg| 2  
  
Note that the results are automatically sorted in descending order by count, showing the URLs with the most 404 errors first.
