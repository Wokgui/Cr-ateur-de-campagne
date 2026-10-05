import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from vmf_generator import box_solid, Vec3

class BrushGeometryTests(unittest.TestCase):
    def test_planes_enclose_center_and_axes_are_tangent(self):
        solid,_=box_solid(10,100,Vec3(-118,-78.5,-8),Vec3(118,78.5,0),"DEV/DEV_MEASUREGENERIC01")
        faces=solid.split('"plane" ')[1:]
        self.assertEqual(len(faces),6)
        center=(0,0,-4)
        for face in faces:
            points=[tuple(map(float,x.split())) for x in re.findall(r'\(([^)]+)\)',face.split('\n')[0])]
            a,b,c=points
            v=[a[i]-b[i] for i in range(3)];w=[c[i]-b[i] for i in range(3)]
            normal=(v[1]*w[2]-v[2]*w[1],v[2]*w[0]-v[0]*w[2],v[0]*w[1]-v[1]*w[0])
            self.assertLess(sum(normal[i]*(center[i]-a[i]) for i in range(3)),0)
            for name in ('uaxis','vaxis'):
                axis=tuple(map(float,re.search(name+r'" "\[([^]]+)\]',face).group(1).split()[:3]))
                self.assertEqual(sum(axis[i]*normal[i] for i in range(3)),0)
