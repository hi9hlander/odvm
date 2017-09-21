class square:
   def __init__(self,a0,b0,a1,b1,c,cover=None):
      if a0 < a1:
         self.a0 = a0
         self.a1 = a1
      else:      
         self.a0 = a1
         self.a1 = a0
      if b0 < b1:
         self.b0 = b0
         self.b1 = b1
      else:
         self.b0 = b1
         self.b1 = b0
      self.c = c
      
      x = int(c); x = x+x if x >= 0 else -1-x-x
      self.ft = x

      self.cover = cover

   def __eq__(self,other): return self.a0 < other.a1 and self.a1 > other.a0 and self.b0 < other.b1 and self.b1 > other.b0 and self.c == other.c

   def __hash__(self): return self.ft


def same_corners(s1,s2,v1,v2):
      if s1+s2 != v1+v2: return False
      ds = s1-s2
      dv = v1-v2
      return abs(ds[0]) == abs(dv[0]) and abs(ds[1]) == abs(dv[1]) and abs(ds[2]) == abs(dv[2])


class grid:
   def __init__(self,da=32.0,db=32.0,na=8,nb=8,ca=0.0,cb=0.0):
      if na&1 == 1: na += 1
      if nb&1 == 1: nb += 1
      self.grid = tuple( tuple( {} for j in range(nb) ) for i in range(na) )

      self.a2i = 1.0/da
      self.di0 = 0.5*na-(ca-0.125)/da
      self.di1 = 0.5*na-(ca+0.125)/da+1.0
      self.b2j = 1.0/db
      self.dj0 = 0.5*nb-(cb-0.125)/db
      self.dj1 = 0.5*nb-(cb+0.125)/db+1.0

      self.i1 = na
      self.j1 = nb
      self.a0 = ca-(0.5*na)*da
      self.b0 = cb-(0.5*nb)*db
      self.a1 = ca+(0.5*na)*da
      self.b1 = cb+(0.5*nb)*db

   def set(self,a0,b0,a1,b1,c,cover):
      sqr = square(a0,b0,a1,b1,c,cover)
      i0  = int( sqr.a0*self.a2i+self.di0 ) if self.a0 < sqr.a0 < self.a1 else ( 0 if sqr.a0 <= self.a0 else self.i1-1 )
      i1  = int( sqr.a1*self.a2i+self.di1 ) if self.a0 < sqr.a1 < self.a1 else ( 1 if sqr.a1 <= self.a0 else self.i1   )
      j0  = int( sqr.b0*self.b2j+self.dj0 ) if self.b0 < sqr.b0 < self.b1 else ( 0 if sqr.b0 <= self.b0 else self.j1-1 )
      j1  = int( sqr.b1*self.b2j+self.dj1 ) if self.b0 < sqr.b1 < self.b1 else ( 1 if sqr.b1 <= self.b0 else self.j1   )
      for clmn in self.grid[i0:i1]:
         for cell in clmn[j0:j1]: cell[sqr] = sqr

   def pop1(self,a0,b0,a1,b1,c):
      sqr = square(a0,b0,a1,b1,c)
      i0  = int( sqr.a0*self.a2i+self.di0 ) if self.a0 < sqr.a0 < self.a1 else ( 0 if sqr.a0 <= self.a0 else self.i1-1 )
      i1  = int( sqr.a1*self.a2i+self.di1 ) if self.a0 < sqr.a1 < self.a1 else ( 1 if sqr.a1 <= self.a0 else self.i1   )
      j0  = int( sqr.b0*self.b2j+self.dj0 ) if self.b0 < sqr.b0 < self.b1 else ( 0 if sqr.b0 <= self.b0 else self.j1-1 )
      j1  = int( sqr.b1*self.b2j+self.dj1 ) if self.b0 < sqr.b1 < self.b1 else ( 1 if sqr.b1 <= self.b0 else self.j1   )
      for clmn in self.grid[i0:i1]:
         for cell in clmn[j0:j1]:
            sqr = cell.pop(sqr,sqr)
            if sqr.cover is not None:
               self.cell1 = cell
               self.clmn1 = clmn
               return sqr
      return None

   def popR(self,sqr):
      i0  = int( sqr.a0*self.a2i+self.di0 ) if self.a0 < sqr.a0 < self.a1 else ( 0 if sqr.a0 <= self.a0 else self.i1-1 )
      i1  = int( sqr.a1*self.a2i+self.di1 ) if self.a0 < sqr.a1 < self.a1 else ( 1 if sqr.a1 <= self.a0 else self.i1   )
      j0  = int( sqr.b0*self.b2j+self.dj0 ) if self.b0 < sqr.b0 < self.b1 else ( 0 if sqr.b0 <= self.b0 else self.j1-1 )
      j1  = int( sqr.b1*self.b2j+self.dj1 ) if self.b0 < sqr.b1 < self.b1 else ( 1 if sqr.b1 <= self.b0 else self.j1   )
      for clmn in self.grid[i0:i1]:
         if clmn is not self.clmn1:
            for cell in clmn[j0:j1]: cell.pop(sqr)
         else:
            for cell in clmn[j0:j1]:
               if cell is not self.cell1: cell.pop(sqr)

   def set1(self,sqr): self.cell1[sqr] = sqr

   def clear(self):
      self.cell1 = None
      self.clmn1 = None
      for clmn in self.grid:
         for cell in clmn: cell.clear()
