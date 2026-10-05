"""Index loose L4D2 assets and VPK directory entries without extracting them."""
from __future__ import annotations
import argparse, json, struct
from pathlib import Path

EXT_CATEGORIES={"mdl":"model","vmt":"material","vtf":"texture","wav":"sound","mp3":"sound"}

def _cstring(f):
    b=bytearray()
    while True:
        c=f.read(1)
        if not c: raise EOFError("Unexpected EOF in VPK tree")
        if c==b"\0": return b.decode("utf-8",errors="replace")
        b.extend(c)

def read_vpk_index(path: Path):
    out=[]
    with path.open("rb") as f:
        sig,ver,tree_size=struct.unpack("<III",f.read(12))
        if sig!=0x55AA1234: raise ValueError(f"Not a VPK: {path}")
        if ver==2: f.read(16)
        while True:
            ext=_cstring(f)
            if not ext: break
            while True:
                directory=_cstring(f)
                if not directory: break
                while True:
                    name=_cstring(f)
                    if not name: break
                    crc,preload,archive,offset,length,term=struct.unpack("<IHHIIH",f.read(18))
                    if term!=0xFFFF: raise ValueError("Invalid VPK entry terminator")
                    f.seek(preload,1)
                    rel=(("" if directory==" " else directory)+"/"+name+"."+ext).lstrip("/")
                    out.append(rel.replace("\\","/"))
    return out

def classify(rel):
    ext=Path(rel).suffix.lower().lstrip(".")
    return EXT_CATEGORIES.get(ext)

def scan(root: Path):
    rows=[]
    seen=set()
    def add(rel,source):
        rel=rel.replace("\\","/")
        cat=classify(rel)
        if cat and rel.lower() not in seen:
            seen.add(rel.lower()); rows.append({"path":rel,"category":cat,"source":source})
    for p in root.rglob("*"):
        if p.is_file() and classify(p.name):
            add(str(p.relative_to(root)),"loose")
    for p in root.rglob("*_dir.vpk"):
        try:
            for rel in read_vpk_index(p): add(rel,p.name)
        except (OSError,EOFError,ValueError) as e:
            print(f"warning: {p}: {e}")
    rows.sort(key=lambda x:(x["category"],x["path"]))
    return {"root":str(root),"count":len(rows),"assets":rows}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("l4d2_root",type=Path)
    ap.add_argument("--out",type=Path,default=Path("build/assets.json"))
    a=ap.parse_args()
    data=scan(a.l4d2_root)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
    print(f"{data['count']} assets indexed -> {a.out}")

if __name__=="__main__": main()
