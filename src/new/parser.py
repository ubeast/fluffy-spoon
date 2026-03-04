"""
EDI X12 315 Parser - Ocean Container Status
============================================
Parses ISA/GS/ST/SE/GE/IEA envelope with 315 transaction sets.

Segment separator : \x15 (vertical tab / group separator)
Element separator : *

Usage (module):
    from edi315_parser import parse_edi315
    result = parse_edi315(raw_string)
    df = result.to_dataframe()

Usage (CLI):
    python edi315_parser.py input.edi [output.json] [output.csv]
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import re

# ─── Reference Tables ─────────────────────────────────────────────────────────

STATUS_CODES: dict[str, str] = {
    "X1": "Container Gate-In at Port of Loading",
    "X2": "Container Loaded on Vessel",
    "X3": "Container Discharged from Vessel",
    "X4": "Container Gate-Out at Port",
    "X5": "Container on Rail",
    "X6": "Container Ingate at Inland Facility",
    "X7": "Container Outgate at Inland Facility",
    "X8": "Container Picked Up",
    "AE": "Loaded on Vessel (Departed)",
    "VD": "Vessel Departed",
    "RD": "Container Returned Empty",
    "I":  "Container Ingate",
    "W":  "Container at Warehouse / Gate-In",
    "OA": "Out-Gated with Cargo",
    "L":  "Container Loaded",
}

PORT_QUALIFIERS: dict[str, str] = {
    "R": "Origin",
    "L": "Port of Loading",
    "1": "Port of Discharge",
    "2": "Place of Delivery",
    "M": "Final Delivery",
    "Y": "Transshipment Port",
}

N9_CODES: dict[str, str] = {
    "BN": "Booking Number",
    "FI": "Filed Booking Number",
    "ZZ": "Cargo Category / Routing Code",
    "EQ": "Container Number",
    "TG": "Transportation Control Number",
    "SN": "Seal Number",
    "P4": "Priority",
    "PG": "Package Count",
    "CT": "Contract Number",
    "BM": "Bill of Lading",
    "CR": "Carrier Reference",
    "TT": "Terminal Code",
    "DO": "Delivery Order",
}

# ─── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class Interchange:
    sender_id: str = ""
    receiver_id: str = ""
    sender_qualifier: str = ""
    receiver_qualifier: str = ""
    date: Optional[str] = None
    time: Optional[str] = None
    control_number: str = ""
    usage_indicator: str = ""
    version_number: str = ""


@dataclass
class FunctionalGroup:
    functional_id_code: str = ""
    sender_code: str = ""
    receiver_code: str = ""
    date: Optional[str] = None
    time: Optional[str] = None
    control_number: str = ""
    version_code: str = ""


@dataclass
class StatusEvent:
    status_code: str = ""
    status_description: str = ""
    status_date: Optional[str] = None
    status_time: Optional[str] = None
    container_prefix: str = ""
    container_number: str = ""
    load_status: str = ""       # L=Loaded, E=Empty
    equipment_type_code: str = ""  # e.g. 42G1, 22T0
    current_location: str = ""
    equipment_status_code: str = ""  # EA=Actual


@dataclass
class Reference:
    qualifier: str = ""
    label: str = ""
    reference_id: str = ""
    freeform: str = ""


@dataclass
class Vessel:
    vessel_code: str = ""
    vessel_name: str = ""
    voyage_number: str = ""
    carrier_code: str = ""
    service_code: str = ""
    type_code: str = ""
    weight: Optional[float] = None
    weight_unit: str = ""
    tonnage: Optional[float] = None


@dataclass
class Location:
    port_qualifier: str = ""
    port_role: str = ""
    location_type: str = ""
    location_code: str = ""
    port_name: str = ""
    country: str = ""
    terminal_code: str = ""
    date: Optional[str] = None
    time: Optional[str] = None
    date_type: str = ""  # Actual / Estimated

    @property
    def full_name(self) -> str:
        parts = [p for p in [self.port_name, self.country] if p]
        return ", ".join(parts)


@dataclass
class Transaction:
    transaction_set_id: str = ""
    control_number: str = ""
    segment_count: int = 0
    status_event: Optional[StatusEvent] = None
    references: list[Reference] = field(default_factory=list)
    vessel: Optional[Vessel] = None
    locations: list[Location] = field(default_factory=list)

    def get_ref(self, qualifier: str) -> Optional[str]:
        """Return the referenceId for the first N9 segment matching qualifier."""
        for r in self.references:
            if r.qualifier == qualifier:
                return r.reference_id
        return None

    def get_location(self, qualifier: str) -> Optional[Location]:
        for loc in self.locations:
            if loc.port_qualifier == qualifier:
                return loc
        return None

    @property
    def summary(self) -> dict:
        """Flat dict of the most useful fields — ideal for DataFrames."""
        def port(q): 
            loc = self.get_location(q)
            return loc.full_name if loc else None

        return {
            "container_number":  self.status_event.container_number if self.status_event else self.get_ref("EQ"),
            "booking_number":    self.get_ref("BN"),
            "bill_of_lading":    self.get_ref("BM"),
            "seal_number":       self.get_ref("SN"),
            "contract_number":   self.get_ref("CT"),
            "status_code":       self.status_event.status_code if self.status_event else None,
            "status":            self.status_event.status_description if self.status_event else None,
            "status_date":       self.status_event.status_date if self.status_event else None,
            "status_time":       self.status_event.status_time if self.status_event else None,
            "current_location":  self.status_event.current_location if self.status_event else None,
            "vessel_name":       self.vessel.vessel_name if self.vessel else None,
            "voyage_number":     self.vessel.voyage_number if self.vessel else None,
            "origin":            port("R"),
            "load_port":         port("L"),
            "discharge_port":    port("1"),
            "final_delivery":    port("M"),
        }


@dataclass
class EDI315Result:
    interchange: Interchange = field(default_factory=Interchange)
    functional_group: FunctionalGroup = field(default_factory=FunctionalGroup)
    transactions: list[Transaction] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def to_dataframe(self):
        """Return a pandas DataFrame of transaction summaries."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required: pip install pandas")
        rows = [tx.summary for tx in self.transactions]
        return pd.DataFrame(rows)


