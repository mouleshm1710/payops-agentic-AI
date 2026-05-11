from app.services.azure_search_service import search_policy_documents


def retrieve_policy_context(question: str):
    search_result = search_policy_documents(question, top_k=3)

    if not search_result["success"]:
        return {
            "success": False,
            "context": "",
            "documents": [],
            "error": search_result["error"],
        }

    documents = search_result["results"]

    if not documents:
        return {
            "success": True,
            "context": "No relevant policy context found.",
            "documents": [],
            "error": None,
        }

    context_text = "\n\n".join([
        f"Document: {item['title']}\nContent: {item['content']}"
        for item in documents
    ])

    return {
        "success": True,
        "context": context_text,
        "documents": documents,
        "error": None,
    }