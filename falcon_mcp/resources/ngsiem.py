"""
Contains NGSIEM resources.
"""

SEARCH_NGSIEM_CQL_DOCUMENTATION = """# CQL (CrowdStrike Query Language) authoring guide for `falcon_search_ngsiem`

This tool **executes** a CQL query you supply against CrowdStrike Next-Gen SIEM. It
does not generate CQL for you. Use this guide to construct a valid query before
calling the tool.

CQL is the LogScale/Humio query language. It is a pipe-based, left-to-right data
pipeline — NOT SQL and NOT Splunk SPL. Do not use `SELECT`, `WHERE`, `stats`,
`| top`, `| limit N`, or `event_type = X`. Those are the most common mistakes.

## The pipe model

A query is a chain of stages joined by `|`, read left to right:

```
<filter> | <command> | <command> | ...
```

Each stage takes the events from the stage before it and transforms them. Start by
filtering to the events you want, then pipe into aggregation, sorting, and limiting.

## Core building blocks

- **Tag filter** — restrict to an event type by its tag field:
  `#event_simpleName=ProcessRollup2`
- **Field match** — match on a field value: `UserName=admin`, `ComputerName=*`.
  Combine filters with a space (implicit AND): `#event_simpleName=ProcessRollup2 ComputerName=DC01`
- **Field creation / assignment** — create a new field with `:=`:
  `total := count()` inside a command, or `field := expression`.
- **`groupBy([fields], function=...)`** — aggregate. Group by one or more fields and
  apply an aggregate function. The result columns are the group fields plus the
  function output (default column name `_count` for `count()`):
  `groupBy([ComputerName], function=count())`
- **`sort(field, order=desc)`** — order rows. Order is `asc` or `desc`. `sort()` also
  takes an optional `limit=`: `sort(_count, order=desc, limit=5)`.
- **`head(n)`** — keep `n` events, **oldest first**. Use `tail(n)` for the most recent
  `n` events, or `sort(@timestamp, order=desc, limit=n)` to order by newest. To cap raw
  results, use `head(n)`/`tail(n)` — NOT `| limit n`.
- **`tail(n)`** — keep the most recent `n` events.

## Worked examples

Build from these. They cover the shapes that are easy to get wrong.

**A sample of events (cap the count):**
```
#event_simpleName=ProcessRollup2 | head(20)
```
(`head` returns oldest-first; for the most recent events use `tail(20)` or
`sort(@timestamp, order=desc, limit=20)`.)

**Top N by count (group, then sort, then limit):**
```
#event_simpleName=ProcessRollup2 | groupBy([ComputerName], function=count(as=process_count)) | sort(process_count, order=desc, limit=5)
```

**Two-level grouping (count per pair of fields):**
```
#event_simpleName=ProcessRollup2 | groupBy([ComputerName, FileName], function=count(as=cnt)) | sort(cnt, order=desc, limit=10)
```

**Distinct count** — count unique values of a field. Use the `count()` function with
the field as its first (positional) argument and `distinct=true` (NOT SQL
`COUNT(DISTINCT ...)`):
```
#event_simpleName=ProcessRollup2 | count(ComputerName, distinct=true, as=distinct_hosts)
```

**Filter on an aggregate** — compute a count, then keep only groups above a
threshold. The filter goes AFTER the `groupBy`, matching on the aggregate's output
column (a bare field-comparison stage, not a `WHERE` clause):
```
#event_simpleName=ProcessRollup2 | groupBy([ComputerName], function=count(as=cnt)) | cnt > 100 | sort(cnt, order=desc)
```

**Time bucketing / time series** — bucket events into fixed intervals with
`bucket()` (aka `timeChart`-style). `bucket()` splits the time range into `buckets`
or by `span`, applying an aggregate per bucket:
```
#event_simpleName=ProcessRollup2 | bucket(span=5m, function=count())
```

**Case-insensitive substring match** — match a field against a regex with
`field=/pattern/i` (the `i` flag makes it case-insensitive). To match a FileName
containing `powershell` case-insensitively, then show 10 events:
```
#event_simpleName=ProcessRollup2 FileName=/powershell/i | head(10)
```

**Regex match on a field** — `field=/pattern/` matches the field against a regex. Add
`i` after the closing slash for case-insensitive matching. (The `=~` operator is
something else — it pipes a field into a function like `wildcard()`, not a bare regex.)

## Important: check what the API actually ran

The API returns no CQL parser diagnostic. Anything it cannot recognize as a command is
demoted to a free-text filter stage and run anyway, so a malformed query returns HTTP
200 with unrelated rows or none at all. **A result is not proof your query parsed as
intended.** Two fields in the response's `job` block settle it:

- **`job.parsed_query`** — the API's normalization of the stages it ran. Compare it
  against your intent. `| limit 5` comes back as `| limit | 5`, each stray word now its
  own free-text match. Normalization also turns an implicit-AND space into a `|`, so
  expect that one difference even on a correct query.
- **`job.processed_events`** — how many events the engine read through your filter.

On zero rows: above zero means the job scanned that many events and none matched, which
is a real negative — report it as the answer. Zero means nothing reached the filter, so
check `job.parsed_query`; if it matches your intent the negative is real (a tag or field
value with no data behaves this way), otherwise fix the syntax.

Because the error signal is unreliable, build the query correctly up front rather than
running it to read a parser error. SPL/SQL-isms and a misspelled `#tag` filter are the
usual causes of a surprising result.

## Authoritative external references

For constructs beyond the building blocks above, CrowdStrike publishes the full
LogScale reference. These links are optional depth, not required reading:

- CQL grammar subset (built for programmatically generating queries):
  <https://library.humio.com/lql-grammar/syntax-grammar-guide.html>
- Query language syntax: <https://library.humio.com/data-analysis/syntax.html>
- Query functions reference: <https://library.humio.com/data-analysis/functions.html>
- Getting started: <https://library.humio.com/logscale-getting-started/beginner-introduction.html>
- Real community queries and parsers to crib from:
  <https://github.com/CrowdStrike/logscale-community-content>
"""
