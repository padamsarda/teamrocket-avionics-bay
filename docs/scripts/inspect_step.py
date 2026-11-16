import sys, cadquery as cq
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_LabelSequence
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
p=sys.argv[1]
s=cq.importers.importStep(p)
bb=s.val().BoundingBox(); print("ALL",round(bb.xmin,2),round(bb.xmax,2),round(bb.ymin,2),round(bb.ymax,2),round(bb.zmin,2),round(bb.zmax,2))
sol=s.solids().vals(); print("nsolids",len(sol))
for i,v in enumerate(sol):
    b=v.BoundingBox()
    print(i, "x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f] size %.2fx%.2fx%.2f"%(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax,b.xlen,b.ylen,b.zlen))
