"""
Dynamic mode for Falcon MCP Server.

Registers three tools total: falcon_search_tools and falcon_execute_tool are the
discovery pair, and falcon_list_enabled_tools is the always-on inventory tool. Together
they reach the full tool surface on demand, keeping the context window small while
every capability stays reachable.
"""

import re
from dataclasses import dataclass, field
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from falcon_mcp.common.fql import FQL_FILTER_HINT_SUFFIX
from falcon_mcp.common.logging import get_logger
from falcon_mcp.filter_hints import FILTER_HINTS, QUERY_STRING_HINTS
from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS, BaseModule
from falcon_mcp.tool_filter import Resolution, ToolPolicy, ToolRecord

logger = get_logger(__name__)

_TOOL_PREFIX = "falcon_"
_NON_ALNUM = re.compile(r"[^a-z0-9]+")

# Words that carry intent but not identity: generic verbs, determiners, and
# conversational filler. They are stripped before the every-token conjunction and
# score nothing outside a tool's own name, because they reach most of the corpus as
# prose ('returns an empty list') and so decide nothing about which tool is wanted.
#
# Membership is a claim about how far a word reaches as prose, not about how generic
# it feels. Words that identify an entity or an operation kind stay out — 'count',
# 'aggregate', 'preview', 'members', 'details' and 'full' all genuinely narrow.
# 'falcon' and 'return'/'returns' are here because they reach very nearly every
# entry: search_corpus is built from the prefixed tool name, and almost every
# docstring has a "Returns" line.
_STOPWORDS = frozenset(
    """
    a an the of for to in on at and or from with by is are was were be been am
    i me my we our us you your it its this that these those there
    do does did done can could would should will shall may might must
    what which who whom whose when where why how
    show list get find search see look tell give fetch return returns retrieve display
    all any some every each single both many much more most
    please thanks thank hey hi ok okay just really actually now right currently
    need needs want wants know knows help helps figure out way best able
    have has had having falcon
    """.split()
)

# How many matches make a block an answer on its own. Below this, the next-wider tier
# is admitted to rescue a right answer the conjunction excluded; at or above it a
# precise query never pays for the wider set.
_TIER_RESCUE_BELOW = 3

# Relative weights only: a name match must outrank any number of description
# matches, so the gap between tiers exceeds the most tokens a query realistically
# carries. A token matching nothing anywhere scores nothing — it is neither
# coverage nor strength.
_SCORE_EXACT_NAME = 1000
_SCORE_NAME_WORD = 10
_SCORE_NAME_SUBSTRING = 5
_SCORE_MODULE_WORD = 3
_SCORE_MODULE_SUBSTRING = 2
_SCORE_DESCRIPTION = 1


def _words(text: str) -> frozenset[str]:
    """Split text into lowercase alphanumeric words."""
    return frozenset(w for w in _NON_ALNUM.split(text.lower()) if w)


def normalize_identifier(name: str) -> str:
    """Reduce a name to lowercase alphanumerics, dropping separators.

    Makes 'Host_Groups', 'host-groups', and 'hostgroups' the same key.
    """
    return _NON_ALNUM.sub("", name.lower())


