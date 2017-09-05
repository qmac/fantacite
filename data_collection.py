from collections import defaultdict
import httplib
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
        conn = httplib.HTTPSConnection("westus.api.cognitive.microsoft.com")
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
        "mode": "json"
    })

    response = evaluate_request(author_params)
    authors = set()
    for paper in response["entities"]:
        for author in paper["AA"]:
            authors.add(author['AuId'])

    return list(authors)


def get_roster_stats(authors, date):
    stats = defaultdict(lambda: [0.0, 0.0])
    author_string = ",".join(["Composite(AA.AuId=%d)" % a for a in authors])
    roster_params = urllib.urlencode({
        "expr": "And(D>%s,Or(%s))" % (date, author_string),
        "attributes": "ECC,AA.AuId",
        "count": 1000,
        "mode": "json"
    })

    response = evaluate_request(roster_params)
    for paper in response["entities"]:
        for author in paper["AA"]:
            au_id = author["AuId"]
            if au_id in authors:
                stats[au_id][0] += 1
                stats[au_id][1] += paper["ECC"]

    return stats


if __name__ == '__main__':
    if len(sys.argv) != 1:
        print 'Usage: python data_collection.py'
        exit(-1)

    authors = get_author_list("['2016-08-01', '2017-08-01']")[10:30]
    print(get_roster_stats(authors, "'2017-08-01'"))
