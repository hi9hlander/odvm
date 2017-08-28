from odvm.voxelmodel import VoxelModel
from odvm.cuboids import cuboids_level, ijk1b_to_idx0_7, idx0_7_to_ijk1b, idx0_63_to_ijk2b
from collections import defaultdict


class dict_cuboids_level(defaultdict):
   def __init__(self): defaultdict.__init__(self,cuboids_level)


class OptimizedVM(VoxelModel):
   def __init__( self, name, fmt, level ):
      VoxelModel.__init__( self, name, fmt )
      self.level   = level
      self.cuboids = ( dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), 
                       dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level() )
      self.added   = ( dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), 
                       dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level() )

   def set_opt_level( self, level ): self.level = level

   def add(self,p2s,i,j,k,c,p2i=0,p2j=0,p2k=0):
      ii  = 0 if i >= 0 else 1
      ij  = 0 if j >= 0 else 1
      ik  = 0 if k >= 0 else 1
      idx = ijk1b_to_idx0_7(ii,ij,ik)
      key = (c,1<<p2s,1<<p2i,1<<p2j,1<<p2k)
      self.cuboids[idx][key].add(abs(i),abs(j),abs(k))

      if   self.level == 0: VoxelModel.add(self,p2s,i,j,k,c,p2i,p2j,p2k)
      elif self.level == 1: self.added[idx][key].add(abs(i),abs(j),abs(k))

   def sub(self,p2s,i,j,k,p2i=0,p2j=0,p2k=0):
      ii = 0 if i >= 0 else 1
      ij = 0 if j >= 0 else 1
      ik = 0 if k >= 0 else 1

      s  = 1<<p2s
      di = 1<<p2i
      dj = 1<<p2j
      dk = 1<<p2k

      for key,cs in self.cuboids[ijk1b_to_idx0_7(ii,ij,ik)].items():
         if key[1] == s and key[2] == di and key[3] == dj and key[4] == dk and cs.sub(abs(i),abs(j),abs(k)):
            if   self.level == 0 or self.level == 1: # for level 1 keep list and process in optimize() call
               cim = self.get(s,i-1,j,k,di,dj,dk)
               if cim is None: cim = key[0]
               cip = self.get(s,i+1,j,k,di,dj,dk)
               if cip is None: cip = key[0]
               cjm = self.get(s,i,j-1,k,di,dj,dk)
               if cjm is None: cjm = key[0]
               cjp = self.get(s,i,j+1,k,di,dj,dk)
               if cjp is None: cjp = key[0]
               ckm = self.get(s,i,j,k-1,di,dj,dk)
               if ckm is None: ckm = key[0]
               ckp = self.get(s,i,j,k+1,di,dj,dk)
               if ckp is None: ckp = key[0]

               self.quads.add( s,i,j,k,
                  ( ( (  0,  0,  0,  0, dj,-dk ), cim ),
                    ( ( di,  0,-dk, di, dj,  0 ), cip ),
                    ( (  0,  0,  0, di,  0,-dk ), cjm ),
                    ( (  0, dj,-dk, di, dj,  0 ), cjp ),
                    ( (  0, dj,  0, di,  0,  0 ), ckm ),
                    ( (  0,  0,-dk, di, dj,-dk ), ckp ) ) )
            return

   def get(self,s,i,j,k,di,dj,dk):
      ii = 0 if i >= 0 else 1
      ij = 0 if j >= 0 else 1
      ik = 0 if k >= 0 else 1
      for key,cs in self.cuboids[ijk1b_to_idx0_7(ii,ij,ik)].items():
         if key[1] == s and key[2] == di and key[3] == dj and key[4] == dk and cs.get(abs(i),abs(j),abs(k)): return key[0]
      else: return None

   def optimize(self):
      if self.level == 0: return
      with self.quads:
         if   self.level == 1: cuboids = self.added
         elif self.level == 2:
            self.quads.reset()
            cuboids = self.cuboids
         else: assert( 0 <= self.level <= 2 )
         for idx2,cs2 in enumerate(cuboids):
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
                     if self.level == 1: cs[idx] = 0
