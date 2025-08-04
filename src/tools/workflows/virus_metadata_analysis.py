import logging

from langgraph.graph import StateGraph, START, END

from src.tools.openvirome import (
    get_sra_identifiers_by_filters,
    get_palm_ids_by_species,
    get_similar_palm_ids_neo4j,
)
from src.tools.llm import run_llm_completion
from src.tools.workflows.metadata_counts import graph as metadata_counts_graph
from src.tools.workflows.mwas import graph as mwas_graph
from src.tools.workflows.state import State, ValidationReport, AnomalyReport
from src.prompts.metadata_analysis import (
    validate_hypothesis_system_prompt,
    validate_hypothesis_user_prompt,
    anomaly_detection_system_prompt,
    anomaly_detection_user_prompt,
)


def get_palm_ids_from_species_label(state: State) -> State:
    logging.info("get_palm_ids_from_species_label node invoked")
    species_label = state["user_input"].get("species_label", "")
    if not species_label:
        logging.warning("No species label provided in state")
        return {
            "messages": [{"role": "assistant", "content": "No species label provided."}]
        }

    percent_identity = 80
    palm_ids_response = get_palm_ids_by_species(species_label, percent_identity)
    palm_ids = palm_ids_response.get("data", [])
    palm_ids = [palm_id[0] for palm_id in palm_ids[1:]]
    return {"palm_ids": palm_ids}


def get_evol_similar_palm_ids(state: State) -> State:
    logging.info("get_evol_similar_palm_ids node invoked")
    if not state["palm_ids"]:
        logging.warning("No palm_ids found in state")
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": "No palm_ids available to find similar viruses.",
                }
            ]
        }

    percent_identity = 80
    evol_similar_viruses = get_similar_palm_ids_neo4j(
        state["palm_ids"], percent_identity
    )
    evol_similar_viruses = evol_similar_viruses.get("data", [])
    evol_similar_viruses = [virus[1] for virus in evol_similar_viruses[1:]]

    # only return unique palm_ids excluding the original palm_ids
    evol_similar_viruses = [
        palm_id for palm_id in evol_similar_viruses if palm_id not in state["palm_ids"]
    ]
    evol_similar_viruses = list(set(evol_similar_viruses))

    if not evol_similar_viruses:
        logging.warning("No similar viruses found for palm_ids")
        return {}
    return {"palm_ids": evol_similar_viruses}


def get_matching_sra_ids(state: State) -> State:
    logging.info("get_matching_sra_ids node invoked")
    if not state["palm_ids"]:
        logging.warning("No palm_ids found in state")
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": "No palm_ids available to find matching SRA accessions.",
                }
            ]
        }
    filters = [
        {"filterType": "sotu", "filterValue": palm_id, "groupByKey": "sotu"}
        for palm_id in state["palm_ids"]
    ]
    sra_identifiers = get_sra_identifiers_by_filters(filters, palmprint_only=True)

    if not sra_identifiers:
        logging.warning("No SRA accessions found for palm_ids")
        return {
            "messages": [{"role": "assistant", "content": "No SRA accessions found."}]
        }
    return {"sra_identifiers": sra_identifiers}


def llm_validate_hypothesis(state: State) -> State:
    logging.info("llm_validate_hypothesis node invoked")
    hypothesis = state["user_input"].get("hypothesis", "")
    virus_species = state["user_input"].get("species_label", "")
    metadata_counts = state.get("metadata_counts", {})
    mwas_results = state.get("mwas_results", {})
    if not hypothesis or (not metadata_counts and not mwas_results):
        logging.warning("Missing hypothesis, metadata counts, or MWAS results in state")
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": (
                        "Missing hypothesis, metadata counts, or MWAS results in state"
                    ),
                }
            ]
        }

    # clean up metadata counts and mwas results for LLM processing
    hypothesis = hypothesis + f". Given virus species: {virus_species}"
    metadata_counts = {
        k: v[:20] for k, v in metadata_counts.items() if isinstance(v, list)
    }
    system_prompt = validate_hypothesis_system_prompt()
    user_prompt = validate_hypothesis_user_prompt(
        hypothesis=hypothesis,
        metadata_counts=metadata_counts,
        mwas_results=mwas_results,
    )
    prompt_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = run_llm_completion(
        messages=prompt_messages,
        model_name="gpt-4o",
        temperature=0.0,
        structured_output=ValidationReport,
    )
    if not response:
        logging.warning("No response from LLM for hypothesis validation")
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": "No validation report generated.",
                }
            ]
        }

    return {"validation_report": response}


