#!/usr/bin/env python3
"""
tools/integrations/pipedrive_match_deal.py
Pipedrive deal matching by participant email or organization domain.

Used by: tools/integrations/sembly_to_pipedrive.py
Auth: PIPEDRIVE_API_KEY env var
"""

import os
import sys
import argparse
import requests

BASE_URL = "https://api.pipedrive.com/v1"


def api_key() -> str:
    key = os.environ.get("PIPEDRIVE_API_KEY", "")
    if not key:
        print("ERROR: PIPEDRIVE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def _params(extra: dict | None = None) -> dict:
    p = {"api_token": api_key()}
    if extra:
        p.update(extra)
    return p


def find_person_by_email(email: str) -> int | None:
    if not email:
        return None
    r = requests.get(
        f"{BASE_URL}/persons/search",
        params=_params({"term": email, "fields": "email", "exact_match": "true", "limit": 5}),
        timeout=20,
    )
    if not r.ok:
        return None
    items = r.json().get("data", {}).get("items", [])
    return items[0]["item"]["id"] if items else None


def open_deal_for_person(person_id: int) -> int | None:
    r = requests.get(
        f"{BASE_URL}/persons/{person_id}/deals",
        params=_params({"status": "open", "limit": 10}),
        timeout=20,
    )
    if not r.ok:
        return None
    deals = r.json().get("data") or []
    if not deals:
        return None
    deals.sort(key=lambda d: d.get("update_time", ""), reverse=True)
    return deals[0].get("id")


def find_org_by_domain(domain: str) -> int | None:
    if not domain:
        return None
    r = requests.get(
        f"{BASE_URL}/organizations/search",
        params=_params({"term": domain, "fields": "name", "limit": 5}),
        timeout=20,
    )
    if not r.ok:
        return None
    items = r.json().get("data", {}).get("items", [])
    return items[0]["item"]["id"] if items else None


def open_deal_for_org(org_id: int) -> int | None:
    r = requests.get(
        f"{BASE_URL}/organizations/{org_id}/deals",
        params=_params({"status": "open", "limit": 10}),
        timeout=20,
    )
    if not r.ok:
        return None
    deals = r.json().get("data") or []
    if not deals:
        return None
    deals.sort(key=lambda d: d.get("update_time", ""), reverse=True)
    return deals[0].get("id")


def find_deal_by_email(email: str) -> int | None:
    """Email first, then org domain. Returns deal_id or None."""
    person_id = find_person_by_email(email)
    if person_id:
        deal_id = open_deal_for_person(person_id)
        if deal_id:
            return deal_id

    domain = email.split("@", 1)[1] if "@" in email else ""
    if domain:
        org_id = find_org_by_domain(domain)
        if org_id:
            return open_deal_for_org(org_id)

    return None


def find_deal_for_participants(emails: list[str]) -> tuple[int | None, str | None]:
    """Try each external email until a deal matches. Returns (deal_id, matched_email)."""
    for email in emails:
        deal_id = find_deal_by_email(email)
        if deal_id:
            return deal_id, email
    return None, None


def main():
    parser = argparse.ArgumentParser(description="Find Pipedrive deal for an email")
    parser.add_argument("--email", required=True)
    args = parser.parse_args()

    deal_id = find_deal_by_email(args.email.strip().lower())
    if deal_id:
        print(f"deal_id={deal_id}")
    else:
        print("no_match")
        sys.exit(2)


if __name__ == "__main__":
    main()
