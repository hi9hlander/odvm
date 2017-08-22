from odvm.groupby import GroupByNormal
from odvm.quads import quads


class VoxelModel(GroupByNormal):
   def __init__( self, name, fmt ):
      GroupByNormal.__init__( self, name, fmt )
      self.quads = quads(self)

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