def llm_identify_anomalies(state: State) -> State:
    logging.info("llm_identify_anomalies node invoked")
    hypothesis = state["user_input"].get("hypothesis", "")
    virus_species = state["user_input"].get("species_label", "")
    metadata_counts = state.get("metadata_counts", {})
    mwas_results = state.get("mwas_results", {})
    if not hypothesis or not metadata_counts or not mwas_results:
        logging.warning("Missing hypothesis, metadata counts, or MWAS results in state")
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": (
                        "Missing hypothesis, metadata counts, or MWAS results in state"
                    ),
                }
            ]
        }

    # clean up metadata counts and mwas results for LLM processing
    hypothesis = hypothesis + f". Given virus species: {virus_species}"
    metadata_counts = {
        k: v[:20] for k, v in metadata_counts.items() if isinstance(v, list)
    }

    system_prompt = anomaly_detection_system_prompt()
    user_prompt = anomaly_detection_user_prompt(
        hypothesis=hypothesis,
        metadata_counts=metadata_counts,
        mwas_results=mwas_results,
    )
    prompt_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = run_llm_completion(
        messages=prompt_messages,
        model_name="gpt-4o",
        temperature=0.0,
        structured_output=AnomalyReport,
    )
    if not response:
        logging.warning("No response from LLM for anomaly identification")
        return {
            "messages": [{"role": "assistant", "content": "No anomalies identified."}]
        }

    return {"anomaly_report": response}


def get_supporting_documents(state: State) -> State:
    logging.info("get_supporting_documents node invoked")
    anomaly_report = state.get("anomaly_report", {})
    validation_report = state.get("validation_report", {})
    if not anomaly_report and not validation_report:
        logging.warning("No anomaly or validation report found in state")
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": "No anomaly or validation report found.",
                }
            ]
        }
    return {}


workflow = StateGraph(State)

workflow.add_node(
    node="get_palm_ids_from_species_label",
    action=get_palm_ids_from_species_label,
)
workflow.add_node(node="get_evol_similar_palm_ids", action=get_evol_similar_palm_ids)
workflow.add_node(node="get_matching_sra_ids", action=get_matching_sra_ids)
workflow.add_node(node="get_metadata_counts", action=metadata_counts_graph)
workflow.add_node(node="get_mwas_results", action=mwas_graph)
workflow.add_node(node="llm_validate_hypothesis", action=llm_validate_hypothesis)
workflow.add_node(node="llm_identify_anomalies", action=llm_identify_anomalies)
workflow.add_node(node="get_supporting_documents", action=get_supporting_documents)

workflow.add_edge(START, "get_palm_ids_from_species_label")
workflow.add_edge("get_palm_ids_from_species_label", "get_evol_similar_palm_ids")
workflow.add_edge("get_evol_similar_palm_ids", "get_matching_sra_ids")
workflow.add_edge("get_matching_sra_ids", "get_metadata_counts")
workflow.add_edge("get_matching_sra_ids", "get_mwas_results")
workflow.add_edge("get_metadata_counts", "llm_validate_hypothesis")
workflow.add_edge("get_metadata_counts", "llm_identify_anomalies")
workflow.add_edge("get_mwas_results", "llm_validate_hypothesis")
workflow.add_edge("get_mwas_results", "llm_identify_anomalies")
workflow.add_edge("llm_identify_anomalies", "get_supporting_documents")
workflow.add_edge("llm_validate_hypothesis", "get_supporting_documents")
workflow.add_edge("get_supporting_documents", END)

graph = workflow.compile()


## Save the graph image for documentation or visualization purposes
# from src.tools.workflows.utils import save_graph_image
# save_graph_image(graph, "./docs/img/virus_metadata_analysis_graph.png")
