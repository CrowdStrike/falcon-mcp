package fql

// FQLFilterHintSuffix is appended to every filter-param description in dynamic
// mode, reminding the model of FQL's boolean/quoting rules. Ported verbatim from
// the Python FQL_FILTER_HINT_SUFFIX.
const FQLFilterHintSuffix = "FQL uses + for AND and , for OR (not the words AND/OR). Values must be single-quoted."
