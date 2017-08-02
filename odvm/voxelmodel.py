from panda3d.core import *
from odvm.quads import Quads


class VoxelModel(Geom):
   def __init__(self):
      Geom.__init__( self, GeomVertexData( 'vertices', GeomVertexFormat.get_v3n3c4(), Geom.UH_static ) )
      self.quads = Quads(self)
      self.add_primitive(self.quads)

   def add(self,p2s,i,j,k,c,p2i=0,p2j=0,p2k=0):
      di = 1 << p2i
      dj = 1 << p2j
      dk = 1 << p2k
      self.quads.add( 1<<p2s,i,j,k,
         ( ( ( 0,  0,  0, di, dj,  0 ), c ),
           ( ( 0,  0,-dk,  0, dj,  0 ), c ),
           ( ( di, 0,  0, di, dj,-dk ), c ),
           ( ( 0,  0,-dk, di,  0,  0 ), c ),
           ( ( 0, dj,-dk, di,  0,-dk ), c ),
           ( ( 0, dj,  0, di, dj,-dk ), c ) ) )
