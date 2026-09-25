import logging, re, time, json, csv, os, threading, tkinter as tk
from tkinter import scrolledtext; from decimal import Decimal; from datetime import datetime
try: import winsound
except: winsound = None
class TkLog(logging.Handler):
    def __init__(self, tw): super().__init__(); self.tw = tw
    def emit(self, r): m = self.format(r); self.tw.after(0, lambda: (self.tw.configure(state='normal'), self.tw.insert(tk.END, m+'\n'), self.tw.configure(state='disabled'), self.tw.yview(tk.END)))
logger = logging.getLogger("VM"); logger.setLevel(logging.INFO); fmt = logging.Formatter("%(message)s")
class VendingMachine:
    def __init__(self):
        self.saldo, self.jackpot, self.falhas, self.sf, self.cf, self.adm = Decimal("0.00"), Decimal("0.00"), 0, "vending_state.json", "vending_sales_log.csv", "SOYUZ1967"
        self.vouchers = {"DESCONTO10": Decimal("0.50"), "PROMOVIP": Decimal("1.00")}
        self.produtos = {
            "A1": {"nome": "Coca-Cola", "preco": Decimal("1.50"), "stock": 10}, "A2": {"nome": "Água Mineral", "preco": Decimal("1.00"), "stock": 10},
            "A3": {"nome": "Sprite", "preco": Decimal("1.40"), "stock": 10}, "B1": {"nome": "Batatas Fritas", "preco": Decimal("1.20"), "stock": 10},
            "B2": {"nome": "Chocolates", "preco": Decimal("1.80"), "stock": 10}, "B3": {"nome": "Energético", "preco": Decimal("2.50"), "stock": 10},
            "DESTINO": {"nome": "Botão do Destino", "preco": Decimal("1.10"), "stock": 10}
        }
        # AJUSTE DE MOEDAS ACETES: Modifique as chaves deste dicionário para alterar as moedas válidas
        self.tubos = {Decimal("2.00"): 10, Decimal("1.00"): 10, Decimal("0.50"): 20, Decimal("0.20"): 20, Decimal("0.10"): 30, Decimal("0.05"): 40}
        if os.path.exists(self.sf):
            try:
                with open(self.sf, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                    for k, v in d.get("produtos", {}).items():
                        if k in self.produtos: self.produtos[k]["stock"], self.produtos[k]["preco"] = int(v["stock"]), Decimal(str(v["preco"]))
                    for k, v in d.get("tubos", {}).items(): self.tubos[Decimal(k)] = int(v)
                logger.info("💾 [COFRE] Estado carregado com moedas atualizadas.")
            except Exception as e: logger.error(f"⚠️ Erro JSON: {e}")
    def som(self, t="curto"):
        def _s():
            if winsound:
                if t == "curto": [winsound.Beep(f, 50) for f in range(1500, 2200, 150)]
                elif t == "quantico": [winsound.Beep(f, 40) for f in range(2000, 3000, 250)]
                elif t == "sabotagem": [winsound.Beep(800, 200) for _ in range(4)]
                else:
                    for _ in range(3):
                        [winsound.Beep(f, 35) for f in range(1400, 2600, 300)]; [winsound.Beep(f, 35) for f in range(2600, 1400, -300)]
        threading.Thread(target=_s, daemon=True).start()
    def salvar(self):
        try:
            d = {"produtos": {k: {"nome": v["nome"], "preco": str(v["preco"]), "stock": v["stock"]} for k, v in self.produtos.items()}, "tubos": {str(k): v for k, v in self.tubos.items()}}
            with open(self.sf, 'w', encoding='utf-8') as f: json.dump(d, f, indent=4, ensure_ascii=False)
        except: pass
    def log_csv(self, s, n, p, nif):
        ex = os.path.exists(self.cf)
        try:
            with open(self.cf, 'a', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                if not ex: w.writerow(["Timestamp", "Slot", "Produto", "Preco", "NIF"])
                w.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), s, n, f"{p:.2f}", nif])
        except: pass
    def calc_troco(self, val: Decimal) -> dict:
        res, resto = {}, val
        for m in sorted(self.tubos.keys(), reverse=True):
            if resto <= 0: break
            q = min(int(resto // m), self.tubos[m])
            if q > 0: res[m] = q; resto -= m * q
        return res if resto == 0 else None
    def atualizar_bolsa(self, slot):
        if slot == "DESTINO": return
        for s, p in self.produtos.items():
            if s == "DESTINO": continue
            p["preco"] = max(Decimal("0.50"), p["preco"] + Decimal("0.10")) if s == slot else max(Decimal("0.40"), p["preco"] - Decimal("0.05"))
        self.salvar()
    def inserir_moeda(self, v: Decimal):
        if v in self.tubos:
            self.tubos[v] += 1; self.saldo += v; self.som("curto"); logger.info(f"🪙 Moeda {v:.2f}€. Saldo: {self.saldo:.2f}€"); self.salvar(); return True
        logger.error(f"❌ Moeda de {v:.2f}€ rejeitada."); return False
    def devolver_saldo(self):
        if self.saldo <= 0: return {}
        tr = self.calc_troco(self.saldo)
        if tr:
            for m, q in tr.items(): self.tubos[m] -= q
            logger.info(f"💰 Devolvido {self.saldo:.2f}€."); self.saldo = Decimal("0.00"); self.salvar(); self.som("curto"); return tr
        return None
    def aplicar_voucher(self, c: str):
        if c in self.vouchers: d = self.vouchers[c]; self.saldo += d; del self.vouchers[c]; logger.info(f"🎟️ Voucher {c} (+{d:.2f}€)"); self.som("quantico"); return True
        return False
    def comprar_produto(self, s: str, nif: str = "999999999") -> bool:
        if s not in self.produtos: return False
        p = self.produtos[s]
        if p["stock"] <= 0 or self.saldo < p["preco"]: return False
        exc = self.saldo - p["preco"]; tr = self.calc_troco(exc)
        if exc > 0 and tr is None: return False
        p["stock"] -= 1
        if exc > 0:
            for m, q in tr.items(): self.tubos[m] -= q
        if s != "DESTINO": self.jackpot += p["preco"] * Decimal("0.05")
        logger.info(f"✅ {p['nome']} dispensado! Troco: {exc:.2f}€"); self.log_csv(s, p["nome"], p["preco"], nif); self.saldo = Decimal("0.00")
        self.som("quantico" if s == "DESTINO" else "longo"); self.atualizar_bolsa(s); self.salvar(); return True
    def autenticar_admin(self, c: str) -> bool:
        if c == self.adm: self.falhas = 0; logger.info("🛠️ Admin OK."); return True
        self.falhas += 1
        if self.falhas >= 3: self.som("sabotagem"); logger.critical("🚨 Alerta Invasão!")
        return False
class VMUi:
    def __init__(self, vm):
        self.vm, self.u_clique = vm, 0.0; self.root = tk.Tk(); self.root.title("Soyuz Bird"); self.root.geometry("440x840"); self.root.configure(bg="#121214")
        self.txt = scrolledtext.ScrolledText(self.root, height=10, bg="#0d0e15", fg="#a9b7c6", font=("Courier", 8), state='disabled')
        th = TkLog(self.txt); th.setFormatter(fmt); logger.addHandler(th)
        self.lbl_saldo = tk.Label(self.root, text="0.00€", font=("Courier", 20, "bold"), fg="#00ff00", bg="#000000", height=2); self.lbl_saldo.pack(pady=5, fill="x", padx=15)
        self.cv = tk.Canvas(self.root, width=400, height=100, bg="#0a0f1d", highlightthickness=1, highlightbackground="#00ff00"); self.cv.pack(pady=5, padx=15)
        self.lbl_pique = self.cv.create_text(200, 50, text="📊 SISTEMA OPERACIONAL\nInsira moedas ou use MB WAY", fill="#00ff00", font=("Arial", 10, "bold"), justify="center")
        f_nif = tk.LabelFrame(self.root, text=" Cliente / Admin ", fg="white", bg="#121214"); f_nif.pack(pady=2, fill="x", padx=15)
        tk.Label(f_nif, text="CÓDIGO:", fg="white", bg="#121214").pack(side="left", padx=5)
        self.ent_nif = tk.Entry(f_nif, width=15); self.ent_nif.pack(side="left", padx=5, pady=5)
        tk.Button(f_nif, text="🔑 Validar", bg="#333", fg="white", command=self.validar).pack(side="left", padx=5)
        f_mb = tk.LabelFrame(self.root, text=" MB WAY ", fg="#00ffff", bg="#121214"); f_mb.pack(pady=2, fill="x", padx=15)
        tk.Button(f_mb, text="📲 Pagar com MB WAY (2.50€)", bg="#e83e8c", fg="white", font=("Arial", 9, "bold"), command=self.simular_mbway).pack(fill="x", pady=2)
        fm = tk.LabelFrame(self.root, text=" Moedas Aceites ", fg="white", bg="#121214"); fm.pack(pady=2, fill="x", padx=15)
        
        # INTERFACE DINÂMICA: Gera os botões automaticamente com base no ajuste de moedas dos tubos
        lista_moedas = [f"{m:.2f}" for m in sorted(self.vm.tubos.keys())]
        for m in lista_moedas: 
            tk.Button(fm, text=f"{m}€", bg="#1b4d3e", fg="#00ff00", font=("Arial", 8, "bold"), command=lambda v=m: self.add_m(v)).pack(side="left", padx=2, expand=True)
            
        fp = tk.LabelFrame(self.root, text=" Mercadorias ", fg="white", bg="#121214"); fp.pack(pady=2, fill="x", padx=15)
        self.b_prods = {}
        for s in ["A1", "A2", "A3", "B1", "B2", "B3"]:
            b = tk.Button(fp, text="", bg="#1f1f23", fg="white", font=("Consolas", 8), anchor="w", command=lambda sl=s: self.venda(sl))
            b.pack(pady=1, fill="x"); self.b_prods[s] = b
        f_dest = tk.LabelFrame(self.root, text=" Especial ", fg="#ff0055", bg="#121214"); f_dest.pack(pady=2, fill="x", padx=15)
        self.btn_dest = tk.Button(f_dest, text="", bg="#ff0055", fg="white", font=("Arial", 9, "bold"), command=lambda: self.venda("DESTINO")); self.btn_dest.pack(fill="x", pady=2)
        tk.Button(self.root, text="🔄 Devolver Troco", bg="#333", fg="white", command=self.troco).pack(pady=4, fill="x", padx=15)
        self.txt.pack(pady=3, fill="both", expand=True, padx=15); self.up()
    def up(self):
        self.lbl_saldo.configure(text=f"{self.vm.saldo:.2f}€")
        for s, b in self.b_prods.items():
            p = self.vm.produtos[s]; t = f"[{p['stock']} UN]" if p['stock'] > 0 else "[ESG]"
            b.configure(text=f"{s} - {p['nome']:<16} {p['preco']:.2f}€ {t}", state="normal" if p['stock'] > 0 else "disabled")
        pd = self.vm.produtos["DESTINO"]; td = f"[{pd['stock']} UN]" if pd['stock'] > 0 else "[ESG]"
        self.btn_dest.configure(text=f"✨ {pd['nome'].upper()} ({pd['preco']:.2f}€) {td}", state="normal" if pd['stock'] > 0 else "disabled")
    def add_m(self, v):
        if self.vm.inserir_moeda(Decimal(v)): self.up()
    def simular_mbway(self):
        self.vm.saldo += Decimal("2.50"); logger.info("✅ MB WAY: +2.50€"); self.vm.som("curto"); self.up()
    def validar(self):
        c = self.ent_nif.get().strip()
        if not c: return
        if self.vm.autenticar_admin(c):
            self.cv.itemconfig(self.lbl_pique, text="🛠️ ADMIN ACTIVE\nStock e moedas reabastecidos."); [p.update({"stock": 20}) for p in self.vm.produtos.values()]; [self.vm.tubos.update({m: 20}) for m in self.vm.tubos]; self.vm.salvar(); self.up(); self.ent_nif.delete(0, tk.END); return
        if self.vm.aplicar_voucher(c): self.up(); self.ent_nif.delete(0, tk.END); return
        if re.match(r"^\d{9}$", c): logger.info(f"👤 NIF {c} registado."); self.cv.itemconfig(self.lbl_pique, text=f"👤 NIF {c}\nPronto para comprar.")
        else: logger.warning("⚠️ Inválido.")
    def venda(self, s):
        if time.time() - self.u_clique < 0.5: return
        self.u_clique = time.time(); inp = self.ent_nif.get().strip(); nif = inp if re.match(r"^\d{9}$", inp) else "999999999"
        if self.vm.comprar_produto(s, nif): self.ent_nif.delete(0, tk.END); self.cv.itemconfig(self.lbl_pique, text="✅ Compra concluída!")
        self.up()
    def troco(self):
        tr = self.vm.devolver_saldo()
        if tr: self.cv.itemconfig(self.lbl_pique, text=f"💰 TROCO EMITIDO\n" + ", ".join([f"{q}x {m}€" for m, q in tr.items()]))
        elif tr == {}: self.cv.itemconfig(self.lbl_pique, text="📊 Sem saldo para devolver.")
        self.up()
if __name__ == "__main__":
    vm = VendingMachine(); app = VMUi(vm); logger.info("🚀 Soyuz Inicializada."); app.root.mainloop()
