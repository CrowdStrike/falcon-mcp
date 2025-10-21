# SHA-256 Hash Multiple Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-crypto-sha256-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## SHA-256 Hash Multiple Fields

SHA-256 hash multiple fields using the [`crypto:sha256()`](https://library.humio.com/data-analysis/functions-crypto-sha256.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    crypto:sha256(field=[a,b,c])

### Introduction

In LogScale it is possible to encode strings using different algorithms such as MD5, SHA-1 and SHA-256 and create a hash; also called a fingerprint. The MD5 hash function is the weakest of the three, whereas SHA-256 is the strongest. The [`crypto:sha256()`](https://library.humio.com/data-analysis/functions-crypto-sha256.html) function is used to create the SHA-256 hash by taking a string of any length and encoding it into a 256-bit fingerprint. The fingerprint is returned as hexadecimal characters. Encoding the same string using the SHA-256 algorithm will always result in the same 256-bit hash output (64 hexadecimal digits). 

In this example, the [`crypto:sha256()`](https://library.humio.com/data-analysis/functions-crypto-sha256.html) function is used to hash the fields a,b,c and return the result into a field named `_sha256`. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         crypto:sha256(field=[a,b,c])

Performs a cryptographic SHA256-hashing of a,b,c. The _`field`_ argument can be omitted to write: [`crypto:sha1([a,b,c])`](https://library.humio.com/data-analysis/functions-crypto-sha1.html)

  3. Event Result set.




### Summary and Results

The query is used to encode a string using the SHA-256 hash. When called with multiple values, [`crypto:sha256()`](https://library.humio.com/data-analysis/functions-crypto-sha256.html) function creates a single SHA-256 sum from the combined value of the supplied fields. Combining fields in this way and converting to an SHa-256 can be an effective method of creating a unique ID for a given fieldset which could be used to identify a specific event type. The SHA-256 is reproducible (for example, supplying the same values will produce the same SHA-256 sum), and so it can sometimes be an effective method of creating unique identifier or lookup fields for a [`join()`](https://library.humio.com/data-analysis/functions-join.html) across two different datasets.
