"""Custom metric that computes mean reward per dimension from multi-key reward.json."""

import argparse
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True, help="Input JSONL file of rewards")
    parser.add_argument("-o", required=True, help="Output JSON file for metrics")
    args = parser.parse_args()

    totals: dict[str, float] = {}
    counts: dict[str, int] = {}

    with open(args.i) as f:
        for line in f:
            reward = json.loads(line)
            if reward is None:
                continue
            for key, value in reward.items():
                totals[key] = totals.get(key, 0) + value
                counts[key] = counts.get(key, 0) + 1

    metrics = {key: totals[key] / counts[key] for key in totals}

    with open(args.o, "w") as f:
        json.dump(metrics, f)


if __name__ == "__main__":
    main()