@dataclass
class ToolEntry:
    """Catalog entry for a single tool."""

    tool: Tool
    module: str
    search_corpus: str = field(init=False)
    name_words: frozenset[str] = field(init=False)
    unprefixed_name: str = field(init=False)
    name_key: frozenset[str] = field(init=False)
    module_words: frozenset[str] = field(init=False)
    module_key: str = field(init=False)

    def __post_init__(self) -> None:
        param_names = " ".join(self.tool.parameters.get("properties", {}).keys())
        self.search_corpus = (
            f"{self.tool.name} {self.tool.description or ''} {self.module} {param_names}"
        ).lower()

        name = self.tool.name.lower()
        self.unprefixed_name = name.removeprefix(_TOOL_PREFIX)
        self.name_words = _words(self.unprefixed_name)
        # Both spellings are accepted as an exact hit so a query can name the tool
        # with or without the server's prefix.
        self.name_key = frozenset(
            {normalize_identifier(name), normalize_identifier(self.unprefixed_name)}
        )
        self.module_words = _words(self.module)
        self.module_key = normalize_identifier(self.module)

    def names_any(self, tokens: list[str]) -> bool:
        """True when any token hits this tool's own name.

        The same two name tiers ``score()`` rewards, asked as a yes/no. Candidate
        selection counts corpus hits without regard to where they land, which lets a
        tool matching several words only in prose qualify while a sibling named for
        the query misses the count — the score already treats a name hit as worth many
        prose hits, and this keeps selection consistent with that.
        """
        return any(t in self.name_words or t in self.unprefixed_name for t in tokens)

    def score(self, tokens: list[str], query_key: str) -> tuple[int, int]:
        """Rank this entry against a tokenized query; higher sorts earlier.

        Returns ``(matched, strength)``. ``matched`` is how many query tokens hit any
        field of this entry — the primary key, so a tool covering more of the query
        outranks one covering less regardless of where the hits land. ``strength`` is
        the weighted sum within that coverage, scoring each token once at the strongest
        field it hits, so a tool named for the query outranks one that only mentions it
        in prose. A token matching nothing adds to neither, and a generic token
        (``_STOPWORDS``) counts only where it hits this tool's own name.
        """
        if query_key and query_key in self.name_key:
            # Sorts above any real query: full coverage plus a strength no per-token
            # sum can reach.
            return (len(tokens) + 1, _SCORE_EXACT_NAME)

        matched = 0
        strength = 0
        for token in tokens:
            if token in self.name_words:
                strength += _SCORE_NAME_WORD
            elif token in self.unprefixed_name:
                strength += _SCORE_NAME_SUBSTRING
            elif token in _STOPWORDS:
                # A generic word reaches most descriptions as prose, so crediting it
                # outside a tool's own name measures docstring wording rather than
                # relevance — enough to let a mutator outrank its read-only sibling.
                continue
            elif token in self.module_words:
                strength += _SCORE_MODULE_WORD
            elif token in self.module_key:
                strength += _SCORE_MODULE_SUBSTRING
            elif token in self.search_corpus:
                strength += _SCORE_DESCRIPTION
            else:
                # Matches nothing anywhere: not coverage, not strength.
                continue
            matched += 1
        return (matched, strength)


