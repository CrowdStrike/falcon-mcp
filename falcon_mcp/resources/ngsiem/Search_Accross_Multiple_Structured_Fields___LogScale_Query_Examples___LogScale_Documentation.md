# Search Accross Multiple Structured Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-transpose-within-groupby.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search Accross Multiple Structured Fields

Search across multiple structured fields using the transpose() function within groupBy() 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2[/Filter/] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    groupBy(@id, function=transpose())
    | row[1] = /httpd/
    | groupBy(column)

### Introduction

The [`transpose()`](https://library.humio.com/data-analysis/functions-transpose.html) function is used to transform table data by converting columns into rows. 

By transposing event set, the information can be viewed and summarized in a more human readable form. In this example, the [`transpose()`](https://library.humio.com/data-analysis/functions-transpose.html) function is used within a [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function to search across multiple structured fields in the [HUMIO](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository. 

Example incoming data might look like this: 

host| @rawstring  
---|---  
MAIL01| 2025-03-18T10:14:47.142Z MAIL01 httpd[61789]: 192.168.0.198 - - [2025-03-13:23:05:48 +0800] "GET /api/v2/products/search HTTP/1.1" 200 33456  
LON-SRV01| 2025-03-18T10:14:46.940Z LON-SRV01 httpd[60123]: 192.168.0.198 - - [2025-03-13:20:50:14 +0500] "GET /uploads/documents/terms.pdf HTTP/1.1" 401 36912  
MAIL01| 2025-03-18T10:14:46.691Z MAIL01 httpd[51234]: 192.168.0.198 - - [2025-03-13:12:50:16 -0300] "GET /downloads/mobile/app-v2.1.apk HTTP/1.1" 403 1234  
SYD-SRV01| 2025-03-18T10:14:46.542Z SYD-SRV01 httpd[45678]: 192.168.1.123 - - [2025-03-13:19:30:17 +0400] "GET /uploads/avatars/default.png HTTP/1.1" 404 61789  
PROD-SQL01| 2025-03-18T10:14:46.141Z PROD-SQL01 httpd[56789]: 192.168.1.245 - - [2025-03-13:17:30:38 +0200] "GET /uploads/avatars/default.png HTTP/1.1" 200 13456  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2[/Filter/] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(@id, function=transpose())

Groups events by unique @id values, applies the [`transpose()`](https://library.humio.com/data-analysis/functions-transpose.html) function for each group, converting row values into column headers. A new row-based structure for each @id field is created. 

After using [`transpose()`](https://library.humio.com/data-analysis/functions-transpose.html), the data might look like this: 

@id| column| row[1]  
---|---|---  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| @timezone| Z  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| app| httpd[56789]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| host| PROD-SQL01  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886,msg, 192.168.1.245 - - [2025-03-13:17:30:38 +0200] "GET /uploads/avatars/default.png HTTP/1.1" 200 13456|  |   
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| priority| 34  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| version| 1  
  
  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2[/Filter/] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | row[1] = /httpd/

Filters for events where row[1] regex matches the value `httpd`. 

After filtering, the data might look like this (@rawstring has been removed from the below for clarity): 

@id| column| row[1]  
---|---|---  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| app| httpd[56789]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_528_1742292886| app| httpd[45678]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_531_1742292886| app| httpd[51234]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_536_1742292886| app| httpd[60123]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_540_1742292887| app| httpd[61789]:  
  
  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2[/Filter/] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(column)

Groups results by the column field, showing which original fields contained the value `httpd`, and makes a count of matches per field, returning the counted results in a field named _count. The final groupBy(column) removes duplicate entries. 

  5. Event Result set.




### Summary and Results

The query is used to search across multiple structured fields in the [HUMIO](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository to show where `httpd` appears most often. It makes results more readable, identifies field patterns, and is very useful for statistical analysis. 

Sample output from the incoming example data: 

column| _count  
---|---  
@rawstring| 5  
app| 5
