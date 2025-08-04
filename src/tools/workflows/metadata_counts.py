import logging

from langgraph.graph import StateGraph, START, END

from src.tools.openvirome import (
    get_counts_by_identifiers,
)
from src.tools.workflows.state import State


DEFAULT_ARGS = {
    "sort_by_column": "count",
    "sort_by_direction": "desc",
    "page_start": 0,
    "page_end": 1000,
    "palmprint_only": True,
}


def get_sra_id_counts(state: State) -> State:
    logging.info("get_sra_id_counts node processing input")
    if not state["sra_identifiers"]:
        logging.warning("No SRA accessions found in state")
        return {
            "messages": [{"role": "assistant", "content": "No SRA accessions found."}]
        }

    if not all(
        key in state["sra_identifiers"] for key in ["run", "biosample", "bioproject"]
    ):
        logging.error("SRA identifiers structure is missing required keys")
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": "Invalid SRA identifiers structure.",
                }
            ]
        }

    run_ids = state["sra_identifiers"].get("run", [])
    biosamples = state["sra_identifiers"].get("biosample", [])
    bioprojects = state["sra_identifiers"].get("bioproject", [])

    if not run_ids and not biosamples and not bioprojects:
        logging.warning("No SRA identifiers found in state")
        return {
            "messages": [{"role": "assistant", "content": "No SRA identifiers found."}]
        }

    sra_counts = {
        "run": run_ids.get("totalCount", []),
        "biosample": biosamples.get("totalCount", []),
        "bioproject": bioprojects.get("totalCount", []),
    }
    metadata_counts = {
        "sra": sra_counts,
    }
    return {"metadata_counts": metadata_counts}


def get_organism_counts(state: State) -> State:
    logging.info("get_organism_counts node invoked")

    sra_identifiers = state.get("sra_identifiers", {})
    run_ids = sra_identifiers.get("run", {}).get("single", [])
    args = {
        "table": "sra",
        "group_by": "organism",
        "id_column": "run",
        "ids": run_ids,
        **DEFAULT_ARGS,
    }

    results = get_counts_by_identifiers(**args)
    metadata_counts = {
        "organism": results,
    }
    return {"metadata_counts": metadata_counts}


def get_tissue_counts(state: State) -> State:
    logging.info("get_tissue_counts node invoked")
    sra_identifiers = state.get("sra_identifiers", {})
    biosamples = sra_identifiers.get("biosample", {}).get("single", [])
    args = {
        "table": "biosample_tissue",
        "group_by": "tissue",
        "id_column": "biosample",
        "ids": biosamples,
        **DEFAULT_ARGS,
    }

    results = get_counts_by_identifiers(**args)
    metadata_counts = {
        "tissue": results,
    }
    return {"metadata_counts": metadata_counts}


def get_disease_counts(state: State) -> State:
    logging.info("get_disease_counts node invoked")
    sra_identifiers = state.get("sra_identifiers", {})
    biosamples = sra_identifiers.get("biosample", {}).get("single", [])
    args = {
        "table": "biosample_disease",
        "group_by": "do_label",
        "id_column": "biosample",
        "ids": biosamples,
        **DEFAULT_ARGS,
    }
    results = get_counts_by_identifiers(**args)
    metadata_counts = {
        "disease": results,
    }
    return {"metadata_counts": metadata_counts}


def get_sex_counts(state: State) -> State:
    logging.info("get_sex_counts node invoked")
    sra_identifiers = state.get("sra_identifiers", {})
    biosamples = sra_identifiers.get("biosample", {}).get("single", [])
    args = {
        "table": "biosample_sex",
        "group_by": "sex",
        "id_column": "biosample",
        "ids": biosamples,
        **DEFAULT_ARGS,
    }
    results = get_counts_by_identifiers(**args)
    metadata_counts = {
        "sex": results,
    }
    return {"metadata_counts": metadata_counts}


def get_stat_host_counts(state: State) -> State:
    logging.info("get_stat_host_counts node invoked")
    sra_identifiers = state.get("sra_identifiers", {})
    run_ids = sra_identifiers.get("run", {}).get("single", [])
    args = {
        "table": "sra_stat",
        "group_by": "stat_host_order",
        "id_column": "run",
        "ids": run_ids,
        **DEFAULT_ARGS,
    }
    results = get_counts_by_identifiers(**args)
    metadata_counts = {
        "stat_organism": results,
    }
    return {"metadata_counts": metadata_counts}


def get_virus_family_counts(state: State) -> State:
    logging.info("get_virus_family_counts node invoked")
    sra_identifiers = state.get("sra_identifiers", {})
    run_ids = sra_identifiers.get("run", {}).get("single", [])
    args = {
        "table": "palm_virome",
        "group_by": "tax_family",
        "id_column": "run",
        "ids": run_ids,
        **DEFAULT_ARGS,
    }
    results = get_counts_by_identifiers(**args)
    metadata_counts = {
        "virus_family": results,
    }
    return {"metadata_counts": metadata_counts}


