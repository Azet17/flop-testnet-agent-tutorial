#!/usr/bin/env python3
"""Testnet agent faucet claim (10 FLOP) — the lane that actually works.

The repo's fund.py targets the devnet room flow (GET faucet.technocore.chat),
which does not exist on testnet. Testnet requires:

  message = "flop-faucet-agent/v1|<genesis>|<ss58>|<nonce_ms>"
  signed with the wallet's sr25519 key (NOT the Ed25519 did:key)
  POST https://faucet.flop.network/v1/testnet/agent-claims
       {"address","nonce","signature":"0x<hex>"}

Never prints the mnemonic. Prints address, nonce, local verify result, reply.
"""
import json
import secrets
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

import sr25519
from substrateinterface import Keypair

HERE = Path(__file__).resolve().parent
GENESIS = "0x918abd58fb16306b30ef3886514cfaebffecb4de43e82b6f8ec4795c43cfd800"
ENDPOINT = "https://faucet.flop.network/v1/testnet/agent-claims"

w = json.loads((HERE / "wallet.json").read_text())
addr = w["address"]
kp = Keypair.create_from_mnemonic(w["mnemonic"], ss58_format=42)
assert kp.ss58_address == addr, "wallet address mismatch"

# nonce: fresh ms clock, nudged so repeated runs never collide
nonce = int(time.time() * 1000) + secrets.randbelow(1000)

msg = f"flop-faucet-agent/v1|{GENESIS}|{addr}|{nonce}".encode("utf-8")
sig = kp.sign(msg)
ok = sr25519.verify(sig, msg, kp.public_key)

print(f"address : {addr}")
print(f"nonce   : {nonce}")
print(f"msg     : {len(msg)} bytes  ({msg[:34].decode()}…)")
print(f"localverify sr25519: {ok}")

body = json.dumps({"address": addr, "nonce": str(nonce), "signature": "0x" + sig.hex()}).encode()
req = urllib.request.Request(
    ENDPOINT, data=body, method="POST",
    headers={"content-type": "application/json", "user-agent": "flop-agent/1.0"},
)
try:
    with urllib.request.urlopen(req, timeout=180, context=ssl.create_default_context()) as r:
        print(f"HTTP {r.status}")
        print(r.read().decode()[:800])
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}")
    print(e.read().decode()[:800])
except Exception as e:
    print(f"NO REPLY ({type(e).__name__}) — cek saldo on-chain sebelum retry")
