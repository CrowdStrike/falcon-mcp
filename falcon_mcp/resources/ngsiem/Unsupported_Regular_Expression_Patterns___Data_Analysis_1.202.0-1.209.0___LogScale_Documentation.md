# Unsupported Regular Expression Patterns | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-regex-unsupported.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

/ [Regular Expression Syntax](syntax-regex.html)

### Unsupported Regular Expression Patterns

The following regular expression patterns and syntax are not supported in LogScale. 

**Table: Unsupported Regular Expression Patterns**

Pattern Group |  Syntax |  Notes   
---|---|---  
`\u{hh..hh}` |  The character with hexadecimal value 0xhh..hh |   
`\N{**`name`**}` |  The unicode character named `name`. |   
`\e` |  The escape character |   
`\C` |  A single byte even in UTF-8 mode |   
`[a-d[m-p]]` |  Intersecting character ranges (a through d or m through p (union)) |   
`[[:**`name`** :]]` |  Named ASCII class inside character class |   
`\h` |  A horizontal whitespace character |   
`\H` |  A non-horizontal whitespace character: [^\h] |   
`\v` |  A vertical whitespace character |   
`\V` |  A non-vertical whitespace character |   
`\p{...}` |  POSIX and Unicode character classes |  Includes `\p{Lower}`, `\p{Upper}`, `\p{ASCII}`, `\p{Alpha}`, `\p{Digit}`, `\p{Alnum}`, `\p{Punct}`, `\p{Graph}`, `\p{Print}`, `\p{Blank}`, `\p{Xdigit}`, `\p{Space}`, `\p{IsLatin}`, `\p{InGreek}`, `\p{IsLatin}`, `\p{InGreek}`, `\p{Lu}`, `\p{IsAlphabetic}`, `\p{Sc}`, `\P{InGreek}`, `[\p{L}&&[^\p{Lu}]]`  
`\b{…}` |  A Unicode boundary of specified type |   
`\G` |  The end of the previous match |   
`\R` |  Any Unicode linebreak sequence |   
`\X` |  Any Unicode extended grapheme cluster |   
`X?+` |  X, once or not at all, possessive |   
`X*+` |  X, zero or more times, possessive |   
`X++` |  X, one or more times, possessive |   
`X{n}+` |  X, exactly n times, possessive |   
`\k<name>` |  Named backreference |   
`X{n,}+` |  X, at least n times, possessive |   
`X{n,m}+` |  X, at least n times but not more than m times, possessive |   
`(?<=X)` |  X, as a zero-width positive lookbehind |   
`(?<!X)` |  X, as a zero-width negative lookbehind |   
`(?>X)` |  X, as an independent, non-capturing (atomic) group. |
