import logging

from langgraph.graph import StateGraph, START, END

from src.tools.openvirome import (
    get_results_by_identifiers,
    get_mwas_results_by_identifiers,
)
from src.tools.workflows.state import State


def get_matching_virus_families(state: State) -> State:
    logging.info("get_matching_virus_families node invoked")
    sra_identifiers = state.get("sra_identifiers", {})
    run_ids = sra_identifiers.get("run", {}).get("single", [])
    args = {
        "table": "palm_virome",
        "id_column": "run",
        "ids": run_ids,
        "page_start": 0,
    }
    results = get_results_by_identifiers(**args)
    # filter results to only include rows related to the original query
    # (i.e. exclude all other viruses that co-occur in the matching runs)
    palm_ids = state.get("palm_ids", [])
    matches = [result for result in results if result.get("palm_id") in palm_ids]
    virus_families = set()
    for match in matches:
        family = match.get("tax_family")
        if family:
            virus_families.add(family)

    return {"virus_families": list(virus_families)}


def get_mwas_results(state: State) -> State:
    logging.info("get_mwas_results node invoked")
    sra_identifiers = state.get("sra_identifiers", {})
    bioprojects = sra_identifiers.get("bioproject", {}).get("single", [])
    if not bioprojects:
        logging.warning("No bioprojects found in state")
        return {"messages": [{"role": "assistant", "content": "No bioprojects found."}]}
    virus_families = state.get("virus_families", [])
    if not virus_families:
        logging.warning("No virus families found in state")
        return {
            "messages": [{"role": "assistant", "content": "No virus families found."}]
        }

    args = {
        "id_column": "bioproject",
        "ids": bioprojects,
        "virus_families": virus_families,
        "page_start": 0,
        "page_end": 100,
    }
    mwas_results = get_mwas_results_by_identifiers(**args)
    if not mwas_results:
        logging.warning("No MWAS results found for bioprojects")
        return {
            "messages": [{"role": "assistant", "content": "No MWAS results found."}]
        }

    #  remove fields with large lists (biosamples, sotus, taxSpecies) to reduce size
    mwas_results = [
        {
            k: v
            for k, v in result.items()
            if k not in ["biosamples", "sotus", "taxSpecies"]
        }
        for result in mwas_results
    ]
    return {"mwas_results": mwas_results}


workflow = StateGraph(State)
workflow.add_node(
    node="get_matching_virus_families", action=get_matching_virus_families
)
workflow.add_node(node="get_mwas_results", action=get_mwas_results)
workflow.add_edge(START, "get_matching_virus_families")
workflow.add_edge("get_matching_virus_families", "get_mwas_results")
workflow.add_edge("get_mwas_results", END)
graph = workflow.compile()
