"""One-shot script to patch Medium URLs on existing articles by exact title match.

Idempotent — run as many times as you want. Articles not in URL_MAP are left
untouched. Pass `--clear` to set URL to NULL for any article whose title is
mapped to None (used to wipe placeholder URLs we couldn't verify).

Run inside the docker container:
    docker compose exec backend python update_urls.py
"""

import sys

from sqlalchemy import select

from database import SessionLocal
from models import Article


# Confirmed via Medium profile + RSS feed (2026-05-28).
# Articles not in this dict are left alone; entries mapped to None
# explicitly clear the URL (used to remove the bad placeholder).
URL_MAP: dict[str, str | None] = {
    # --- "OP_* on Signet" series (all confirmed) ---
    "OP_CAT on Signet — Concatenation, Commitment, and Bitcoin Inquisition":
        "https://medium.com/@aaron.recompile/op-cat-on-signet-concatenation-commitment-and-bitcoin-inquisition-ed34a07866d6",
    "OP_CHECKSIGFROMSTACK on Signet — Sign Anything, Verify on Stack":
        "https://medium.com/@aaron.recompile/op-checksigfromstack-on-signet-sign-anything-verify-on-stack-9cf70ab07583",
    "OP_CHECKTEMPLATEVERIFY on Signet — Locking Outputs at UTXO Creation Time":
        "https://medium.com/@aaron.recompile/op-checktemplateverify-on-signet-locking-outputs-at-utxo-creation-time-1d623fbe3899",
    "OP_INTERNALKEY + OP_CHECKSIGFROMSTACK on Signet — Identity-Bound Authorization":
        "https://medium.com/@aaron.recompile/op-internalkey-op-checksigfromstack-on-signet-identity-bound-authorization-04f0440557bc",
    "OP_CAT + OP_CHECKSIGFROMSTACK on Signet — Dynamic Message, Oracle Authorization":
        "https://medium.com/@aaron.recompile/op-cat-op-checksigfromstack-on-signet-dynamic-message-oracle-authorization-8c73e1ef5353",
    "SIGHASH_ANYPREVOUT on Signet: When Signatures Stop Binding to UTXOs":
        "https://medium.com/@aaron.recompile/sighash-anyprevout-on-signet-when-signatures-stop-binding-to-utxos-eed4fc475668",

    # --- Standalones (4 confirmed via profile fetch) ---
    "The Missing Developer Stack of Taproot":
        "https://medium.com/@aaron.recompile/the-missing-developer-stack-of-taproot-61352dad7f96",
    "RootScope: A Tool for Reconstructing Taproot Script Paths — Step by Step":
        "https://medium.com/@aaron.recompile/rootscope-a-tool-for-reconstructing-taproot-script-paths-step-by-step-106012af54b9",
    "Commit-Reveal vs Dual-Layer Scripts: The Real Architecture of Bitcoin Script":
        "https://medium.com/@aaron.recompile/commit-reveal-vs-dual-layer-scripts-the-real-architecture-of-bitcoin-script-665a79b0bd34",
    "The Anatomy of Bitcoin Scripts: From P2PKH to Taproot":
        "https://medium.com/@aaron.recompile/the-anatomy-of-bitcoin-scripts-from-p2pkh-to-taproot-4db16924232f",

    # --- Older posts confirmed via user-supplied URLs (2026-05-28) ---
    "Building a 4-Leaf Taproot Tree in Python: The First Complete Implementation on Bitcoin Testnet":
        "https://medium.com/@aaron.recompile/building-a-4-leaf-taproot-tree-in-python-the-first-complete-implementation-on-bitcoin-testnet-c8b66c331f29",
    "Taproot Control Block Deep Analysis & Stack Execution Visualization | Part 2":
        "https://medium.com/@aaron.recompile/taproot-control-block-deep-analysis-stack-execution-visualization-5ff10f98032c",
    "Bitcoin Script Doesn't Execute What's on the Stack: A Developer's Journey From Misconception to Clarity":
        "https://medium.com/@aaron.recompile/bitcoin-script-doesnt-execute-what-s-on-the-stack-a-developer-s-journey-from-misconception-to-5fd4229a0864",
    "Why Counterparty's Fake-Pubkey Grinding Reveals the Real Boundary Between Bitcoin Consensus and Policy":
        "https://medium.com/@aaron.recompile/why-counterpartys-fake-pubkey-grinding-reveals-the-real-boundary-between-bitcoin-consensus-and-3c891f0e7ec9",
    "Why V3 Matters: Bitcoin's Relay Layer Was Rewritten, and Most People Didn't Notice":
        "https://medium.com/@aaron.recompile/why-v3-matters-bitcoins-relay-layer-was-rewritten-and-most-people-didn-t-notice-5d4f1b56b5bd",
    "Bitcoin Doesn't Use Encryption — What Adam Back's Comment Really Means":
        "https://medium.com/@aaron.recompile/bitcoin-doesnt-use-encryption-what-adam-back-s-comment-really-means-4c3f1527a4d3",

    # --- Final 3 URLs supplied by user (2026-05-28) — all 19 articles now linked ---
    "How I Built a Time-Locked Bitcoin Script with CSV and P2SH":
        "https://medium.com/@aaron.recompile/how-i-built-a-time-locked-bitcoin-script-with-csv-and-p2sh-c48c0389709d",
    "A Guide to Creating Taproot Scripts with Python Bitcoinutils":
        "https://medium.com/@aaron.recompile/a-guide-to-creating-taproot-scripts-with-python-bitcoinutils-e088633bc2a7",
    "How Bitcoin P2SH Scripts Work: From 2-of-3 Multisig to Timelocked Inheritance":
        "https://medium.com/@aaron.recompile/how-bitcoin-p2sh-scripts-work-from-2-of-3-multisig-to-timelocked-inheritance-8015010dd6f2",
}


def main() -> int:
    db = SessionLocal()
    try:
        updated = 0
        cleared = 0
        not_found: list[str] = []
        for title, url in URL_MAP.items():
            article = db.execute(
                select(Article).where(Article.title == title)
            ).scalar_one_or_none()
            if article is None:
                not_found.append(title)
                continue
            if article.url == url:
                continue
            article.url = url
            if url is None:
                cleared += 1
            else:
                updated += 1
        db.commit()
        print(f"Set real URL on {updated} articles.")
        print(f"Cleared placeholder URL on {cleared} articles.")
        if not_found:
            print(f"WARN: {len(not_found)} titles in the map did not match any article:")
            for t in not_found:
                print(f"  - {t}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
