import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langgraph.graph.message import BaseMessage

from src.tools.workflows.utils import merge_dicts, unique_list_merge


class MetadataFilter(TypedDict):
    filterType: str
    filterValue: str
    groupByKey: str


class SRAIdentifier(TypedDict):
    totalCount: int
    single: list[str]


class SRAIdentifiers(TypedDict):
    biosample: list[SRAIdentifier]
    bioproject: list[SRAIdentifier]
    run: list[SRAIdentifier]


class MetadataCounts(TypedDict):
    sra: list[dict[str, str]]
    organism: list[dict[str, str]]
    tissue: list[dict[str, str]]
    disease: list[dict[str, str]]
    sex: list[dict[str, str]]
    stat_organism: list[dict[str, str]]
    virus_family: list[dict[str, str]]
    geo_attribute: list[dict[str, str]]
    biome: list[dict[str, str]]


class MWASResult(TypedDict, total=False):
    bioproject: str
    family: str
    metadata_field: str
    metadata_value: str
    num_true: str
    num_false: str
    mean_rpm_true: str
    mean_rpm_false: str
    sd_rpm_true: str
    sd_rpm_false: str
    fold_change: str
    test_statistic: str
    p_value: str
    # biosamples: list[str]
    # sotus: list[str]
    # tax_species: list[str]


class MetadataCountsReport(TypedDict):
    filter_type: str
    filter_value: str
    filter_count: int


class ValidationReport(TypedDict):
    rating: float
    reasoning: str
    supporting_metadata_counts: list[MetadataCountsReport]
    supporting_mwas_results: list[MWASResult]


class AnomalyReport(TypedDict):
    rating: float
    reasoning: str
    supporting_metadata_counts: list[MetadataCountsReport]
    supporting_mwas_results: list[MWASResult]


class UserInput(TypedDict):
    hypothesis: str
    species_label: str


class State(TypedDict):
    user_input: Annotated[UserInput, merge_dicts]
    messages: Annotated[Sequence[BaseMessage], operator.add]
    palm_ids: Annotated[list[str], unique_list_merge]
    sra_identifiers: Annotated[SRAIdentifiers, merge_dicts]
    metadata_counts: Annotated[MetadataCounts, merge_dicts]
    mwas_results: Annotated[list[MWASResult], operator.add]
    virus_families: Annotated[list[str], unique_list_merge]
    validation_report: Annotated[ValidationReport, merge_dicts]
    anomaly_report: Annotated[AnomalyReport, merge_dicts]
