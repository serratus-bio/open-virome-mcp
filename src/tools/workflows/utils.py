def save_graph_image(graph, outfile: str = "graph_image.png") -> None:
    """
    Save the langgraph graph as a PNG image.
    Args:
        graph: langgraph graph object
        outfile: path to save the image
    """
    print(f"Saving graph image to {outfile}")
    with open(outfile, "wb") as file:
        png_data = graph.get_graph(xray=True).draw_mermaid_png()
        file.write(png_data)


def merge_dicts(a: dict, b: dict) -> dict:
    if a is None:
        return b or {}
    if b is None:
        return a or {}
    return {**a, **b}


def unique_list_merge(a: list, b: list) -> list:
    return list(dict.fromkeys(a + b))
