# Regular Expression Syntax | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-regex.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

Content was updated:May 31, 2023

## Regular Expression Syntax

LogScale's regular expression functionality is built on the JitRex engine and shares similar syntax with common regex implementations like Perl, JavaScript, and re2, though some operations are adapted specifically for CrowdStrike Query Language (CQL). The documentation covers supported regex patterns, query functions, and provides detailed comparisons between LogScale's regex implementation and other popular environments including JavaScript, PCRE, and re2. 

The regular expression parser within LogScale is based on the [JitRex regular expression engine](https://github.com/humio/JitRex) which was part of the Jint programming language (see [Jint Programming Language](http://jint.sourceforge.net/)). 

The engine works with very similar syntax to other regular expression engines such as those included with scripting languages like [Perl](https://perldoc.perl.org/perlre), [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions) or Google's [re2](https://github.com/google/re2/wiki/Syntax) engine. 

Due to the nature of querying within the CrowdStrike Query Language (CQL), certain regular expression operations have to be performed in a slightly different way (for example, named groups), but otherwise the syntax will be familiar to users of most regular expression environments. 

For more information on the regular expression support within LogScale: 

  * For information on the supported regular expression syntax, see [Regular Expression Syntax Patterns](syntax-regex-syntax.html "Regular Expression Syntax Patterns"). 

  * For a list of related regular expression functions, see [Regular Expression Query Functions](functions-regular-expression.html "Regular Expression Query Functions"). 

  * For a comparison between the LogScale regex syntax and other environments, see: 

    * [JavaScript Regular Expression Differences](syntax-regex-diffs.html#syntax-regex-diffs-js "JavaScript Regular Expression Differences")

    * [Perl Compatible Regular Expressions (PCRE) Differences](syntax-regex-diffs.html#syntax-regex-diffs-pcre "Perl Compatible Regular Expressions \(PCRE\) Differences")

    * [re2 Regular Expressions Differences](syntax-regex-diffs.html#syntax-regex-diffs-re2 "re2 Regular Expressions Differences")
