# SHA-256 Hash a Field With a Given Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-crypto-sha256-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## SHA-256 Hash a Field With a Given Value

SHA-256 hash a field with a given value using the [`crypto:sha256()`](https://library.humio.com/data-analysis/functions-crypto-sha256.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    a := "Hello, world!"
    | crypto:sha256(a)

### Introduction

In LogScale it is possible to encode strings using different algorithms such as MD5, SHA-1 and SHA-256 and create a hash; also called a fingerprint. The MD5 hash function is the weakest of the three, whereas SHA-256 is the strongest. The [`crypto:sha256()`](https://library.humio.com/data-analysis/functions-crypto-sha256.html) function is used to create the SHA-256 hash by taking a string of any length and encoding it into a 256-bit fingerprint. The fingerprint is returned as hexadecimal characters. Encoding the same string using the SHA-256 algorithm will always result in the same 256-bit hash output (64 hexadecimal digits). 

In this example, the [`crypto:sha256()`](https://library.humio.com/data-analysis/functions-crypto-sha256.html) function is used to hash the field a with value `Hello, world!` and convert the result into `_sha256`. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         a := "Hello, world!"

Assigns the value `Hello, world!` to the field a. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | crypto:sha256(a)

Performs a cryptographic SHA-256-hashing of a:= "Hello, world!". The output value would be `_sha256 = "315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3"`

  4. Event Result set.




### Summary and Results

The query is used to encode a string using the SHA-256 hash. The hash generators `MD5`, `SHA-1`, and `SHA-256` are, for example, useful for encoding passwords or representing other strings in the system as hashed values.