# ─── Parser ───────────────────────────────────────────────────────────────────

def parse_edi315(raw: str) -> EDI315Result:
    """
    Parse a raw EDI X12 315 string into an EDI315Result.

    Accepts both escaped (\\x15) and literal segment separators.
    """
    # Normalise: handle escaped \x15 sequences and strip line endings
    normalized = raw.replace("\\x15", "\x15").replace("\r\n", "").replace("\r", "").replace("\n", "")

    segments = [s.strip() for s in normalized.split("\x15") if s.strip()]

    result = EDI315Result()
    current_tx: Optional[Transaction] = None

    for seg in segments:
        e = seg.split("*")
        seg_id = e[0]

        # ── ISA ──────────────────────────────────────────────────────────────
        if seg_id == "ISA":
            result.interchange = Interchange(
                sender_qualifier   = _get(e, 5),
                sender_id          = _get(e, 6),
                receiver_qualifier = _get(e, 7),
                receiver_id        = _get(e, 8),
                date               = _fmt_date(_get(e, 9)),
                time               = _fmt_time(_get(e, 10)),
                version_number     = _get(e, 12),
                control_number     = _get(e, 13),
                usage_indicator    = "Production" if _get(e, 15) == "P" else "Test",
            )

        # ── GS ───────────────────────────────────────────────────────────────
        elif seg_id == "GS":
            result.functional_group = FunctionalGroup(
                functional_id_code = _get(e, 1),
                sender_code        = _get(e, 2),
                receiver_code      = _get(e, 3),
                date               = _fmt_date(_get(e, 4)),
                time               = _fmt_time(_get(e, 5)),
                control_number     = _get(e, 6),
                version_code       = _get(e, 8),
            )

        # ── ST ───────────────────────────────────────────────────────────────
        elif seg_id == "ST":
            current_tx = Transaction(
                transaction_set_id = _get(e, 1),
                control_number     = _get(e, 2),
            )

        # ── B4 ───────────────────────────────────────────────────────────────
        # Positions: [3]=status [4]=date [5]=time [7]=prefix [8]=num
        #            [9]=load   [10]=equip_type [11]=location [12]=eq_status
        elif seg_id == "B4" and current_tx:
            code = _get(e, 3)
            prefix = _get(e, 7)
            number = _get(e, 8)
            current_tx.status_event = StatusEvent(
                status_code          = code,
                status_description   = STATUS_CODES.get(code, f"Unknown ({code})"),
                status_date          = _fmt_date(_get(e, 4)),
                status_time          = _fmt_time(_get(e, 5)),
                container_prefix     = prefix,
                container_number     = prefix + number,
                load_status          = _get(e, 9),
                equipment_type_code  = _get(e, 10),
                current_location     = _clean_location(_get(e, 11)),
                equipment_status_code= _get(e, 12),
            )

        # ── N9 ───────────────────────────────────────────────────────────────
        elif seg_id == "N9" and current_tx:
            qualifier = _get(e, 1)
            current_tx.references.append(Reference(
                qualifier    = qualifier,
                label        = N9_CODES.get(qualifier, qualifier),
                reference_id = _get(e, 2),
                freeform     = _get(e, 3),
            ))

        # ── Q2 ───────────────────────────────────────────────────────────────
        # Positions: [1]=vessel_code [6]=weight [7]=weight_unit [8]=voyage
        #            [10]=service [11]=carrier [12]=type [13]=vessel_name [14]=tonnage
        elif seg_id == "Q2" and current_tx:
            weight_raw  = _get(e, 6)
            tonnage_raw = _get(e, 14)
            current_tx.vessel = Vessel(
                vessel_code  = _get(e, 1),
                weight       = float(weight_raw) if weight_raw else None,
                weight_unit  = _get(e, 7),
                voyage_number= _get(e, 8),
                service_code = _get(e, 10),
                carrier_code = _get(e, 11),
                type_code    = _get(e, 12),
                vessel_name  = _get(e, 13),
                tonnage      = float(tonnage_raw) if tonnage_raw else None,
            )

        # ── R4 ───────────────────────────────────────────────────────────────
        elif seg_id == "R4" and current_tx:
            qual = _get(e, 1)
            current_tx.locations.append(Location(
                port_qualifier = qual,
                port_role      = PORT_QUALIFIERS.get(qual, qual),
                location_type  = _get(e, 2),
                location_code  = _get(e, 3),
                port_name      = _get(e, 4),
                country        = _get(e, 5),
                terminal_code  = _get(e, 6),
            ))

        # ── DTM ──────────────────────────────────────────────────────────────
        elif seg_id == "DTM" and current_tx and current_tx.locations:
            qualifier = _get(e, 1)
            loc = current_tx.locations[-1]
            loc.date      = _fmt_date(_get(e, 2))
            loc.time      = _fmt_time(_get(e, 3))
            loc.date_type = "Actual" if qualifier == "140" else "Estimated" if qualifier == "139" else qualifier

        # ── SE ───────────────────────────────────────────────────────────────
        elif seg_id == "SE" and current_tx:
            current_tx.segment_count = int(_get(e, 1) or 0)
            result.transactions.append(current_tx)
            current_tx = None

    return result


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get(elements: list[str], index: int) -> str:
    """Safely get element by index, returning empty string if missing."""
    try:
        return elements[index].strip()
    except IndexError:
        return ""


