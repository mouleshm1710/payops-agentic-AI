from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from app.config import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_KEY,
    AZURE_SEARCH_INDEX,
)


def get_search_client():
    return SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX,
        credential=AzureKeyCredential(AZURE_SEARCH_KEY),
    )


search_client = get_search_client()


def search_policy_documents(query: str, top_k: int = 3):
    try:
        results = search_client.search(
            search_text=query,
            top=top_k,
        )

        contexts = []

        for result in results:
            contexts.append({
                "title": (result.get("title") or result.get("source_file") or result.get("file_name")
        or result.get("document_name") or "Policy Document"
            ),
                "content": result.get("content", ""),
                "score": result.get("@search.score", None),
            })

        return {
            "success": True,
            "results": contexts,
            "error": None,
        }

    except Exception as error:
        return {
            "success": False,
            "results": [],
            "error": str(error),
        }