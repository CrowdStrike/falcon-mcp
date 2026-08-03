"""
Tool-level filtering for the Falcon MCP server.

Lets an operator shrink a server's blast radius without giving up a whole module.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field

from mcp.types import ToolAnnotations

# Sentinel reason for a tool no rule withheld — it was simply never requested, by
# module gate or allow-list. Not a decision worth reporting, so it stays out of
# Resolution.reasons.
_NOT_REQUESTED = "not-requested"


@dataclass(frozen=True)
class ToolRecord:
    """Everything a policy needs to know about one registered tool.

    Attributes:
        module: Name of the module that registered the tool.
        annotations: The tool's effective MCP annotations, if any.
    """

    module: str
    annotations: ToolAnnotations | None


@dataclass(frozen=True)
class Resolution:
    """Which tools a policy keeps and which it withholds.

    Attributes:
        keep: Prefixed names the policy admits.
        removed: Prefixed names the policy withholds, for any reason.
        withheld_by_rule: The subset of ``removed`` dropped by the deny-list or
            read-only, rather than by never being requested.
        reasons: For each name in ``withheld_by_rule``, the rule that dropped it —
            ``"deny-list"`` or ``"read-only"``. Names the cause for one tool, which
            ``ToolPolicy.describe()`` cannot do because it summarizes the whole server.
    """

    keep: frozenset[str]
    removed: frozenset[str]
    withheld_by_rule: frozenset[str]
    reasons: Mapping[str, str] = field(default_factory=dict)


class ToolPolicy:
    """Resolves a catalog of candidate tools into keep/remove sets.

    Precedence, highest first:

    1. Deny-list — removes a tool unconditionally, even if the allow-list names it.
    2. Read-only — removes every non-read-only tool unconditionally, even if the
       allow-list names it.
    3. Allow-list — adds the tools it names, bypassing the module gate.
    4. Module gate — an unnamed tool survives only if its module was enabled in
       its own right.

    The allow-list is additive, not intersecting: ``--modules detections --tools X``
    registers every detections tool plus X, even when X's module is off. Rules 1 and
    2 still decide any tool the allow-list names, so it can never widen past
    ``--read-only`` or ``--exclude-tools``.

    Tool names are the ``falcon_``-prefixed names clients see. Scope is tools only;
    FQL guide resources are static docs and stay registered — most tool descriptions
    name their guide by URI, so withholding one would point a model at nothing.
    """

    def __init__(
        self,
        read_only: bool = False,
        allowed: set[str] | None = None,
        excluded: set[str] | None = None,
        enabled_modules: set[str] | None = None,
    ):
        """Initialize the policy.

        Args:
            read_only: Keep only tools whose annotations set readOnlyHint=True.
            allowed: Additive allow-list of prefixed tool names.
            excluded: Deny-list of prefixed tool names.
            enabled_modules: Modules the operator enabled in their own right, whose
                tools survive without being named. None disables the module gate,
                so every module contributes its full surface.
        """
        self.read_only = read_only
        self.allowed = frozenset(allowed or ())
        self.excluded = frozenset(excluded or ())
        self.enabled_modules = (
            None if enabled_modules is None else frozenset(enabled_modules)
        )

    @property
    def active(self) -> bool:
        """True if any filtering rule is configured."""
        return self.read_only or bool(self.allowed) or bool(self.excluded)

    def resolve(self, catalog: dict[str, ToolRecord]) -> Resolution:
        """Partition a catalog of candidate tools into keep and removed sets.

        Pure: computed once per registration path from the full catalog, so a
        repeated pass cannot double-count and no per-tool state is carried.

        Args:
            catalog: Prefixed tool name to its owning module and annotations.

        Returns:
            The keep/removed partition of ``catalog``, with the rule-driven removals
            tracked separately and each one's cause recorded.
        """
        keep: set[str] = set()
        removed: set[str] = set()
        reasons: dict[str, str] = {}
        for name, record in catalog.items():
            reason = self._rejection_reason(name, record)
            if reason is None:
                keep.add(name)
                continue
            removed.add(name)
            if reason != _NOT_REQUESTED:
                reasons[name] = reason
        return Resolution(
            keep=frozenset(keep),
            removed=frozenset(removed),
            withheld_by_rule=frozenset(reasons),
            reasons=reasons,
        )

    def _rejection_reason(self, name: str, record: ToolRecord) -> str | None:
        """Name the rule that withholds this tool, or None if the policy keeps it.

        Follows the documented precedence, so the reason is the rule that actually
        decided this tool rather than every rule the server has enabled.

        A tool nothing requested is ``_NOT_REQUESTED`` even when a subtracting rule
        would also have dropped it: ``--tools X`` loads X's whole module to reach X,
        so blaming read-only for a sibling the operator never named would invent a
        decision the allow-list already made by omission.
        """
        requested = name in self.allowed or (
            self.enabled_modules is None or record.module in self.enabled_modules
        )
        if not requested:
            return _NOT_REQUESTED

        if name in self.excluded:
            return "deny-list"

        if self.read_only and self._is_mutating(record):
            return "read-only"

        return None

    def _is_mutating(self, record: ToolRecord) -> bool:
        """True if read-only mode would reject this tool.

        Anything other than readOnlyHint=True counts as mutating, so an unclassified
        tool is withheld rather than exposed. Always False when read-only is off, so
        a mutating tool dropped for another reason is not misattributed to it.
        """
        if not self.read_only:
            return False
        annotations = record.annotations
        return not (annotations and annotations.readOnlyHint is True)

    def describe(self) -> str:
        """Human-readable summary of which rules are in effect."""
        parts = []
        if self.read_only:
            parts.append("read-only")
        if self.allowed:
            parts.append(f"allow-list ({len(self.allowed)} named)")
        if self.excluded:
            parts.append(f"deny-list ({len(self.excluded)} named)")
        return ", ".join(parts) if parts else "none"
