"""Backup identitas Agent FLOP testnet ke file ZIP.

Usage: python3 backup.py
Membuat flop-testnet-backup-YYYYMMDD.zip (mode 0600) berisi: did-key.json,
wallet.json, public.json, gen_keys.py, tc.py, fund.py, backup.py, README.txt.
Jalankan HANYA kalau user-nya sendiri yang minta backup.
ZIP-nya TIDAK ber-password: simpan di tempat privat, jangan disebar/upload.
Tidak pernah menampilkan isi seed/mnemonic.
"""
import datetime
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))

README_TXT = """Backup identitas Agent FLOP testnet — {date}
Testnet only, tidak ada dana asli di dompet ini.

ISI FILE:
- did-key.json  : DID agent + seed (RAHASIA). Identitas agent di Technocore.
- wallet.json   : alamat Substrate + mnemonic (RAHASIA). Dompet testnet FLOP.
- public.json   : DID + alamat wallet (boleh disebar, tidak ada rahasia).
- gen_keys.py   : script pembuat kunci (sudah dipakai, tidak perlu diulang).
- tc.py         : kirim pesan signed ke room Technocore. Pakai: python3 tc.py <room> <teks>
- claim_testnet.py : siapkan klaim faucet testnet. Pakai: python3 claim_testnet.py
                    (mencetak alamat + langkah web faucet; tidak mengirim request).
- backup.py     : script pembuat ZIP ini.
- requirements.txt : versi dependency yang sudah di-pin (pynacl, base58, substrate-interface).

CARA KLAIM FAUCET TESTNET (langkah manual, sekali saja):
1. Buka https://faucet.flop.network/ di PC/HP kamu.
2. Install extension Polkadot.js (atau Talisman / SubWallet).
3. Import akun dari mnemonic di wallet.json:
   Polkadot.js -> tombol + -> "Import account from pre-existing seed"
   -> tempel 12 kata dari field "mnemonic" di wallet.json -> simpan.
4. Klik "Connect wallet" di halaman faucet, pilih akun tadi. Kolom
   "Your FLOP address (SS58)" harus terisi alamat di public.json.
5. Klik "Request 10 FLOP", tanda tangani di extension.
6. Setelah selesai, HAPUS akun itu dari extension (Forget account).

PENTING:
- Seed di did-key.json dan mnemonic di wallet.json adalah SATU-SATUNYA
  cara memulihkan identitas/dompet ini. Simpan file ini baik-baik.
- Kalau bocor, orang lain bisa posting sebagai agent ini di Technocore
  dan klaim faucet ke alamat ini. Tidak ada dana asli yang bisa dicuri,
  tapi identitas agent-nya bisa dipakai orang lain.
- ZIP ini tidak ber-password — amannya karena disimpan privat.
"""

FILES = ["did-key.json", "wallet.json", "public.json",
         "gen_keys.py", "tc.py", "claim_testnet.py", "backup.py", "requirements.txt",
         "README.txt"]

missing = [f for f in ("did-key.json", "wallet.json") if not os.path.exists(os.path.join(HERE, f))]
if missing:
    raise SystemExit(f"keys not found ({', '.join(missing)}) — run gen_keys.py first")

today = datetime.date.today().strftime("%Y%m%d")
with open(os.path.join(HERE, "README.txt"), "w") as f:
    f.write(README_TXT.format(date=datetime.date.today().isoformat()))

zip_path = os.path.join(HERE, f"flop-testnet-backup-{today}.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for name in FILES:
        z.write(os.path.join(HERE, name), name)
os.chmod(zip_path, 0o600)
print("backup written:", zip_path)
print("keep it private — this ZIP is NOT password-protected")
