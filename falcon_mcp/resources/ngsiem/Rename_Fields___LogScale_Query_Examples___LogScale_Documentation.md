# Rename Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-rename-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Rename Fields

Rename fields to more readable names using the [`rename()`](https://library.humio.com/data-analysis/functions-rename.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    rename(field=[[src_ip, source_address], [dst_ip, destination_address], [src_port, source_port], [dst_port, destination_port]])

### Introduction

The [`rename()`](https://library.humio.com/data-analysis/functions-rename.html) function can be used to rename fields or column headers to more standardised and readable names. It is possible to rename multiple fields in a single operation. 

In this example, the [`rename()`](https://library.humio.com/data-analysis/functions-rename.html) function is used to rename multiple fields to more readable names. 

Example incoming data might look like this: 

timestamp| src_ip| dst_ip| src_port| dst_port| protocol| bytes_sent| bytes_received  
---|---|---|---|---|---|---|---  
2025-04-01T07:00:00Z| 192.168.1.100| 10.0.0.50| 52431| 443| TCP| 1024| 2048  
2025-04-01T07:00:01Z| 172.16.0.25| 8.8.8.8| 33221| 53| UDP| 64| 512  
2025-04-01T07:00:02Z| 192.168.1.150| 172.16.0.100| 49223| 80| TCP| 2048| 4096  
2025-04-01T07:00:03Z| 10.0.0.75| 192.168.1.1| 55678| 22| TCP| 512| 1024  
2025-04-01T07:00:04Z| 192.168.1.200| 1.1.1.1| 44556| 53| UDP| 64| 512  
2025-04-01T07:00:05Z| 172.16.0.50| 192.168.1.25| 51234| 3389| TCP| 4096| 8192  
2025-04-01T07:00:06Z| 192.168.1.75| 10.0.0.100| 48751| 445| TCP| 2048| 4096  
2025-04-01T07:00:07Z| 10.0.0.25| 172.16.0.75| 53992| 8080| TCP| 1024| 2048  
2025-04-01T07:00:08Z| 192.168.1.125| 8.8.4.4| 35667| 53| UDP| 64| 512  
2025-04-01T07:00:09Z| 172.16.0.100| 192.168.1.50| 47891| 21| TCP| 512| 1024  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         rename(field=[[src_ip, source_address], [dst_ip, destination_address], [src_port, source_port], [dst_port, destination_port]])

Renames the fields src_ip, dst_ip, src_port, and dst_port to more readable field names. The original field names are replaced with the new field names. 

Since [_`field`_](https://library.humio.com/data-analysis/functions-rename.html#query-functions-rename-field) is the unnamed parameter, the query could also look like this: `rename([[src_ip, source_address], [dst_ip, destination_address], [src_port, source_port], [dst_port, destination_port]])`. 

  3. Event Result set.




### Summary and Results

The query is used to rename multiple fields in one single operation. Renaming of fields is used for standardisation, normalization, and readability. Normalizing field names across different data sources is, for example, useful for joins. The [`rename()`](https://library.humio.com/data-analysis/functions-rename.html) function is often used with the [`table()`](https://library.humio.com/data-analysis/functions-table.html) function. 

For renaming existing fields in arrays, see [Rename Existing Fields in Array](examples-array-rename-fields.html "Rename Existing Fields in Array"). 

Sample output from the incoming example data (only showing renamed fields): 

destination_address| destination_port| source_address| source_port  
---|---|---|---  
10.0.0.50| 443| 192.168.1.100| 52431  
8.8.8.8| 53| 172.16.0.25| 33221  
172.16.0.100| 80| 192.168.1.150| 49223  
192.168.1.1| 22| 10.0.0.75| 55678  
1.1.1.1| 53| 192.168.1.200| 44556  
192.168.1.25| 3389| 172.16.0.50| 51234  
10.0.0.100| 445| 192.168.1.75| 48751  
172.16.0.75| 8080| 10.0.0.25| 53992  
8.8.4.4| 53| 192.168.1.125| 35667  
192.168.1.50| 21| 172.16.0.100| 47891
