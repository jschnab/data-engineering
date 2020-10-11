import shutil

from urllib import parse, request


def query_uniprot():
    query = (
        'kinase annotation:(type:transmem) database:(type:pdb) '
        'goa:("plasma membrane")'
    )
    query_args = {
        "query": query,
        "sort": "score",
        "format": "fasta",
    }
    encoded_args = parse.urlencode(query_args)
    url = "https://uniprot.org/uniprot/?" + encoded_args
    with request.urlopen(url) as response:
        with open("results.fa", "wb") as outfile:
            shutil.copyfileobj(response, outfile)


if __name__ == "__main__":
    query_uniprot()
