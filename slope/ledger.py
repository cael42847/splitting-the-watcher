"""ledger — the fake-coin chain for the money market (AGREED #112). Arm-agnostic plumbing only:
start a local Anvil chain, give each seller an account, pay, read balances, read the payment log.
No model calls here. Anvil v1.8.3 at ~/.foundry/bin (installed 2026-10-17, checksum verified).
The accounts are Anvil's public default dev keys: local only, worthless by design, never reused anywhere else.

Usage from game.py (later, once she has chosen the family and the ledger arm):
    L = Ledger(n_sellers=2); L.start()
    L.pay(0, 1, 0.5)            # seller 0 pays seller 1 half a coin
    L.balances()                # [coins per seller]
    L.log                       # every payment: (round, frm, to, amount, tx_hash)
    L.stop()
Smoke: python3 ledger.py
"""
import json, os, subprocess, time, urllib.request

ANVIL = os.path.expanduser("~/.foundry/bin/anvil")
COIN = 10 ** 18          # one coin = one ether on the local chain
START_COINS = 10         # each seller's wallet at round 0 (the pot); the rest of the dev balance is never touched


class Ledger:
    def __init__(self, n_sellers, port=8547, start_coins=START_COINS, bank=False):
        self.n, self.port, self.start_coins, self.bank = n_sellers, port, start_coins, bank
        self.url = f"http://127.0.0.1:{port}"
        self.proc, self.accounts, self.log, self.round = None, [], [], 0
        self.base = []  # dev balance at start, so a seller's coins = start_coins + (balance - base)

    def rpc(self, method, params=None):
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}).encode()
        r = urllib.request.urlopen(urllib.request.Request(self.url, body, {"Content-Type": "application/json"}), timeout=10)
        j = json.load(r)
        if "error" in j:
            raise RuntimeError(j["error"])
        return j["result"]

    def start(self):
        # --balance 100000000 (2026-10-19): the bank had Anvil's default 10,000 and a 60-round pot paid out more (L3 rep1 crashed at t55)
        import socket   # 2026-10-19: a free port per ledger; the fixed 8547 let parallel runs share one chain (void-map-2026-10-19)
        with socket.socket() as sk:
            sk.bind(("127.0.0.1", 0)); self.port = sk.getsockname()[1]
        self.url = f"http://127.0.0.1:{self.port}"
        self.proc = subprocess.Popen([ANVIL, "--port", str(self.port), "--silent", "--accounts", str(max(self.n + (1 if self.bank else 0), 2)), "--base-fee", "0", "--gas-price", "0", "--balance", "100000000"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(50):
            try:
                acc = self.rpc("eth_accounts"); self.accounts = acc[: self.n]; self.bank_acct = acc[self.n] if self.bank else None
                break
            except Exception:
                time.sleep(0.1)
        else:
            raise RuntimeError("anvil did not start")
        if int(self.rpc("eth_blockNumber"), 16) != 0 or self.proc.poll() is not None:
            raise RuntimeError("ledger: not a fresh chain of our own (port %d)" % self.port)
        self.base = [int(self.rpc("eth_getBalance", [a, "latest"]), 16) for a in self.accounts]
        return self

    def pay(self, frm, to, amount):
        """Seller frm pays seller to `amount` coins. Refused (returns None) if it would take frm below zero coins."""
        if frm == to or amount <= 0 or amount > self.coins(frm):
            return None
        wei = int(round(amount * COIN))
        tx = self.rpc("eth_sendTransaction", [{"from": self.accounts[frm], "to": self.accounts[to], "value": hex(wei),
                                               "gasPrice": "0x0"}])
        self.rpc("evm_mine")  # a zero-fee tx waits in the pool until a block is mined (found in the 10-17 smoke)
        self.log.append({"round": self.round, "from": frm, "to": to, "amount": amount, "tx": tx})
        return tx

    def _send(self, frm_acct, to_acct, amount):
        tx = self.rpc("eth_sendTransaction", [{"from": frm_acct, "to": to_acct, "value": hex(int(round(amount * COIN))), "gasPrice": "0x0"}])
        self.rpc("evm_mine"); return tx

    def settle_profit(self, i, coins):
        """C1, the pot: the round's profit paid in by the bank (a loss paid out to it). The wallet may go below zero."""
        if not self.bank or abs(coins) < 1e-12: return None
        return self._send(self.bank_acct, self.accounts[i], coins) if coins > 0 else self._send(self.accounts[i], self.bank_acct, -coins)

    def coins(self, i):
        bal = int(self.rpc("eth_getBalance", [self.accounts[i], "latest"]), 16)
        return self.start_coins + (bal - self.base[i]) / COIN

    def balances(self):
        return [round(self.coins(i), 6) for i in range(self.n)]

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=5)
            self.proc = None


if __name__ == "__main__":
    L = Ledger(2).start()
    try:
        assert L.balances() == [10, 10], L.balances()
        L.round = 1
        assert L.pay(0, 1, 2.5)
        assert L.balances() == [7.5, 12.5], L.balances()
        assert L.pay(0, 1, 100) is None          # cannot pay what it doesn't have
        assert L.pay(1, 1, 1) is None            # cannot pay itself
        print("ledger smoke PASS", L.balances(), len(L.log), "payment logged")
    finally:
        L.stop()
