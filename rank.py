# coding=utf-8
import requests
import json
import csv
from mpms import MultiProcessesMultiThreads

START_STAR = 0
END_STAR = 100

GITHUB_API_URL = "https://api.github.com/search/repositories"
result = []


def worker(stars):
    print("Getting: {}".format(stars))

    try:
        r = requests.get(
            GITHUB_API_URL,
            params={"q": "stars:>={}".format(stars)}
        )
        j = json.loads(r.text)
        return stars, j["total_count"]
    except:
        return stars, None


def handler(meta, stars=None, count=None):
    self = meta["self"]  # type: MultiProcessesMultiThreads

    if count is not None:
        print("Stars: {} Count:{}".format(stars, count))
        result.append({"stars": stars, "count": count})

        if len(result) == END_STAR + 1 - START_STAR:
            self.close()

    else:
        print("[Failed] Stars:{} Retrying".format(stars))
        self.put(stars)


def main():
    print("From {} To {}".format(START_STAR, END_STAR))

    q = MultiProcessesMultiThreads(
        worker,
        handler,
        processes=2,
        threads_per_process=4,
    )
    for i in range(START_STAR, END_STAR + 1):
        q.put(i)

    q.join(close=False)

    # write to file
    print("writing to output.csv")
    with open("output.csv", "w", encoding="utf-8", newline="") as fw:
        writer = csv.DictWriter(fw, fieldnames=["stars", "count"])
        writer.writeheader()
        writer.writerows(sorted(result, key=lambda x: x["stars"]))


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 2:
        END_STAR = int(sys.argv[1])
    elif len(sys.argv) == 3:
        START_STAR = int(sys.argv[1])
        END_STAR = int(sys.argv[2])

    main()
