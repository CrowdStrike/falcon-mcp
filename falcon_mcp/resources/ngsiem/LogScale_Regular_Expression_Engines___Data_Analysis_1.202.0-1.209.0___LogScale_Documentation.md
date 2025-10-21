# LogScale Regular Expression Engines | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-regex-engines.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

/ [Regular Expression Syntax](syntax-regex.html)

### LogScale Regular Expression Engines

LogScale provides two regular expression engines - the default v1 engine and a newer v2 engine (enabled with the 'F' flag), with the latter aiming to offer improved performance while maintaining compatibility with common regex engines like PCRE2, Java, and ECMAscript. The v2 engine introduces some key differences in how it handles horizontal and vertical whitespace characters, word-boundary assertions, and in-line flags in alternations, though users experiencing unexpected results can revert to v1 by removing the 'F' flag. 

LogScale supports the following regular expression engines: 

  * LogScale Regular Expression Engine v1 (default) 

The default regular expression is used for all regular expression operations. 

  * LogScale Regular Expression Engine v2 

Enabled by using the `F` flag to a regular expression. For more information, see [LogScale Regular Expression Engine V2](syntax-regex-engines.html#syntax-regex-engines-v2 "LogScale Regular Expression Engine V2")




#### LogScale Regular Expression Engine V2

### Important

LogScale Regular Expression Engine v2 is currently under development. 

  * V2 aims to be faster in general than V1, but there may be regular expressions where the performance is slower. For example, repetition of some character classes concatenated with a suffix, e.g. `[a-zA-Z]+ing`. 

  * Some constructs have different meanings in v2 than the default (v1) regex engine: 

    * Horizontal whitespace character classes. In particular, v2 recognises `\h` as the character class representing horizontal whitespace, whereas the current engine considers `\h` to be the escaping of the character `h`. 

    * Vertical whitespace; `\v` in v2 is understood as the character class representing vertical whitespace, whereas it is being understood as the character `v` by the v1 regex engine, unless the current regex engine fails to compile the rest of the regular expression, in which case it enters a fallback mode, and where `\v` specifically matches the vertical tab character, and neither `v` or the full vertical whitespace character class. 

    * Word-boundary assertions: `\b` in v2 uses the same definition for "word character" as `\w` (that is, "any ASCII letter, digit, or the character '_'"), while v1 uses "any Unicode letter, digit, or the character '_'". 

The v2 behavior is consistent with that of other engines such as PCRE2, Java, and ECMAscript. 

    * In v1 the regular expression engine applies in-line flags to the first branch of an alternation and not the entire implicit group. I.e. the regex: 

logscale Syntax
          
          (?i)Huck[a-z]+
          | Saw[a-z]+

Is interpreted as: 

logscale Syntax
          
          (?:(?i)Huck[a-z]+)
          | Saw[a-z]+

By the current engine, whereas it is interpreted in v2 as: 

logscale Syntax
          
          (?i)(?:Huck[a-z]+
          | Saw[a-z]+)

The latter being behavior consistent with that of other engines such as PCRE2, Java, ECMAscript. 

  * Not all features for v2 are available. In the event of an unavailable feature or syntax, an error message will be shown and the user can either try to modify the regular expression to not use the features or use the default (v1) engine instead. 




If you experience an unexpected result using v2, try using the v1 engine by removing the `F` flag from the use of the regular expression, to see if the default engine produces a different result.