def get_geo_attribute_counts(state: State) -> State:
    logging.info("get_geo_attribute_counts node invoked")
    sra_identifiers = state.get("sra_identifiers", {})
    biosamples = sra_identifiers.get("biosample", {}).get("single", [])
    args = {
        "table": "biosample_geographical_location",
        "group_by": "geo_attribute_value",
        "id_column": "biosample",
        "ids": biosamples,
        **DEFAULT_ARGS,
    }
    results = get_counts_by_identifiers(**args)
    metadata_counts = {
        "geo_attribute": results,
    }
    return {"metadata_counts": metadata_counts}


def get_biome_counts(state: State) -> State:
    logging.info("get_biome_counts node invoked")
    sra_identifiers = state.get("sra_identifiers", {})
    biosamples = sra_identifiers.get("biosample", {}).get("single", [])
    args = {
        "table": "bgl_gm4326_gp4326",
        "group_by": "biome_attribute_value",
        "id_column": "biosample",
        "ids": biosamples,
        **DEFAULT_ARGS,
    }
    results = get_counts_by_identifiers(**args)
    biome_id_to_name = {
        "WWF_TEW_BIOME_01": "Tropical & Subtropical Moist Broadleaf Forests",
        "WWF_TEW_BIOME_02": "Tropical & Subtropical Dry Broadleaf Forests",
        "WWF_TEW_BIOME_03": "Tropical & Subtropical Coniferous Forests",
        "WWF_TEW_BIOME_04": "Temperate Broadleaf & Mixed Forests",
        "WWF_TEW_BIOME_05": "Temperate Conifer Forests",
        "WWF_TEW_BIOME_06": "Boreal Forests/Taiga",
        "WWF_TEW_BIOME_07": "Tropical & Subtropical Grasslands, Savannas & Shrublands",
        "WWF_TEW_BIOME_08": "Temperate Grasslands, Savannas & Shrublands",
        "WWF_TEW_BIOME_09": "Flooded Grasslands & Savannas",
        "WWF_TEW_BIOME_10": "Montane Grasslands & Shrublands",
        "WWF_TEW_BIOME_11": "Tundra",
        "WWF_TEW_BIOME_12": "Mediterranean Forests, Woodlands & Scrub",
        "WWF_TEW_BIOME_13": "Deserts & Xeric Shrublands",
        "WWF_TEW_BIOME_14": "Mangroves",
        "WWF_TEW_BIOME_98": "Ocean",
        "WWF_TEW_BIOME_99": "Ocean",
    }
    # Map biome names to full names
    results_clean = results.copy()
    for result in results_clean:
        biome_id = result.get("name")
        if biome_id in biome_id_to_name:
            result["name"] = biome_id_to_name[biome_id]

    metadata_counts = {
        "biome": results_clean,
    }
    return {"metadata_counts": metadata_counts}


workflow = StateGraph(State)
workflow.add_node(node="get_sra_id_counts", action=get_sra_id_counts)
workflow.add_node(node="get_tissue_counts", action=get_tissue_counts)
workflow.add_node(node="get_disease_counts", action=get_disease_counts)
workflow.add_node(node="get_organism_counts", action=get_organism_counts)
workflow.add_node(node="get_sex_counts", action=get_sex_counts)
workflow.add_node(node="get_stat_host_counts", action=get_stat_host_counts)
workflow.add_node(node="get_virus_family_counts", action=get_virus_family_counts)
workflow.add_node(node="get_geo_attribute_counts", action=get_geo_attribute_counts)
workflow.add_node(node="get_biome_counts", action=get_biome_counts)

workflow.add_edge(START, "get_sra_id_counts")
workflow.add_edge(START, "get_tissue_counts")
workflow.add_edge(START, "get_disease_counts")
workflow.add_edge(START, "get_organism_counts")
workflow.add_edge(START, "get_sex_counts")
workflow.add_edge(START, "get_stat_host_counts")
workflow.add_edge(START, "get_virus_family_counts")
workflow.add_edge(START, "get_geo_attribute_counts")
workflow.add_edge(START, "get_biome_counts")

workflow.add_edge("get_sra_id_counts", END)
workflow.add_edge("get_tissue_counts", END)
workflow.add_edge("get_disease_counts", END)
workflow.add_edge("get_organism_counts", END)
workflow.add_edge("get_sex_counts", END)
workflow.add_edge("get_stat_host_counts", END)
workflow.add_edge("get_virus_family_counts", END)
workflow.add_edge("get_geo_attribute_counts", END)
workflow.add_edge("get_biome_counts", END)

graph = workflow.compile()
