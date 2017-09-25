from .voxelmodel import VoxelModel
from .cuboids import cuboids_level, ijk1b_to_idx0_7, idx0_7_to_ijk1b, idx0_63_to_ijk2b, mask_to_2x2x2, mask_to_1x2x2, mask_to_2x1x2, mask_to_2x2x1, mask_to_2x1x1, mask_to_1x2x1, mask_to_1x1x2, mask_to_i2_j2, mask_to_i2_k2, mask_to_j2_k2
from collections import defaultdict


class dict_cuboids_level(defaultdict):
   def __init__(self): defaultdict.__init__(self,cuboids_level)


class OptimizedVM(VoxelModel):
   def __init__( self, name, fmt, level ):
      VoxelModel.__init__( self, name, fmt )
      self.opt_level = level
      self.prv_level = -2
      self.cmp_level = 0
      self.cuboids   = ( dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), 
                         dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level() )
      self.added     = ( dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), 
                         dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level(), dict_cuboids_level() )
      self.updating  = 0

   def set_opt_level( self, level ): self.opt_level = level

   def optimized( self, opt_level=-1, cmp_level=0 ):
      if opt_level == -1: self.prv_level = -1
      else:
         self.prv_level = self.opt_level
         self.set_opt_level(opt_level)
      self.cmp_level = cmp_level
      return self

   def __enter__(self):
      if self.updating == 0:
         if self.prv_level == -2: self.optimized(0,0)
         self.quads.__enter__()
      self.updating += 1
      return self

   def __exit__(self,exc_type,exc_value,traceback): 
      self.updating -= 1
      if self.updating == 0:
         self.compact(self.cmp_level)
         self.optimize()
         if self.prv_level != -1: self.set_opt_level(self.prv_level)
         self.prv_level = -2
         self.quads.__exit__(exc_type,exc_value,traceback)

   def add(self,p2s,i,j,k,c,p2i=0,p2j=0,p2k=0):
      si,ii = (0, i) if i >= 0 else (1,-1-i)
      sj,ij = (0, j) if j >= 0 else (1,-1-j)
      sk,ik = (0,-k) if k <= 0 else (1, k-1)
      idx = ijk1b_to_idx0_7(si,sj,sk)
      key = (c,p2s,p2i,p2j,p2k)
      self.cuboids[idx][key].add( ii>>(p2s+p2i), ij>>(p2s+p2j), ik>>(p2s+p2k) )

      if   self.opt_level == 0: VoxelModel.add(self,p2s,i,j,k,c,p2i,p2j,p2k)
      elif self.opt_level == 1: self.added[idx][key].add( ii>>(p2s+p2i), ij>>(p2s+p2j), ik>>(p2s+p2k) )

   def sub(self,p2s,i,j,k,p2i=0,p2j=0,p2k=0):
      si,ii = (0, i) if i >= 0 else (1,-1-i)
      sj,ij = (0, j) if j >= 0 else (1,-1-j)
      sk,ik = (0,-k) if k <= 0 else (1, k-1)
      idx = ijk1b_to_idx0_7(si,sj,sk)

      while True:
         split_rqrd = False
         for key,cs in self.cuboids[idx].items():
            if cs.sub( ii>>(key[1]+key[2]), ij>>(key[1]+key[3]), ik>>(key[1]+key[4]) ):
               if key[1]+key[2] <= p2s+p2i and key[1]+key[3] <= p2s+p2j and key[1]+key[4] <= p2s+p2k:
                  if   self.opt_level == 0 or self.opt_level == 1: # todo: for level 1 keep list and process in optimize() call
                     key1 = self.get(i-1,j,k)
                     if key1 is None: cim = key[0]
                     else:
                        if key1[1]+key1[3] >= p2s+p2j and key1[1]+key1[4] >= p2s+p2k: cim = key1[0]
                        else:
                           # cs.add( ii>>(key[1]+key[2]), ij>>(key[1]+key[3]), ik>>(key[1]+key[4]) )
                           # split
                           cim = key1[0]
                           pass
                     cim  = key[0] if key1 is None else key1[0]
                     key1 = self.get(i+1,j,k)
                     cip  = key[0] if key1 is None else key1[0]
                     key1 = self.get(i,j-1,k)
                     cjm  = key[0] if key1 is None else key1[0]
                     key1 = self.get(i,j+1,k)
                     cjp  = key[0] if key1 is None else key1[0]
                     key1 = self.get(i,j,k-1)
                     ckm  = key[0] if key1 is None else key1[0]
                     key1 = self.get(i,j,k+1)
                     ckp  = key[0] if key1 is None else key1[0]

                     di = 1<<key[2]
                     dj = 1<<key[3]
                     dk = 1<<key[4]
                     self.quads.add( 1<<key[1],i,j,k,
                        ( ( (  0,  0,  0,  0, dj,-dk ), cim ),
                          ( ( di,  0,-dk, di, dj,  0 ), cip ),
                          ( (  0,  0,  0, di,  0,-dk ), cjm ),
                          ( (  0, dj,-dk, di, dj,  0 ), cjp ),
                          ( (  0, dj,  0, di,  0,  0 ), ckm ),
                          ( (  0,  0,-dk, di, dj,-dk ), ckp ) ) )
                  if key[1]+key[2] == p2s+p2i and key[1]+key[3] == p2s+p2j and key[1]+key[4] == p2s+p2k: break
               else:
                  split_rqrd = True
                  break
         if split_rqrd:
            if   key[3]-p2j <= key[2]-p2i >= key[4]-p2k:
               if key[2] == key[3] == key[4]: key1 = (key[0],key[1]-1,key[2]  ,key[3]+1,key[4]+1)
               else                         : key1 = (key[0],key[1]  ,key[2]-1,key[3]  ,key[4]  )
               pi = ii>>(key1[1]+key1[2])
               pj = ij>>(key1[1]+key1[3])
               pk = ik>>(key1[1]+key1[4])
               self.cuboids[idx][key1].add(pi  ,pj,pk)
               self.cuboids[idx][key1].add(pi^1,pj,pk)
            elif key[2]-p2i <= key[3]-p2j >= key[4]-p2k:
               if key[2] == key[3] == key[4]: key1 = (key[0],key[1]-1,key[2]+1,key[3]  ,key[4]+1)
               else                         : key1 = (key[0],key[1]  ,key[2]  ,key[3]-1,key[4]  )
               pi = ii>>(key1[1]+key1[2])
               pj = ij>>(key1[1]+key1[3])
               pk = ik>>(key1[1]+key1[4])
               self.cuboids[idx][key1].add(pi,pj  ,pk)
               self.cuboids[idx][key1].add(pi,pj^1,pk)
            else:
               if key[2] == key[3] == key[4]: key1 = (key[0],key[1]-1,key[2]+1,key[3]+1,key[4]  )
               else                         : key1 = (key[0],key[1]  ,key[2]  ,key[3]  ,key[4]-1)
               pi = ii>>(key1[1]+key1[2])
               pj = ij>>(key1[1]+key1[3])
               pk = ik>>(key1[1]+key1[4])
               self.cuboids[idx][key1].add(pi,pj,pk  )
               self.cuboids[idx][key1].add(pi,pj,pk^1)
         else: break

   def get(self,i,j,k):
      si,ii = (0, i) if i >= 0 else (1,-1-i)
      sj,ij = (0, j) if j >= 0 else (1,-1-j)
      sk,ik = (0,-k) if k <= 0 else (1, k-1)
      for key,cs in self.cuboids[ijk1b_to_idx0_7(si,sj,sk)].items():
         if cs.get( ii>>(key[1]+key[2]), ij>>(key[1]+key[3]), ik>>(key[1]+key[4]) ): return key
      else: return None

   def compact( self, level ):
      if   self.opt_level == 0: return
      elif self.opt_level == 1: cuboids = self.added
      else                    : cuboids = self.cuboids
      planes = [1,2,0]
      lines  = [0,2,1]
      for cs2 in cuboids:
         min_p2s = 0
         while True:
            added = []
            for key1,cs1 in cs2.items():
               if key1[1] < min_p2s: continue
               c,p2s,p2i,p2j,p2k = key1
               if level >= 1:
                  if p2i <= p2j >= p2k:
                     planes[0] = 1
                     if p2k >= p2i:
                        planes[1] = 2
                        planes[2] = 0
                     else:
                        planes[1] = 0
                        planes[2] = 2
                  elif p2i <= p2k >= p2j:
                     planes[0] = 2
                     if p2j >= p2i:
                        planes[1] = 1
                        planes[2] = 0
                     else:
                        planes[1] = 0
                        planes[2] = 1
                  else:
                     planes[0] = 0
                     if p2j >= p2k:
                        planes[1] = 1
                        planes[2] = 2
                     else:
                        planes[1] = 2
                        planes[2] = 1
               if level >= 2:
                  if p2j >= p2i <= p2k:
                     lines[0] = 0
                     if p2k <= p2j:
                        lines[1] = 2
                        lines[2] = 1
                     else:
                        lines[1] = 1
                        lines[2] = 2
                  elif p2i >= p2k <= p2j:
                     lines[0] = 2
                     if p2i <= p2j:
                        lines[1] = 0
                        lines[2] = 1
                     else:
                        lines[1] = 1
                        lines[2] = 0
                  else:
                     lines[0] = 1
                     if p2i <= p2k:
                        lines[1] = 0
                        lines[2] = 2
                     else:
                        lines[1] = 2
                        lines[2] = 0
               for ijk,cs in cs1.items():
                  for idx,mask in enumerate(cs):
                     if not mask: continue
                     i,j,k = idx0_63_to_ijk2b(idx)
                     i = ijk[0]+(i<<2)
                     j = ijk[1]+(j<<2)
                     k = ijk[2]+(k<<2)
                     for t in mask_to_2x2x2:
                        if mask&t[0] == t[0]:
                           added.append(( (c,p2s+1,p2i,p2j,p2k), (i+t[1])>>1, (j+t[2])>>1, (k+t[3])>>1 ))
                           mask &= ~t[0]
                     if not mask:
                        cs[idx] = mask
                        continue
                     if level >= 1:
                        for p in planes:
                           if   p == 0:
                              for t in mask_to_1x2x2:
                                 if mask&t[0] == t[0]:
                                    added.append(( (c,p2s,p2i,p2j+1,p2k+1), i+t[1], (j+t[2])>>1, (k+t[3])>>1 ))
                                    mask &= ~t[0]
                           elif p == 1:
                              for t in mask_to_2x1x2:
                                 if mask&t[0] == t[0]:
                                    added.append(( (c,p2s,p2i+1,p2j,p2k+1), (i+t[1])>>1, j+t[2], (k+t[3])>>1 ))
                                    mask &= ~t[0]
                           else:
                              for t in mask_to_2x2x1:
                                 if mask&t[0] == t[0]:
                                    added.append(( (c,p2s,p2i+1,p2j+1,p2k), (i+t[1])>>1, (j+t[2])>>1, k+t[3] ))
                                    mask &= ~t[0]
                        if not mask:
                           cs[idx] = mask
                           continue
                     if level >= 3:
                        for p in planes:
                           if   p == 0:
                              for t in mask_to_j2_k2:
                                 if mask&t[0] == t[0]:
                                    added.append(( (c,p2s,p2i,p2j+1,p2k), i+t[1], (j+t[2])>>1, k+t[3] ))
                                    added.append(( (c,p2s,p2i,p2j,p2k+1), i+t[4], j+t[5], (k+t[6])>>1 ))
                                    mask &= ~t[0]
                           elif p == 1:
                              for t in mask_to_i2_k2:
                                 if mask&t[0] == t[0]:
                                    added.append(( (c,p2s,p2i+1,p2j,p2k), (i+t[1])>>1, j+t[2], k+t[3] ))
                                    added.append(( (c,p2s,p2i,p2j,p2k+1), i+t[4], j+t[5], (k+t[6])>>1 ))
                                    mask &= ~t[0]
                           else:
                              for t in mask_to_i2_j2:
                                 if mask&t[0] == t[0]:
                                    added.append(( (c,p2s,p2i+1,p2j,p2k), (i+t[1])>>1, j+t[2], k+t[3] ))
                                    added.append(( (c,p2s,p2i,p2j+1,p2k), i+t[4], (j+t[5])>>1, k+t[6] ))
                                    mask &= ~t[0]
                        if not mask:
                           cs[idx] = mask
                           continue
                     if level >= 2:
                        for l in lines:
                           if   l == 0:
                              for t in mask_to_2x1x1:
                                 if mask&t[0] == t[0]:
                                    added.append(( (c,p2s,p2i+1,p2j,p2k), (i+t[1])>>1, j+t[2], k+t[3] ))
                                    mask &= ~t[0]
                           elif l == 1:
                              for t in mask_to_1x2x1:
                                 if mask&t[0] == t[0]:
                                    added.append(( (c,p2s,p2i,p2j+1,p2k), i+t[1], (j+t[2])>>1, k+t[3] ))
                                    mask &= ~t[0]
                           else:
                              for t in mask_to_1x1x2:
                                 if mask&t[0] == t[0]:
                                    added.append(( (c,p2s,p2i,p2j,p2k+1), i+t[1], j+t[2], (k+t[3])>>1 ))
                                    mask &= ~t[0]
                     cs[idx] = mask
            if added:
               min_p2s = 127
               for v in added:
                  cs2[v[0]].add(v[1],v[2],v[3])
                  if v[0][1] < min_p2s: min_p2s = v[0][1]
               continue
            else: break
         empty = []
         for key1,cs1 in cs2.items():
            if cs1.compact(): empty.append(key1)
         for key1 in empty: del cs2[key1]

   def optimize(self):
      if self.opt_level == 0: return
      with self.quads:
         if   self.opt_level == 1: cuboids = self.added
         elif self.opt_level == 2:
            self.quads.reset()
            cuboids = self.cuboids
         else: assert( 0 <= self.opt_level <= 2 )
         cnt = 0
         for idx2,cs2 in enumerate(cuboids):
            fi,fj,fk = idx0_7_to_ijk1b(idx2)
            si =  1-fi-fi
            sj =  1-fj-fj
            sk = -1+fk+fk
            for key1,cs1 in ( cs2.items() if self.opt_level == 1 else sorted( cs2.items(), key=lambda k: k[0][1]+max(k[0][2],k[0][3],k[0][4]), reverse=True ) ):
               c  =    key1[0]
               s  = 1<<key1[1]
               di = 1<<key1[2]
               dj = 1<<key1[3]
               dk = 1<<key1[4]
               ai = si*di
               aj = sj*dj
               ak = sk*dk
               for ijk,cs in cs1.items():
                  ii = ijk[0]+fi
                  ij = ijk[1]+fj
                  ik = ijk[2]+fk
                  for idx,mask in enumerate(cs):
                     if not mask: continue
                     i,j,k = idx0_63_to_ijk2b(idx)
                     i = ii+(i<<2)
                     j = ij+(j<<2)
                     k = ik+(k<<2)
                     m = 1
                     for idx1 in range(64):
                        if mask&m:
                           ijk1 = idx0_63_to_ijk2b(idx1)
                           self.quads.add( s,ai*(i+ijk1[0]),aj*(j+ijk1[1]),ak*(k+ijk1[2]),
                              ( ( ( 0,  0,  0, di, dj,  0 ), c ),
                                ( ( 0,  0,-dk,  0, dj,  0 ), c ),
                                ( ( di, 0,  0, di, dj,-dk ), c ),
                                ( ( 0,  0,-dk, di,  0,  0 ), c ),
                                ( ( 0, dj,-dk, di,  0,-dk ), c ),
                                ( ( 0, dj,  0, di, dj,-dk ), c ) ) )
                           cnt += 1
                        m += m
                     if self.opt_level == 1: cs[idx] = 0
         if self.opt_level == 2: print(cnt)
