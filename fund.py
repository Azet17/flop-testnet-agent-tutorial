"""Sign the faucet challenge with the Sr25519 wallet key and claim the grant.

Usage: python3 fund.py <nonce>
Builds challenge "fund|<ss58>|<nonce>", signs with the wallet key from
wallet.json (0600), and privately GETs the faucet fund endpoint with curl.
Prints ONLY the faucet response. Never prints the mnemonic or signature.
"""
import json
import os
import subprocess
import sys

from substrateinterface import Keypair

OUT = os.path.dirname(os.path.abspath(__file__))
nonce = sys.argv[1]

with open(f"{OUT}/wallet.json") as f:
    w = json.load(f)
addr = w["address"]
kp = Keypair.create_from_mnemonic(w["mnemonic"], ss58_format=42)
assert kp.ss58_address == addr, "wallet address mismatch"

challenge = f"fund|{addr}|{nonce}".encode("utf-8")
sig_hex = "0x" + kp.sign(challenge).hex()
url = f"https://faucet.technocore.chat/faucet/fund/{addr}/{nonce}/{sig_hex}"
r = subprocess.run(["curl", "-s", "-m", "30", url],
                   capture_output=True, text=True)
print("faucet reply:")
print(r.stdout[:1500])
if r.stderr:
    print("STDERR:", r.stderr[:300])
