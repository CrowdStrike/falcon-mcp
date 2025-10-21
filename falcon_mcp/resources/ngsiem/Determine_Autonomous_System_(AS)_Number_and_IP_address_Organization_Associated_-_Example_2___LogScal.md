# Determine Autonomous System (AS) Number and IP address/Organization Associated - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-asn-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Determine Autonomous System (AS) Number and IP address/Organization Associated - Example 2

Determine the autonomous system (AS) number and organization associated with a given IP address 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    asn(field=ipaddr,as=address)

### Introduction

The [`asn()`](https://library.humio.com/data-analysis/functions-asn.html) function assumes the default values ip for input parameter and outputs to new fields based on this field name. This can be modified by using the [_`as`_](https://library.humio.com/data-analysis/functions-asn.html#query-functions-asn-as) parameter. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         asn(field=ipaddr,as=address)

Adds the fields address.asn and address.org (based on the field ipaddr) to the event. 

  3. Event Result set.




### Summary and Results

The query is used to automatically add an AS number to its associated IP address (and organization with that IP address associated). Knowing the Autonomos System Number of the associated IP addresses is useful to identify registered owner/organizations of an IP range. When using the ASN search to query a list of IP addresses, it is possible to mix IPv4 and IPv6 addresses within the one query.