def _fmt_date(raw: str) -> Optional[str]:
    """Format EDI date: YYYYMMDD → YYYY-MM-DD, YYMMDD → YYYY-MM-DD."""
    if not raw:
        return None
    if len(raw) == 8:
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    if len(raw) == 6:
        return f"20{raw[:2]}-{raw[2:4]}-{raw[4:6]}"
    return raw


def _fmt_time(raw: str) -> Optional[str]:
    """Format EDI time: HHMM → HH:MM."""
    if not raw or len(raw) < 4:
        return raw or None
    return f"{raw[:2]}:{raw[2:4]}"


def _clean_location(raw: str) -> str:
    """Collapse multiple spaces in location strings."""
    if not raw:
        return ""
    return re.sub(r"\s{2,}", ", ", raw).rstrip(", ").strip()


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _print_results(result: EDI315Result) -> None:
    isa = result.interchange
    print("╔══════════════════════════════════════════════╗")
    print("║          EDI 315 Parse Results               ║")
    print("╚══════════════════════════════════════════════╝\n")
    print(f"  Sender:        {isa.sender_id}")
    print(f"  Receiver:      {isa.receiver_id}")
    print(f"  Date/Time:     {isa.date}  {isa.time}")
    print(f"  Control #:     {isa.control_number}")
    print(f"  Environment:   {isa.usage_indicator}")
    print(f"  Transactions:  {len(result.transactions)}\n")

    for i, tx in enumerate(result.transactions, 1):
        s = tx.summary
        print(f"  ─── Transaction {i:02d} {'─' * 30}")
        print(f"    Container:     {s['container_number']}")
        print(f"    Booking #:     {s['booking_number']}")
        print(f"    B/L:           {s['bill_of_lading']}")
        print(f"    Seal #:        {s['seal_number'] or '—'}")
        print(f"    Status:        [{s['status_code']}] {s['status']}")
        print(f"    Date/Time:     {s['status_date']}  {s['status_time']}")
        print(f"    Location:      {s['current_location']}")
        print(f"    Vessel:        {s['vessel_name']}  (Voy: {s['voyage_number']})")
        print(f"    Route:         {s['origin']}  →  {s['load_port']}  →  {s['discharge_port']}  →  {s['final_delivery']}")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python edi315_parser.py <input.edi> [output.json] [output.csv]")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        raw = f.read()

    result = parse_edi315(raw)
    _print_results(result)

    if len(sys.argv) >= 3:
        out_json = sys.argv[2]
        with open(out_json, "w", encoding="utf-8") as f:
            f.write(result.to_json())
        print(f"  ✓ JSON written to: {out_json}")

    if len(sys.argv) >= 4:
        out_csv = sys.argv[3]
        df = result.to_dataframe()
        df.to_csv(out_csv, index=False)
        print(f"  ✓ CSV written to:  {out_csv}")
