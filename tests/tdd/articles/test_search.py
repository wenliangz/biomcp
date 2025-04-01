import json

from biomcp.articles.search import (
    PubmedRequest,
    ResultItem,
    convert_request,
    search_articles,
)


async def test_convert_search_query(anyio_backend):
    pubmed_request = PubmedRequest(
        chemicals=["Caffeine"],
        diseases=["non-small cell lung cancer"],
        genes=["BRAF"],
        variants=["BRAF V600E"],
        keywords=["therapy"],
    )
    pubtator_request = await convert_request(request=pubmed_request)
    assert (
        pubtator_request.text == "therapy AND "
        "@CHEMICAL_Caffeine AND "
        "@DISEASE_Carcinoma_Non_Small_Cell_Lung AND "
        "@GENE_BRAF AND "
        "@VARIANT_p.V600E_BRAF_human"
    )
    # default page request
    assert pubtator_request.size == 40


async def test_search(anyio_backend):
    query = {
        "genes": ["BRAF"],
        "diseases": ["NSCLC", "Non - Small Cell Lung Cancer"],
        "keywords": ["BRAF mutations NSCLC"],
        "variants": ["mutation", "mutations"],
    }

    query = PubmedRequest(**query)
    output = await search_articles(query, output_json=True)
    data = json.loads(output)
    assert isinstance(data, list)
    assert len(data) == 40
    result = ResultItem.model_validate(data[0])
    # todo: this might be flaky.
    assert (
        result.title
        == "[Expert consensus on the diagnosis and treatment in advanced "
        "non-small cell lung cancer with BRAF mutation in China]."
    )
