# Decode Redirect URLs in Authentication Logs | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-urldecode-as-3.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Decode Redirect URLs in Authentication Logs

Decode Redirect URLs in Authentication Logs to analyze authentication flows using the urlDecode() function with [_`as`_](https://library.humio.com/data-analysis/functions-urldecode.html#query-functions-urldecode-as) parameter 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    redirect_url = *
    | urlDecode(field=redirect_url, as=decoded_redirect)
    | auth_status="success"

### Introduction

The [`urlDecode()`](https://library.humio.com/data-analysis/functions-urldecode.html) function can be used to decode URL-encoded strings. URL decoding takes the encoded URL and converts the percent-encoded characters back to their original form. This is necessary when processing user input or retrieving data from a URL. 

In this example, the [`urlDecode()`](https://library.humio.com/data-analysis/functions-urldecode.html) function is used to decode URL-encoded redirect URLs in authentication logs to analyze user authentication flows and potential security issues. Using the [_`as`_](https://library.humio.com/data-analysis/functions-urldecode.html#query-functions-urldecode-as) parameter, you can specify a custom field name for the decoded result. 

Example incoming data might look like this: 

@timestamp| auth_status| redirect_url| user_id| source_ip  
---|---|---|---|---  
1683000000000| success| https%3A%2F%2Fapp.example.com%2Fdashboard%3Ftoken%3Dabc123| user1| 10.0.0.1  
1683000001000| failed| https%3A%2F%2Fmalicious.com%2Fphish%3Ftoken%3Dxyz789| user2| 192.168.1.100  
1683000002000| success| https%3A%2F%2Fapp.example.com%2Freports%3Fid%3D456%26view%3Dfull| user3| 10.0.0.2  
1683000003000| success| https%3A%2F%2Fapp.example.com%2Fsettings%3Fmode%3Dadmin| user4| 10.0.0.3  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         redirect_url = *

Filters for events containing the redirect_url field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | urlDecode(field=redirect_url, as=decoded_redirect)

Decodes the URL-encoded values in the redirect_url field and stores the result in a new field named decoded_redirect using the [_`as`_](https://library.humio.com/data-analysis/functions-urldecode.html#query-functions-urldecode-as) parameter. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | auth_status="success"

Filters to include only successful authentication attempts. 

  5. Event Result set.




### Summary and Results

The query is used to analyze post-authentication redirect patterns by decoding redirect URLs from authentication logs. 

This query is useful, for example, to monitor authentication flows, detect suspicious redirect patterns, or track which application areas users access after authentication. 

Sample output from the incoming example data: 

@timestamp| auth_status| decoded_redirect| redirect_url| source_ip| user_id  
---|---|---|---|---|---  
1.683E+12| success| https://app.example.com/dashboard?token=abc123| https%3A%2F%2Fapp.example.com%2Fdashboard%3Ftoken%3Dabc123| 10.0.0.1| user1  
1.683E+12| success| https://app.example.com/reports?id=456&view=full| https%3A%2F%2Fapp.example.com%2Freports%3Fid%3D456%26view%3Dfull| 10.0.0.2| user3  
1.683E+12| success| https://app.example.com/settings?mode=admin| https%3A%2F%2Fapp.example.com%2Fsettings%3Fmode%3Dadmin| 10.0.0.3| user4  
  
Note that the decoded URL is stored in the specified field decoded_redirect and special characters (&, =, ?) are properly decoded.
