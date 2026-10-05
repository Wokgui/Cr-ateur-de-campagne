"""Semantic-ish local asset resolver. Deterministic fallback for the future ChatGPT layer."""
from __future__ import annotations
import json, re, unicodedata
from pathlib import Path

ALIASES={
 "voiture":["car","cara","sedan","vehicle","hatchback"],
 "ambulance":["ambulance"],
 "camion":["truck","van"],
 "etagere":["shelf","shelves","rack"],
 "chaise":["chair"],
 "table":["table"],
 "lit":["bed"],
 "poubelle":["trash","garbage","dumpster"],
 "barriere":["fence","barrier"],
}

def _plain(s):
 s=unicodedata.normalize("NFD",s.lower())
 return "".join(c for c in s if unicodedata.category(c)!="Mn")

def load_catalog(path):
 return json.loads(Path(path).read_text(encoding="utf-8"))["assets"]

def resolve_asset(query, assets, category="model"):
 q=_plain(query)
 terms=set(re.findall(r"[a-z0-9]+",q))
 expanded=set(terms)
 for k,vals in ALIASES.items():
  if k in terms: expanded.update(vals)
 candidates=[]
 for a in assets:
  if a.get("category")!=category: continue
  path=_plain(a["path"])
  score=sum(5 for t in terms if t in path)+sum(2 for t in expanded-terms if t in path)
  if score:
   if a.get("source","").lower().startswith("pak"): score+=1
   candidates.append((score,len(path),a))
 if not candidates: return None
 candidates.sort(key=lambda x:(-x[0],x[1],x[2]["path"]))
 return candidates[0][2]
