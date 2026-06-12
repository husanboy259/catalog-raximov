"""
Mebel katalogi - ma'lumotlar boshqaruvi (JSON fayl orqali)
"""

import json
import os
from datetime import datetime
from typing import Optional

DATA_FILE = "katalog.json"


class MebelKatalog:
    kategoriyalar = [
        "Divan", "Kreslo", "Stol", "Stul", "Shkaf",
        "Krovat", "Komod", "Oshxona mebellari",
        "Ofis mebellari", "Boshqa"
    ]

    def __init__(self):
        self._data: dict[str, dict] = {}
        self._counter: int = 0
        self._yukla()

    # ── Saqlash / Yuklash ──────────────────────────────────────────────────────

    def _yukla(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self._data    = saved.get("mahsulotlar", {})
                    self._counter = saved.get("counter", 0)
            except (json.JSONDecodeError, KeyError):
                self._data    = {}
                self._counter = 0

    def _saqlash(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"mahsulotlar": self._data, "counter": self._counter},
                f, ensure_ascii=False, indent=2
            )

    # ── ID yaratish ────────────────────────────────────────────────────────────

    def _yangi_id(self) -> str:
        self._counter += 1
        return f"DAM-{self._counter:04d}"

    # ── CRUD ───────────────────────────────────────────────────────────────────

    def qosh(self, nomi: str, narxi: int, tavsif: str,
             kategoriya: str, rasm_id: str) -> dict:
        """Yangi mahsulot qo'shish."""
        mid = self._yangi_id()
        mahsulot = {
            "id":         mid,
            "nomi":       nomi,
            "narxi":      narxi,
            "tavsif":     tavsif,
            "kategoriya": kategoriya,
            "rasm_id":    rasm_id,
            "sana":       datetime.now().strftime("%d.%m.%Y %H:%M"),
            "holat":      "Aktiv",
        }
        self._data[mid] = mahsulot
        self._saqlash()
        return mahsulot

    def tahrirlash(self, mid: str, maydon: str, yangi_qiymat) -> bool:
        """Mahsulot maydonini yangilash."""
        if mid not in self._data:
            return False
        self._data[mid][maydon] = yangi_qiymat
        self._saqlash()
        return True

    def ochir(self, mid: str) -> bool:
        """Mahsulotni o'chirish."""
        if mid not in self._data:
            return False
        del self._data[mid]
        self._saqlash()
        return True

    # ── Qidirish / Filtrlash ───────────────────────────────────────────────────

    def id_boyicha(self, mid: str) -> Optional[dict]:
        return self._data.get(mid.upper())

    def barchasi(self) -> list[dict]:
        return list(self._data.values())

    def kategoriya_boyicha(self, kategoriya: str) -> list[dict]:
        return [m for m in self._data.values() if m["kategoriya"] == kategoriya]

    def qidirish(self, so_z: str) -> list[dict]:
        so_z_l = so_z.lower()
        return [
            m for m in self._data.values()
            if so_z_l in m["nomi"].lower()
            or so_z_l in m["id"].lower()
            or so_z_l in m["tavsif"].lower()
        ]

    def narx_boyicha(self, teskari: bool = False) -> list[dict]:
        return sorted(self._data.values(), key=lambda m: m["narxi"], reverse=teskari)

    # ── Statistika ─────────────────────────────────────────────────────────────

    def statistika(self) -> dict:
        mahsulotlar = list(self._data.values())
        kat_soni = {k: 0 for k in self.kategoriyalar}
        for m in mahsulotlar:
            if m["kategoriya"] in kat_soni:
                kat_soni[m["kategoriya"]] += 1

        narxlar = [m["narxi"] for m in mahsulotlar] if mahsulotlar else [0]
        return {
            "jami":          len(mahsulotlar),
            "aktiv":         sum(1 for m in mahsulotlar if m["holat"] == "Aktiv"),
            "kategoriyalar": kat_soni,
            "min_narx":      min(narxlar),
            "max_narx":      max(narxlar),
            "ortacha_narx":  int(sum(narxlar) / len(narxlar)) if narxlar else 0,
        }
