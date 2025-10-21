# Filter Events Using CIDR Subnets - Example 4 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-cidr-4.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter Events Using CIDR Subnets - Example 4

Filter events using CIDR subnets with negation to match events not in a given IP range 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    !cidr(ipAddress, subnet="192.0.2.0/24")

### Introduction

The [`cidr()`](https://library.humio.com/data-analysis/functions-cidr.html) function can be used to filter events using CIDR subnets and is used for both IPv4 and IPv6 addresses. 

In this example, the [`cidr()`](https://library.humio.com/data-analysis/functions-cidr.html) function is used with a negation to match events for which the `ipAddress` attributes is not in a given IP range. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         !cidr(ipAddress, subnet="192.0.2.0/24")

Matches events for which the ipAddress field is not in the IP range 192.0.2.0/24. 

  3. Event Result set.




### Summary and Results

The query is used to search on specific subnets within the network, uptimizing query performance. The search will only be performed on the IP addresses that does not fall in the range of the specified subnet filter.
