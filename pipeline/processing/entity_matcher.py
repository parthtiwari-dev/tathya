"""Deterministic Phase 2 entity matching against the seed spine."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class EntityDefinition:
    name: str
    type: str
    aliases: tuple[str, ...] = ()

    @property
    def search_terms(self) -> tuple[str, ...]:
        return (self.name, *self.aliases)

    @property
    def specificity(self) -> int:
        return max(len(term) for term in self.search_terms)


DEFAULT_ENTITIES: tuple[EntityDefinition, ...] = (
    EntityDefinition("Government of India", "ministry", ("Union Government", "Central Government", "Centre")),
    EntityDefinition("Prime Minister's Office", "ministry", ("PMO", "PMO India", "Prime Minister Office")),
    EntityDefinition("Ministry of Home Affairs", "ministry", ("MHA", "Home Ministry")),
    EntityDefinition("Ministry of Finance", "ministry", ("Finance Ministry", "MoF")),
    EntityDefinition("Ministry of External Affairs", "ministry", ("MEA", "External Affairs Ministry")),
    EntityDefinition("Ministry of Defence", "ministry", ("Defence Ministry", "MoD")),
    EntityDefinition("Ministry of Education", "ministry", ("Education Ministry", "MoE")),
    EntityDefinition("Ministry of Health and Family Welfare", "ministry", ("Health Ministry", "MoHFW")),
    EntityDefinition("Ministry of Electronics and Information Technology", "ministry", ("MeitY", "IT Ministry")),
    EntityDefinition("Lok Sabha", "ministry", ("House of the People", "Lower House")),
    EntityDefinition("Rajya Sabha", "ministry", ("Council of States", "Upper House")),
    EntityDefinition("Press Information Bureau", "ministry", ("PIB",)),
    EntityDefinition("Reserve Bank of India", "ministry", ("RBI", "Central Bank")),
    EntityDefinition("Income Tax Department", "ministry", ("Income Tax", "IT Department")),
    EntityDefinition("Narendra Modi", "person", ("PM Modi", "Prime Minister Modi")),
    EntityDefinition("Sonam Wangchuk", "person", ("Wangchuk",)),
    EntityDefinition("Anna Hazare", "person", ("Hazare",)),
    EntityDefinition("Amit Shah", "person", ("Union Home Minister Amit Shah",)),
    EntityDefinition("Derek O'Brien", "person", ("Derek OBrien", "Derek O'Brien")),
    EntityDefinition("Om Birla", "person", ("Lok Sabha Speaker Om Birla",)),
    EntityDefinition("Ayushman Bharat", "scheme", ("PM-JAY", "Pradhan Mantri Jan Arogya Yojana")),
    EntityDefinition("Pradhan Mantri Awas Yojana", "scheme", ("PMAY",)),
    EntityDefinition("Mahatma Gandhi National Rural Employment Guarantee Act", "law", ("MGNREGA", "NREGA")),
    EntityDefinition("Digital Personal Data Protection Act, 2023", "law", ("DPDP Act", "Digital Personal Data Protection Act")),
    EntityDefinition("Information Technology Act, 2000", "law", ("IT Act", "Information Technology Act")),
)


def match_entities(text: str, entities: tuple[EntityDefinition, ...] = DEFAULT_ENTITIES) -> list[EntityDefinition]:
    """Return seed entities mentioned in text, using conservative word-boundary matching."""
    matches: list[EntityDefinition] = []
    for entity in entities:
        if any(_contains_term(text, term) for term in entity.search_terms):
            matches.append(entity)
    return sorted(matches, key=lambda entity: entity.specificity, reverse=True)


def _contains_term(text: str, term: str) -> bool:
    if len(term) <= 3 and term.isupper():
        pattern = rf"(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])"
    else:
        pattern = rf"(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None
