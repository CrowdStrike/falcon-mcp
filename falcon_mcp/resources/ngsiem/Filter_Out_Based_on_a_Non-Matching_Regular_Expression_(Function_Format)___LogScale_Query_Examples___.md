# Filter Out Based on a Non-Matching Regular Expression (Function Format) | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-negative-regex-filter-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter Out Based on a Non-Matching Regular Expression (Function Format)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    responsesize > 2000
    | not regex("/falcon-logscale-.*/",field=url)

### Introduction

Typically a regular expression is used to filter events based on a value that the regular expression matches. The opposite can also be achieved, filtering events by those that do not match the regular expression by using the function form of a regula expression match. 

This example searches weblog data looking for large log entries that are larger than a specified size but not in a specific directory. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         responsesize > 2000

Fine 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | not regex("/falcon-logscale-.*/",field=url)

Negates the regular expression match, here filtering out any filename that contains the prefix `falcon-logscale`, but returning all other matching URLs. 

  4. Event Result set.




### Summary and Results

For example, given the following events: 

@timestamp| #repo| #type| @id| @ingesttimestamp| @rawstring| @timestamp.nanos| @timezone| client| httpversion| method| responsesize| statuscode| url| userid  
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6401_1719982743| 2024-07-03T04:59:41| 192.168.1.240 - - [03/07/2024:04:59:03 +0000] "GET /js/htmllinkhelp.js HTTP/1.1" 200 23| 0| Z| 192.168.1.240| HTTP/1.1| GET| 23| 200| /js/htmllinkhelp.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6400_1719982743| 2024-07-03T04:59:41| 192.168.1.24 - - [03/07/2024:04:59:03 +0000] "GET /data-analysis-1.100/css-images/external-link.svg HTTP/1.1" 200 1072| 0| Z| 192.168.1.24| HTTP/1.1| GET| 1072| 200| /data-analysis-1.100/css-images/external-link.svg| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6399_1719982743| 2024-07-03T04:59:41| 192.168.1.209 - - [03/07/2024:04:59:03 +0000] "GET /js/htmllinkhelp.js HTTP/1.1" 304 -| 0| Z| 192.168.1.209| HTTP/1.1| GET| -| 304| /js/htmllinkhelp.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6398_1719982743| 2024-07-03T04:59:41| 192.168.1.39 - - [03/07/2024:04:59:03 +0000] "GET /data-analysis/js/java.min.js HTTP/1.1" 304 -| 0| Z| 192.168.1.39| HTTP/1.1| GET| -| 304| /data-analysis/js/java.min.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6397_1719982743| 2024-07-03T04:59:41| 192.168.1.62 - - [03/07/2024:04:59:03 +0000] "GET /falcon-logscale-cloud/js/php.min.js HTTP/1.1" 200 6397| 0| Z| 192.168.1.62| HTTP/1.1| GET| 6397| 200| /falcon-logscale-cloud/js/php.min.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6396_1719982743| 2024-07-03T04:59:41| 192.168.1.206 - - [03/07/2024:04:59:03 +0000] "GET /integrations/js/theme.js HTTP/1.1" 200 14845| 0| Z| 192.168.1.206| HTTP/1.1| GET| 14845| 200| /integrations/js/theme.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6395_1719982743| 2024-07-03T04:59:41| 192.168.1.1 - - [03/07/2024:04:59:03 +0000] "GET /data-analysis/js/json.min.js HTTP/1.1" 200 496| 0| Z| 192.168.1.1| HTTP/1.1| GET| 496| 200| /data-analysis/js/json.min.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6394_1719982743| 2024-07-03T04:59:41| 192.168.1.252 - - [03/07/2024:04:59:03 +0000] "GET /falcon-logscale-cloud/js/java.min.js HTTP/1.1" 200 2739| 0| Z| 192.168.1.252| HTTP/1.1| GET| 2739| 200| /falcon-logscale-cloud/js/java.min.js| -  
  
Might return the following values: 

@timestamp| #repo| #type| @id| @ingesttimestamp| @rawstring| @timestamp.nanos| @timezone| client| httpversion| method| responsesize| statuscode| url| userid  
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_2_6541_1719982743| 2024-07-03T05:03:48| 192.168.1.231 - - [03/07/2024:04:59:03 +0000] "GET /logscale-repo-schema/js/corp.js HTTP/1.1" 200 18645| 0| Z| 192.168.1.231| HTTP/1.1| GET| 18645| 200| /logscale-repo-schema/js/corp.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_2_6538_1719982743| 2024-07-03T05:03:48| 192.168.1.69 - - [03/07/2024:04:59:03 +0000] "GET /data-analysis-1.100/images/dashboards.png HTTP/1.1" 200 152590| 0| Z| 192.168.1.69| HTTP/1.1| GET| 152590| 200| /data-analysis-1.100/images/dashboards.png| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_2_6535_1719982743| 2024-07-03T05:03:47| 192.168.1.154 - - [03/07/2024:04:59:03 +0000] "GET /integrations/js/theme.js HTTP/1.1" 200 14845| 0| Z| 192.168.1.154| HTTP/1.1| GET| 14845| 200| /integrations/js/theme.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_2_6534_1719982743| 2024-07-03T05:03:47| 192.168.1.58 - - [03/07/2024:04:59:03 +0000] "GET /integrations/images/extrahop.png HTTP/1.1" 200 10261| 0| Z| 192.168.1.58| HTTP/1.1| GET| 10261| 200| /integrations/images/extrahop.png| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_2_6527_1719982743| 2024-07-03T05:03:47| 192.168.1.164 - - [03/07/2024:04:59:03 +0000] "GET /integrations/images/zeek.png HTTP/1.1" 200 4392| 0| Z| 192.168.1.164| HTTP/1.1| GET| 4392| 200| /integrations/images/zeek.png| -
