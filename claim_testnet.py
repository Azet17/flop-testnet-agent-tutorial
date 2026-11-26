#!/usr/bin/env python3
"""Testnet agent faucet claim (10 FLOP) — the lane that actually works.

DEFAULT IS PREPARE-ONLY. The faucet limits grants per IP (3/day, 24 h cooldown),
so an agent on a shared host would burn the IP quota for every other user of that
host. This script signs the claim locally and prints a ready-to-run curl command;
the HUMAN runs it from their own PC or phone.

  python3 claim_testnet.py            sign locally, print the curl (default)
  python3 claim_testnet.py --send     actually POST from this machine
                                      (only on a dedicated/private IP)

Claim message:  flop-faucet-agent/v1|<genesis>|<ss58>|<nonce_ms>   (150 bytes)
Signature:      the wallet's own key (sr25519)
Endpoint:       POST https://faucet.flop.network/v1/testnet/agent-claims
                {"address", "nonce": "<string>", "signature": "0x<hex>"}

The nonce MUST be a JSON string. A numeric nonce returns 401
"Sign the D10 versioned claim with the recipient key" — a misleading error.

Never prints the mnemonic or the seed. Prints address, nonce, signature.
"""
import json
import secrets
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import sr25519
from substrateinterface import Keypair

HERE = Path(__file__).resolve().parent
GENESIS = "0x918abd58fb16306b30ef3886514cfaebffecb4de43e82b6f8ec4795c43cfd800"
ENDPOINT = "https://faucet.flop.network/v1/testnet/agent-claims"

MODE = "send" if "--send" in sys.argv else "prepare"

w = json.loads((HERE / "wallet.json").read_text())
addr = w["address"]
kp = Keypair.create_from_mnemonic(w["mnemonic"], ss58_format=42)
assert kp.ss58_address == addr, "wallet address mismatch"

# nonce: fresh ms clock, nudged so repeated runs never collide
nonce = int(time.time() * 1000) + secrets.randbelow(1000)

msg = f"flop-faucet-agent/v1|{GENESIS}|{addr}|{nonce}".encode("utf-8")
sig = kp.sign(msg)
ok = sr25519.verify(sig, msg, kp.public_key)
body = json.dumps({"address": addr, "nonce": str(nonce), "signature": "0x" + sig.hex()})

print(f"address : {addr}")
print(f"nonce   : {nonce}")
print(f"message : {len(msg)} bytes  (flop-faucet-agent/v1|…|{addr[:8]}…|{nonce})")
print(f"verify  : {ok}  (sr25519, local check)")
print()

if MODE == "prepare":
    print("=" * 72)
    print("LANGKAH MANUAL — kerjakan di PC/HP kamu sendiri, bukan di server")
    print("=" * 72)
    print()
    print("1. Buka  https://faucet.flop.network/  di browser.")
    print()
    print("2. Connect wallet FLOP kamu: Polkadot.js / Talisman / SubWallet.")
    print("   (Belum ada di wallet? import dari backup.py dulu, lalu hapus")
    print("   lagi setelah selesai.)")
    print()
    print(f"3. Alamat FLOP (SS58):  {addr}")
    print("   Klik 'Connect wallet' — kolom 'Your FLOP address' terisi otomatis.")
    print("   Kalau mau manual, tempel alamat itu ke kolomnya.")
    print()
    print("4. Klik  Request 10 FLOP  lalu tanda tangan di extension wallet.")
    print("   Sukses = 'Testnet claim accepted/finalized' + link tx.")
    print()
    print("Kenapa harus connect wallet:")
    print("Halaman faucet yang menandatangani klaim (signRaw) dengan wallet")
    print("yang ter-connect, jadi alamat yang di-request harus wallet yang")
    print("ada di browser kamu. Menempel alamat saja tidak cukup.")
    print()
    print("Catatan:")
    print("- Testnet: 10 FLOP per 24 jam. Tier 'Verified human' tidak tersedia.")
    print("- 429 = IP kamu sudah klaim dalam 24 jam terakhir. Tunggu.")
    print("- Setelah grant masuk, agent bisa verifikasi saldo on-chain.")
    sys.exit(0)

print("WARNING: --send memakai IP mesin ini. Kalau mesin ini dipakai bersama")
print("(banyak user Muse di satu host), kuota IP jadi rebutan: 3 grant/hari,")
print("cooldown 24 jam. Pakai mode default (prepare) kalau ragu.")
print()

req = urllib.request.Request(
    ENDPOINT, data=body.encode(), method="POST",
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
