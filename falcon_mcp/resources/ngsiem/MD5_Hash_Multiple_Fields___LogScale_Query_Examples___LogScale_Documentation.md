# MD5 Hash Multiple Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-crypto-md5-1-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## MD5 Hash Multiple Fields

MD5 hash multiple fields using the [`crypto:md5()`](https://library.humio.com/data-analysis/functions-crypto-md5.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    crypto:md5(field=[a,b,c])

### Introduction

In LogScale it is possible to encode strings using different algorithms such as `MD5`, `SHA-1`, and `SHA-256` and create a hash; also called a fingerprint. The MD5 hash function is the weakest of the three, whereas SHA-256 is the strongest. The [`crypto:md5()`](https://library.humio.com/data-analysis/functions-crypto-md5.html) function is used to create the MD5 hash by taking a string of any length and encoding it into a 128-bit fingerprint. The fingerprint is returned as hexadecimal characters. Encoding the same string using the MD5 algorithm will always result in the same 128-bit hash output (16 hexadecimal digits). 

In this example, the [`crypto:md5()`](https://library.humio.com/data-analysis/functions-crypto-md5.html) function is used to hash the fields a,b,c and return the result into a field named `_md5`. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         crypto:md5(field=[a,b,c])

Performs a cryptographic MD5-hashing of a,b,c. The _`field`_ argument can be omitted to write: [`crypto:md5([a,b,c])`](https://library.humio.com/data-analysis/functions-crypto-md5.html)

  3. Event Result set.




### Summary and Results

The query is used to encode a string using the MD5 hash. When called with multiple values, [`crypto:md5()`](https://library.humio.com/data-analysis/functions-crypto-md5.html) function creates a single MD5 sum from the combined value of the supplied fields. Combining fields in this way and converting to an MD5 can be an effective method of creating a unique ID for a given fieldset which could be used to identify a specific event type. The MD5 is reproducible (for example, supplying the same values will produce the same MD5 sum), and so it can sometimes be an effective method of creating unique identifier or lookup fields for a [`join()`](https://library.humio.com/data-analysis/functions-join.html) across two different datasets.
