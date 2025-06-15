from langchain.tools import tool
from tools.get_model_info import get_model_info

@tool
def compare_models(model_id1: str, model_id2: str) -> str:
    """
    Compare two models using their metadata and README. 
    Returns a simple side-by-side comparison for the LLM to summarize.
    """
    info1 = get_model_info.invoke({"model_id": model_id1})
    info2 = get_model_info.invoke({"model_id": model_id2})
    return f"Model 1: {model_id1}\n{info1}\n\nModel 2: {model_id2}\n{info2}"