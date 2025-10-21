# Hash Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-hash-functions.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Jul 23, 2025

## Hash Query Functions

Functions for creating or validating string hashes. 

**Table: Event and Hash Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`crypto:md5([as], field)`](functions-crypto-md5.html "crypto:md5\(\)")| [_`field`_](functions-crypto-md5.html#query-functions-crypto-md5-field)|  |  Computes a cryptographic MD5-hashing of an input string.   
[`crypto:sha1([as], field)`](functions-crypto-sha1.html "crypto:sha1\(\)")| [_`field`_](functions-crypto-sha1.html#query-functions-crypto-sha1-field)|  |  Computes a cryptographic SHA1-hashing of an input string.   
[`crypto:sha256([as], field)`](functions-crypto-sha256.html "crypto:sha256\(\)")| [_`field`_](functions-crypto-sha256.html#query-functions-crypto-sha256-field)|  |  Computes a cryptographic SHA256-hashing of an input string.   
[`hash([as], field, [limit], [seed])`](functions-hash.html "hash\(\)")| [_`field`_](functions-hash.html#query-functions-hash-field)|  |  Computes a non-cryptographic hash of a list of fields.   
[`tokenHash([as], field)`](functions-tokenhash.html "tokenHash\(\)")| [_`field`_](functions-tokenhash.html#query-functions-tokenhash-field)|  |  Calculates a hash by tokenizing the input string (split by spaces), creating a hash for each token and then added the result together. This generates the same hash value, even if the order of the individual values in the source string is different.   
  
  


Hashes are used to create a consistent string value that can be used for comparison and identification without having to use or manipulate the original values. Hashes are typically used for three different purposes: 

  * General hashing to create unique identifiers, see [General Hashing](functions-hash-functions.html#functions-hash-functions-general "General Hashing")

  * General hashing for PII or comparison, see [Hashing for Privacy or Comparison](functions-hash-functions.html#functions-hash-functions-privacy "Hashing for Privacy or Comparison")

  * Cryptographic hashing for handling passwords or encrypted strings, see [Hashing for Cryptography](functions-hash-functions.html#functions-hash-functions-cryptography "Hashing for Cryptography")




For all hashes, the principle is that the encoded version of the incoming data (the hash) cannot easily be converted back to it's original format, but encoding the same string should result in a consistent hash value. Therefore, computing a new hash of the same string allows it to be used for comparison. 

### General Hashing

The [`hash()`](functions-hash.html "hash\(\)") computes an integer based on one or more incoming field values. This is useful for general hashing on non-sensitive data (for example to create a simplified ID of a complex value) to create consistency, ensure consistent inputs, or to obtain faster performance. 

### Hashing for Privacy or Comparison

Often used when parsing and ingesting data and encoding into a format where the underlying value needs to be anonymized. The [`tokenHash()`](functions-tokenhash.html "tokenHash\(\)") function is useful for anonymizing private data, masking data containing personal and/or sensitive information - also called Personally Identifiable Information (PII). 

The [`tokenHash()`](functions-tokenhash.html "tokenHash\(\)") tokenises the incoming string (separated by spaces), and then creates a hash for each tokenised elements and adds them together. The hash generated in this form will therefore consistent, providing each token in the input is identical, irrespective of the order. For example, the following two log lines contain the same information even though the order of each word is different: 

strings  
---  
abc def ghi  
def ghi abc  
  
Executing [`tokenHash()`](functions-tokenhash.html "tokenHash\(\)") on each will generate the same hash value. 

This can be useful to compare, filter or deduplicate log lines during parsing or querying even though the order of the individual values within a set of key/value pairs might be different. 

### Hashing for Cryptography

Hashes are often used to encode passwords or other security tokens, and LogScale includes tools for creating these hashes to be used for comparison or identification with existing values stored in LogScale. 

The following functions support standard methodologies for these types of hashes: 

  * [`crypto:md5()`](functions-crypto-md5.html "crypto:md5\(\)")

  * [`crypto:sha1()`](functions-crypto-sha1.html "crypto:sha1\(\)")

  * [`crypto:sha256()`](functions-crypto-sha256.html "crypto:sha256\(\)")




Each function takes a string as input and generates a hexadecimal hash representation of the value. 

These functions are not strong encryption keys and should not be used for encryption of text as such.
