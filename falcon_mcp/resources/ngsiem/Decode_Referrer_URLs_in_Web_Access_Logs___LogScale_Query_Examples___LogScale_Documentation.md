# Decode Referrer URLs in Web Access Logs | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-urldecode-assign-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Decode Referrer URLs in Web Access Logs

Decode Referrer URLs in Web Access Logs to analyze traffic sources using the [`urlDecode()`](https://library.humio.com/data-analysis/functions-urldecode.html) function with assignment operator 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    referrer = *
    | decodedUrl := urlDecode(field=referrer)
    | conversion=true

### Introduction

The [`urlDecode()`](https://library.humio.com/data-analysis/functions-urldecode.html) function can be used to decode URL-encoded strings. URL decoding takes the encoded URL and converts the percent-encoded characters back to their original form. This is necessary when processing user input or retrieving data from a URL. 

In this example, the [`urlDecode()`](https://library.humio.com/data-analysis/functions-urldecode.html) function is used to decode URL-encoded referrer URLs to analyze traffic sources and marketing campaign effectiveness. Using the assignment operator (:=), you can specify a custom field name for the decoded result. 

Example incoming data might look like this: 

@timestamp| referrer| campaign_id| conversion| revenue  
---|---|---|---|---  
1683000000000| https%3A%2F%2Fwww.google.com%2Fsearch%3Fq%3Dbest%20cloud%20security| camp_001| true| 199.99  
1683000001000| https%3A%2F%2Fwww.facebook.com%2Fads%3Fcampaign%3Dsecurity2023| camp_002| false| 0.00  
1683000002000| https%3A%2F%2Ftwitter.com%2Fstatus%3Fpromo%3Dspring50| camp_003| true| 299.99  
1683000003000| https%3A%2F%2Fwww.google.com%2Fsearch%3Fq%3Dantivirus%20enterprise| camp_001| false| 0.00  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         referrer = *

Filters for events containing the referrer field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | decodedUrl := urlDecode(field=referrer)

Decodes the URL-encoded values in the referrer field and assigns the result to a new field named decodedUrl. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["Expression"] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | conversion=true

Filters to include only successful conversions. 

  5. Event Result set.




### Summary and Results

The query is used to analyze traffic sources that led to successful conversions by decoding referrer URLs. 

This query is useful, for example, to track which search terms or social media campaigns are driving successful conversions, or to analyze the effectiveness of different marketing channels. 

Sample output from the incoming example data: 

@timestamp| campaign_id| conversion| decodedUrl| referrer| revenue  
---|---|---|---|---|---  
1.683E+12| camp_001| TRUE| https://www.google.com/search?q=best cloud security| https%3A%2F%2Fwww.google.com%2Fsearch%3Fq%3Dbest%20cloud%20security| 199.99  
1.683E+12| camp_003| TRUE| https://twitter.com/status?promo=spring50| https%3A%2F%2Ftwitter.com%2Fstatus%3Fpromo%3Dspring50| 299.99  
  
Note that the original encoded referrer field remains unchanged.
