import http.client
import urllib
import json
import os
import sys

headers = {
    # Request headers
    "Ocp-Apim-Subscription-Key": os.environ["MICROSOFT_ACADEMIC_API_KEY"],
    "Content-Type": "application/json"
}


def evaluate_request(params):
    try:
        conn = http.client.HTTPSConnection("westus.api.cognitive.microsoft.com")
        conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = json.loads(response.read())
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    return data


def get_author_list(dates):
    author_params = urllib.urlencode({
        "expr": "And(Composite(F.FN=='computer science'),D=%s)" % dates,
        "attributes": "AA.AuId,ECC",
        "orderby": "ECC:desc",
        "count": 1000,
        "mode": "json",
    })

    response = evaluate_request(author_params)
    authors = set()
    for paper in response["entities"]:
        for author in paper["AA"]:
            authors.add(author['AuId'])

    return authors


if __name__ == '__main__':
    if len(sys.argv) != 1:
        print 'Usage: python data_collection.py'
        exit(-1)

    print(len(get_author_list("['2016-08-01', '2017-08-01']")))