class DynamicToolCatalog:
    """Builds a searchable catalog of tools from modules via a scratch FastMCP instance."""

    def __init__(
        self, modules: dict[str, BaseModule], policy: ToolPolicy | None = None
    ) -> None:
        self._entries: dict[str, ToolEntry] = {}
        self._policy = policy or ToolPolicy()
        self.resolution = Resolution(
            keep=frozenset(), removed=frozenset(), withheld_by_rule=frozenset()
        )
        self._build(modules)

    def _build(self, modules: dict[str, BaseModule]) -> None:
        scratch = FastMCP("scratch")

        for module_name, module in modules.items():
            module.register_tools(scratch)

        all_tools: dict[str, Tool] = scratch._tool_manager._tools

        module_tool_names: dict[str, str] = {}
        for module_name, module in modules.items():
            for tool_name in module.tools:
                module_tool_names[tool_name] = module_name

        self.resolution = self._policy.resolve(
            {
                tool_name: ToolRecord(
                    module=module_tool_names.get(tool_name, "unknown"),
                    annotations=tool_obj.annotations,
                )
                for tool_name, tool_obj in all_tools.items()
            }
        )

        for tool_name, tool_obj in all_tools.items():
            # Omitting a withheld tool here is the whole enforcement: it is then
            # absent from falcon_search_tools and 404s in falcon_execute_tool, so the
            # executor is not a bypass.
            if tool_name in self.resolution.removed:
                # Named here because this path never calls server.remove_tool, so
                # --debug would otherwise report a count with no names behind it.
                logger.debug("Withheld tool: %s", tool_name)
                continue
            module_name = module_tool_names.get(tool_name, "unknown")
            self._entries[tool_name] = ToolEntry(tool=tool_obj, module=module_name)

        for module in modules.values():
            module.tools.clear()

        logger.debug("Dynamic catalog built with %d tools", len(self._entries))

    @property
    def entries(self) -> dict[str, ToolEntry]:
        return self._entries

    def get(self, tool_name: str) -> ToolEntry | None:
        return self._entries.get(tool_name)

    def withholding_rule(self, tool_name: str) -> str | None:
        """Name the rule that withholds this tool, or None if no rule did."""
        return self.resolution.reasons.get(tool_name)

    def describe_policy(self) -> str:
        """Summarize every filtering rule the server has enabled."""
        return self._policy.describe()

    def search(
        self,
        query: str = "",
        module: str | None = None,
        limit: int = 50,
        tool_names: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return catalog entries, with the input schema only when tools are named.

        Naming tools is a request for their schemas, so those entries carry
        parameters. A discovery search is not: the caller has yet to choose a tool,
        and the schema is most of an entry's cost. Names the catalog does not hold
        are dropped here; the caller reports them.
        """
        if tool_names:
            # Dedupe while preserving order: a repeated name is one schema, and a
            # duplicate would otherwise inflate the reported total.
            return [
                self._format_entry(entry)
                for entry in (self.get(name) for name in dict.fromkeys(tool_names))
                if entry is not None
            ]
        return [self._format_lean_entry(e) for e in self._matches(query, module)[:limit]]

    def count_matches(self, query: str = "", module: str | None = None) -> int:
        """Count every matching entry, ignoring the result limit.

        Shares _matches with search() so the reported total cannot drift from the
        results returned.
        """
        return len(self._matches(query, module))

    def full_coverage_count(self, query: str = "", module: str | None = None) -> int:
        """How many matches cover every gate token; any others rank below them.

        The composition of the result page, which is what the search hint describes:
        generic words are excluded from the count's basis, so this is coverage of the
        words the query actually narrowed on.
        """
        return len(self._match_set(query, module)[0])

    def relaxed(self, query: str = "", module: str | None = None) -> bool:
        """True when nothing matched every gate token, so every result is partial.

        Once a page can carry both blocks at once this no longer means "the results
        are poor" — only that none of them covered the whole query.
        """
        return self.full_coverage_count(query, module) == 0

    def _match_set(
        self, query: str, module: str | None
    ) -> tuple[list[ToolEntry], list[ToolEntry]]:
        """Split matching entries into a full-coverage block and a partial one.

        Requiring every token narrows well when the query is already tool-shaped, but
        it also lets one incidental word decide eligibility: a generic verb appears as
        prose across most descriptions, so conjoining on it can shrink the set to
        whichever tools happen to use it in passing — excluding the right tool while
        looking precise. Two rules keep that from happening.

        Generic words (``_STOPWORDS``) are dropped before the conjunction, so they
        cannot veto; ranking still sees every token. And when the full-coverage block
        is too small to be a usable answer on its own, entries carrying at least half
        the gate tokens — or any one of them in their own name — join it as a second,
        lower-ranked block, so a near miss is demoted rather than dropped. A query
        whose conjunction already works keeps its narrow set untouched and pays
        nothing for the wider one.
        """
        candidates: list[ToolEntry] = list(self._entries.values())

        if module:
            module_key = normalize_identifier(module)
            candidates = [e for e in candidates if e.module_key == module_key]

        if not query:
            return candidates, []

        tokens = list(_words(query))
        query_key = normalize_identifier(query)

        # Naming a tool is a request for that tool, not a keyword search, so every
        # other entry sharing a token is noise. Membership, not substring, so a short
        # query is not absorbed into an unrelated collapsed name. This mirrors
        # score()'s exact-name short-circuit, and reaches the glued 'searchhosts' form
        # that tokenizing alone cannot.
        if query_key:
            exact = [e for e in candidates if query_key in e.name_key]
            if exact:
                return exact, []

        if not tokens:
            # Punctuation only: nothing to match on, and an empty gate would otherwise
            # make the conjunction vacuously true for every entry.
            return [], []

        # Falling back to the raw words when every one of them is generic keeps the
        # query answerable, but the result is a partial match by construction: these
        # tools carry the words incidentally, which is the whole reason the words do
        # not gate. Reporting it as full coverage would tell the model the opposite —
        # 'a' is a substring of every corpus, so it would present the entire catalog
        # as a precise match.
        gate = [t for t in tokens if t not in _STOPWORDS]
        if not gate:
            return [], [
                e for e in candidates if all(t in e.search_corpus for t in tokens)
            ]
        # At least half the gate tokens, rounding up: enough to demote a near miss
        # rather than drop it, without admitting every tool that shares one word.
        threshold = (len(gate) + 1) // 2

        full: list[ToolEntry] = []
        partial: list[ToolEntry] = []
        for entry in candidates:
            hits = sum(1 for t in gate if t in entry.search_corpus)
            if hits == len(gate):
                full.append(entry)
            elif hits >= threshold or entry.names_any(gate):
                partial.append(entry)

        if len(full) >= _TIER_RESCUE_BELOW:
            # A full-coverage block this size is already an answer, so a precise query
            # pays nothing for the wider set.
            return full, []
        if len(full) + len(partial) >= _TIER_RESCUE_BELOW:
            return full, partial
        # Still too thin to answer with. Drop to any single gate token, so a match the
        # threshold excluded is demoted rather than lost — otherwise a near miss by one
        # tool would suppress the rescue for all of them, which is the conjunction's own
        # failure one tier down. Generic tokens stay out even here: the shortest of them
        # ('a', 'on') are substrings of every corpus, so admitting them would return the
        # whole catalog on the strength of a letter.
        covered = {e.tool.name for e in full}
        return full, [
            e
            for e in candidates
            if e.tool.name not in covered and any(t in e.search_corpus for t in gate)
        ]

    def _matches(self, query: str, module: str | None) -> list[ToolEntry]:
        full, partial = self._match_set(query, module)

        if not query:
            # Browsing has no relevance signal, so order by name to stay stable
            # across processes.
            return sorted(full, key=lambda e: e.tool.name)

        tokens = list(_words(query))
        query_key = normalize_identifier(query)
        # Full coverage first, so a tool matching every gate token always outranks one
        # that missed a word. Within a block, coverage leads: a tool matching more of
        # the query's words is the more relevant answer, and strength then orders by
        # where the hits landed. When both still tie — a bare noun matches a read-only
        # tool and its destructive sibling identically (search_iocs vs remove_iocs) —
        # read-only wins, so ordering never steers an agent to the mutator first. Only
        # then do ties break toward the least-qualified name and finally
        # alphabetically, since catalog insertion order follows a set of module names
        # and is not stable across processes.
        full_names = {e.tool.name for e in full}

        def sort_key(e: ToolEntry) -> tuple[int, int, int, int, bool, str]:
            matched, strength = e.score(tokens, query_key)
            annotations = e.tool.annotations
            read_only = annotations.readOnlyHint if annotations else True
            return (
                0 if e.tool.name in full_names else 1,
                -matched,
                -strength,
                len(e.name_words),
                not read_only,
                e.tool.name,
            )

        return sorted(full + partial, key=sort_key)

    @staticmethod
    def _append_hint(params: dict[str, Any], key: str, text: str) -> None:
        """Append a hint to one parameter's description, spacing it correctly.

        A description already ending in '.' just needs a space before the hint;
        otherwise the separator supplies the period too.
        """
        if key not in params:
            return
        desc = params[key]["description"]
        separator = " " if desc.endswith(".") else ". "
        params[key]["description"] = desc + separator + text

    @staticmethod
    def _base_entry(entry: ToolEntry) -> dict[str, Any]:
        """The fields every entry carries, with or without the input schema."""
        annotations = entry.tool.annotations
        return {
            "name": entry.tool.name,
            "module": entry.module,
            "description": entry.tool.description or "",
            "read_only": annotations.readOnlyHint if annotations else True,
            "destructive": annotations.destructiveHint if annotations else False,
        }

    def _format_lean_entry(self, entry: ToolEntry) -> dict[str, Any]:
        """Describe a tool without its input schema.

        Deciding which tool is right needs the name, what it does, and whether it
        mutates — not the parameters. The schema is roughly two thirds of a full
        entry, so omitting it is what makes a wide result window affordable. The
        absent ``parameters`` key is itself the signal that a second call, naming the
        tool, is needed before executing it.
        """
        return self._base_entry(entry)

    def _format_entry(self, entry: ToolEntry) -> dict[str, Any]:
        """Describe a tool including its input schema and filter-syntax hints."""
        params_summary = {}
        properties = entry.tool.parameters.get("properties", {})
        required = entry.tool.parameters.get("required", [])

        for name, schema in properties.items():
            param_info: dict[str, Any] = {
                "type": schema.get("type", "any"),
                "required": name in required,
                "description": schema.get("description", ""),
            }
            examples = schema.get("examples")
            if examples:
                param_info["examples"] = examples
            params_summary[name] = param_info

        hint = FILTER_HINTS.get(entry.tool.name)
        if hint:
            self._append_hint(params_summary, "filter", hint)
        self._append_hint(params_summary, "filter", FQL_FILTER_HINT_SUFFIX)

        # CQL tools use a `query_string` param instead of an FQL `filter`; inject the
        # curated CQL hint there so dynamic mode reaches the model the same way.
        cql_hint = QUERY_STRING_HINTS.get(entry.tool.name)
        if cql_hint:
            self._append_hint(params_summary, "query_string", cql_hint)

        return {**self._base_entry(entry), "parameters": params_summary}

    @staticmethod
    def summarize_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
        summary = {}
        properties = parameters.get("properties", {})
        required = parameters.get("required", [])

        for name, schema in properties.items():
            summary[name] = {
                "type": schema.get("type", "any"),
                "required": name in required,
                "description": schema.get("description", ""),
            }
        return summary


class DynamicMode:
    """Registers the discovery pair: falcon_search_tools + falcon_execute_tool.

    falcon_list_enabled_tools, the third dynamic-mode tool, is registered by the
    server itself since it is always on, in both modes.
    """

    def __init__(
        self,
        modules: dict[str, BaseModule],
        server: FastMCP,
        policy: ToolPolicy | None = None,
    ) -> None:
        self.server = server
        self.catalog = DynamicToolCatalog(modules, policy)

    def register(self) -> None:
        self.server.add_tool(
            self._search_tools,
            name="falcon_search_tools",
            annotations=READ_ONLY_ANNOTATIONS,
            structured_output=False,
        )
        self.server.add_tool(
            self._execute_tool,
            name="falcon_execute_tool",
            annotations=None,
            structured_output=False,
        )

    def _entries_remain(self) -> bool:
        """True if the catalog still holds at least one Falcon tool.

        Filtering can withhold every tool (``--tools <mutator> --read-only``), which
        changes what is honest to tell a model about looking elsewhere.
        """
        return bool(self.catalog.entries)

    async def _search_tools(
        self,
        query: Annotated[
            str,
            Field(
                description="Keywords to search across tool names, descriptions, module names, and parameter names.",
            ),
        ] = "",
        module: Annotated[
            str | None,
            Field(
                description=(
                    "Restrict results to one module (e.g., 'hosts', 'detections'). Case "
                    "and separators are ignored, so 'Host_Groups' and 'hostgroups' both "
                    "work. Call falcon_list_enabled_tools for the module names this "
                    "server accepts. Pass it with no query to browse every tool that "
                    "module contributes here, which may be a subset of the module's "
                    "full surface."
                ),
            ),
        ] = None,
        limit: Annotated[
            int,
            Field(
                ge=1,
                le=500,
                description="Maximum number of results to return (default: 50, max: 500). Ignored when tool_names is given.",
            ),
        ] = 50,
        tool_names: Annotated[
            list[str] | None,
            Field(
                description=(
                    "Exact tool names to return full parameter schemas for. Use this after "
                    "a keyword search has told you which tool you want; pass two or more "
                    "names to compare candidates in one call. Overrides query, module, and "
                    "limit."
                ),
            ),
        ] = None,
    ) -> dict[str, Any]:
        """Find a Falcon tool by keyword, then get its parameters before executing it.

        This is the entry point in dynamic mode, and it works in two steps.

        Search first: pass keywords in query, or a module name (or nothing at all) to
        browse. Results are ordered by likely relevance, but the order is a keyword
        match with no view of your intent: read each tool's description and its
        read_only / destructive flags and pick the one that fits, rather than taking
        the first row. These results deliberately carry no parameters.

        Then get the schema: call this tool again with tool_names set to the names you
        picked, and those entries come back with every parameter (type, required,
        description, examples, and filter-syntax hints where the tool takes a filter),
        ready to pass to falcon_execute_tool. Naming several at once compares them.

        Read total and truncated to tell a capped list from a complete one, and hint
        for how much of the query each result matched.
        """
        # Naming tools is a schema lookup, not a search, so the match-set fields
        # describe what was asked for rather than a query nobody ran.
        if tool_names:
            return self._describe_named(tool_names)

        results = self.catalog.search(query=query, module=module, limit=limit)
        total = self.catalog.count_matches(query=query, module=module)
        truncated = total > len(results)

        if not results:
            # Name every narrowing term: a module-scoped miss is not an empty server.
            criteria = []
            if query:
                criteria.append(f"matching '{query}'")
            if module:
                criteria.append(f"in module '{module}'")
            subject = f"No tool {' '.join(criteria)} is" if criteria else "No tool is"
            if not self._entries_remain():
                hint = (
                    "This server has no Falcon tools available: its configuration "
                    f"({self.catalog.describe_policy()}) withholds all of them. Tell the "
                    "user the server is configured with no tools available rather than "
                    "searching again."
                )
            elif self.catalog.resolution.withheld_by_rule:
                hint = (
                    f"{subject} available on this server, which is "
                    f"running with a tool filter ({self.catalog.describe_policy()}). "
                    "Call falcon_list_enabled_tools for what is available. The "
                    "capability may exist but be withheld by configuration — tell the "
                    "user that rather than trying more searches."
                )
            else:
                hint = (
                    f"{subject} available on this server. Call "
                    "falcon_list_enabled_tools for the full inventory. If the capability "
                    "you need is genuinely absent, it was not enabled on this server — "
                    "tell the user rather than trying more searches."
                )
            return {
                "results": [],
                "total": 0,
                "truncated": False,
                "hint": hint,
            }

        envelope: dict[str, Any] = {
            "results": results,
            "total": total,
            "truncated": truncated,
        }
        hints: list[str] = []
        full_on_page = min(
            self.catalog.full_coverage_count(query=query, module=module), len(results)
        )
        partial_on_page = len(results) - full_on_page
        if not full_on_page:
            hints.append(
                "No tool matched every word, so these match at least one of them, "
                "ordered by likely relevance. Read the descriptions and pick the one "
                "that fits rather than assuming the capability is missing."
            )
        elif partial_on_page:
            hints.append(
                f"The first {full_on_page} match every word; the remaining "
                f"{partial_on_page} match only some of them and rank below. Read the "
                "descriptions rather than assuming the top result is the right tool."
            )
        if truncated:
            hints.append(
                f"Showing {len(results)} of {total}. Call falcon_list_enabled_tools "
                "for all names, or narrow with query."
            )
        # Always last, so it is the instruction the model reads on the way out.
        hints.append(
            "These results carry no parameters. Pick the tool you want, then call "
            "falcon_search_tools again with tool_names=[its name] to get the "
            "parameters before calling falcon_execute_tool."
        )
        envelope["hint"] = " ".join(hints)
        return envelope

    def _describe_named(self, tool_names: list[str]) -> dict[str, Any]:
        """Return full schemas for the named tools, reporting any this server lacks.

        total counts what came back rather than the catalog, because no query ran:
        there is no wider match set for it to describe.
        """
        results = self.catalog.search(tool_names=tool_names)
        found = {entry["name"] for entry in results}
        missing = [name for name in tool_names if name not in found]
        envelope: dict[str, Any] = {
            "results": results,
            "total": len(results),
            "truncated": False,
        }
        if missing:
            # Returning fewer entries than were asked for, silently, reads as those
            # tools having no parameters rather than being unavailable. A withheld tool
            # and one that never existed need different words, and a single call can
            # name both.
            withheld = {
                name: rule
                for name in missing
                if (rule := self.catalog.withholding_rule(name)) is not None
            }
            hints: list[str] = []
            if withheld:
                named = ", ".join(f"{n} ({r})" for n, r in withheld.items())
                hints.append(
                    f"Withheld by this server's configuration: {named}. The capability "
                    "is not missing — tell the user it is disabled by configuration "
                    "rather than searching again."
                )
            unknown = [name for name in missing if name not in withheld]
            if unknown:
                hints.append(
                    f"Not available on this server: {', '.join(unknown)}. Search by "
                    "keyword for the right name, or call falcon_list_enabled_tools "
                    "for the full inventory."
                )
            envelope["hint"] = " ".join(hints)
        return envelope

    async def _execute_tool(
        self,
        tool_name: str = Field(
            description="Exact tool name to execute (from falcon_search_tools results).",
        ),
        parameters: dict[str, Any] = Field(
            default_factory=dict,
            description="Tool parameters as a JSON object.",
        ),
    ) -> Any:
        """Execute a Falcon tool by name with the given parameters.

        Call falcon_search_tools first: search by keyword to find the tool, then call
        it again with tool_names to get the parameter schema and the mutation risk
        (read_only / destructive fields). Do not execute destructive tools without
        confirming the user's intent.
        Results are returned in full — use each tool's own limit parameter to control
        response volume. Empty result sets return a dict with results, pagination, and
        hint keys rather than a bare empty list.
        """
        entry = self.catalog.get(tool_name)
        if not entry:
            # A tool the policy withheld is absent from the catalog exactly like one
            # that never existed. Say which it is, or the model reports an operator
            # config choice to the user as a missing product capability.
            rule = self.catalog.withholding_rule(tool_name)
            if rule is not None:
                # Promising other tools on an empty surface sends the model hunting.
                remainder = (
                    "Do not try to achieve the same effect through a different tool, "
                    "though other tools remain available for other work."
                    if self._entries_remain()
                    else "This server currently has no Falcon tools available at all, "
                    "so do not look for an alternative."
                )
                return {
                    "error": f"'{tool_name}' exists on this server but its configuration "
                    f"withholds it ({rule}). The capability is not missing — tell the user "
                    f"it is disabled by this server's configuration. {remainder}",
                    "tool": tool_name,
                }
            return {
                "error": f"Unknown tool: '{tool_name}'. Use falcon_search_tools to discover valid names."
            }

        try:
            result = await entry.tool.run(parameters)
        except Exception as e:
            error_type = type(e).__name__
            if "validation" in error_type.lower() or "valid" in str(e).lower():
                return {
                    "error": f"Parameter validation failed: {e}",
                    "tool": tool_name,
                    "expected_parameters": self.catalog.summarize_parameters(
                        entry.tool.parameters
                    ),
                }
            return {"error": f"Execution failed: {e}", "tool": tool_name}

        return self._normalize_empty(result)

    def _normalize_empty(self, result: Any) -> Any:
        """Return a helpful hint when a tool produces an empty result set."""
        if isinstance(result, list) and len(result) == 0:
            return {
                "results": [],
                "pagination": {"total": 0, "next": None},
                "hint": "No records returned. Call falcon_search_tools with tool_names to review the tool parameters if this is unexpected.",
            }
        return result
