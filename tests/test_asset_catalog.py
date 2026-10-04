import struct
from pathlib import Path
from src.asset_catalog import read_vpk_index, classify

def _s(x): return x.encode()+b"\\0"

def test_vpk_v1_index(tmp_path):
    tree=_s("mdl")+_s("props")+_s("car")+struct.pack("<IHHIIH",0,0,0x7fff,0,0,0xffff)+_s("")+_s("")+_s("")
    p=tmp_path/"pak01_dir.vpk"
    p.write_bytes(struct.pack("<III",0x55AA1234,1,len(tree))+tree)
    assert read_vpk_index(p)==["props/car.mdl"]

def test_categories():
    assert classify("models/a.mdl")=="model"
    assert classify("materials/a.vmt")=="material"
    assert classify("readme.txt") is None
