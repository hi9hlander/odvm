from odvm.voxelmodel import VoxelModel
from collections import defaultdict


def ijk1b_to_idx0_7( i, j, k ):
   assert( 0 <= i <= 1 and 0 <= j <= 1 and 0 <= k <= 1 )
   return ((k&1)<<2)|((j&1)<<1)|(i&1)


def idx0_7_to_ijk1b( idx ):
   assert( 0 <= idx <= 7 )
   return ( idx&1, (idx&2)>>1, (idx&4)>>2 )


def ijk2b_to_idx0_63( i, j, k ):
   assert( 0 <= i <= 3 and 0 <= j <= 3 and 0 <= k <= 3 )
   return ( ((k&1)<<2)|((j&1)<<1)|(i&1) ) | ( ((k&2)<<4)|((j&2)<<3)|((i&2)<<2) )


def idx0_63_to_ijk2b( idx ):
   assert( 0 <= idx <= 63 )
   return ( ((idx&8)>>2)|(idx&1), ((idx&16)>>3)|((idx&2)>>1), ((idx&32)>>4)|((idx&4)>>2) )


class packed_cuboids(list):
   def __init__(self):
      list.__init__(self)
      self.extend([0]*64)

   def add( self, i, j, k ):
      assert( 0 <= i <= 15 and 0 <= j <= 15 and 0 <= k <= 15 )
      self[ijk2b_to_idx0_63(i>>2,j>>2,k>>2)] |= 1<<ijk2b_to_idx0_63(i&3,j&3,k&3)


class cuboids_level(list):
   def __init__( self, bits=8 ):
      list.__init__(self)
      self.extend([None]*64)
      self.bits = bits

   def add( self, i, j, k ):
      idx = ijk2b_to_idx0_63(i>>self.bits,j>>self.bits,k>>self.bits)
      if self[idx] is None:
         if self.bits == 4: self[idx] = packed_cuboids()
         else             : self[idx] = cuboids_level(self.bits-2)
      mask = (1<<self.bits)-1
      self[idx].add( i&mask, j&mask, k&mask )

   def items( self ):
      if self.bits == 4:
         for idx,cs in enumerate(self):
            if cs is not None:
               i,j,k = idx0_63_to_ijk2b(idx)
               yield ( (i<<4,j<<4,k<<4), cs )
      else:
         for idx,cs1 in enumerate(self):
            if cs1 is not None:
               i,j,k = idx0_63_to_ijk2b(idx)
               i <<= self.bits
               j <<= self.bits
               k <<= self.bits
               for ijk,cs in cs1.items():
                  yield ( (i+ijk[0],j+ijk[1],k+ijk[2]), cs )


class dict_cuboids_level(defaultdict):
   def __init__(self): defaultdict.__init__(self,cuboids_level)


class OptimizedVM(VoxelModel):
   def __init__( self, name, fmt ):
      VoxelModel.__init__( self, name, fmt )
      self.cuboids = ( dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), 
                       dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level() )

   def add(self,p2s,i,j,k,c,p2i=0,p2j=0,p2k=0):
      ii = 0 if i >= 0 else 1
      ij = 0 if j >= 0 else 1
      ik = 0 if k >= 0 else 1
      self.cuboids[ijk1b_to_idx0_7(ii,ij,ik)][(c,1<<p2s,1<<p2i,1<<p2j,1<<p2k)].add(abs(i),abs(j),abs(k))

   def optimize(self):
      with self.quads:
         for idx2,cs2 in enumerate(self.cuboids):
            si,sj,sk = idx0_7_to_ijk1b(idx2)
            si = 1-si-si
            sj = 1-sj-sj
            sk = 1-sk-sk
            for key1,cs1 in cs2.items():
               c,s,di,dj,dk = key1
               for ijk,cs in cs1.items():
                  for idx,mask in enumerate(cs):
                     if not mask: continue
                     i,j,k = idx0_63_to_ijk2b(idx)
                     i = ijk[0] + (i<<2)
                     j = ijk[1] + (j<<2)
                     k = ijk[2] + (k<<2)
                     m = 1
                     for idx1 in range(64):
                        if mask&m:
                           ijk1 = idx0_63_to_ijk2b(idx1)
                           self.quads.add( s,si*(i+ijk1[0]),sj*(j+ijk1[1]),sk*(k+ijk1[2]),
                              ( ( ( 0,  0,  0, di, dj,  0 ), c ),
                                ( ( 0,  0,-dk,  0, dj,  0 ), c ),
                                ( ( di, 0,  0, di, dj,-dk ), c ),
                                ( ( 0,  0,-dk, di,  0,  0 ), c ),
                                ( ( 0, dj,-dk, di,  0,-dk ), c ),
                                ( ( 0, dj,  0, di, dj,-dk ), c ) ) )
                        m += m
