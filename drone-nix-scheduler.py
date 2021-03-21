#!/usr/bin/env python

import requests
import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict
from dataclasses import dataclass
import logging


@dataclass
class DroneClient:
    server: str
    repo: str
    token: str

    def headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def build(self, num: int) -> Dict[str, Any]:
        return requests.get(
            f"{self.server}/api/repos/{self.repo}/builds/{num}",
            headers=self.headers(),
        ).json()

    def create_build(self, params: Dict[str, str]) -> Dict[str, str]:
        return requests.post(
            f"{self.server}/api/repos/{self.repo}/builds",
            params=params,
            headers=self.headers(),
        ).json()


def ensure_env_var(var: str) -> str:
    val = os.environ.get(var)
    if val is None:
        print(f"{var} not set", file=sys.stderr)
        sys.exit(1)
    return val

STATUS_MAP = dict(success="✔", failure="✖")


def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print(f"USAGE: {sys.argv[0]} json")
            sys.exit(1)
        else:
            with open(sys.argv[1]) as f:
                res = json.load(f)
    else:
        res = json.load(sys.stdin)

    branch = ensure_env_var("DRONE_BRANCH")
    commit = ensure_env_var("DRONE_COMMIT")
    token = ensure_env_var("DRONE_TOKEN")
    server = ensure_env_var("DRONE_SERVER")
    repo = ensure_env_var("DRONE_REPO")

    client = DroneClient(server, repo, token)

    jobs = {}
    for job, args in res.items():
        drv = args["drvPath"]
        num_builds = len(args['builds'])
        num_substititions = len(args['substitutes'])
        if num_builds == 0:
            print(f"{job}: skipped")
            continue
        data = client.create_build(
            dict(branch="master", commit=commit, derivation=str(drv))
        )
        num = int(data["number"])
        url = f"{server}/{repo}/{num}"
        print(f"{job}: {num_builds} build(s), {num_substititions} substition(s), build started at {url}")
        if data["status"] == "pending":
            jobs[num] = job

    failures = 0
    for num, job in jobs.items():
        print(f"{job}: ", end="")
        while True:
            data = client.build(num)
            if data["status"] not in ["pending", "running"]:
                break
        if data["status"] != "success":
            failures += 1
        status = data["status"]
        print(f"{STATUS_MAP.get(status, status)}")
    if failures != 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
