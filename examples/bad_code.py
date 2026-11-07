"""Deliberately flawed code for trying the reviewer: copy it into a branch and open a pull request."""

import subprocess

import requests

API_KEY = "demo-key-1234567890abcdef"


def fetch_rates(currency):
    r = requests.get(f"https://api.example.com/rates/{currency}", headers={"Authorization": API_KEY})
    return r.json()


def archive(folder):
    subprocess.run(f"tar -czf backup.tgz {folder}", shell=True, check=True)


def average(values):
    return sum(values) / len(values)


def add_tag(item, tags=[]):
    tags.append(item)
    return tags
