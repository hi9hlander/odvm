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

   def sub( self, i, j, k ):
      assert( 0 <= i <= 15 and 0 <= j <= 15 and 0 <= k <= 15 )
      idx  = ijk2b_to_idx0_63(i>>2,j>>2,k>>2)
      mask = 1<<ijk2b_to_idx0_63(i&3,j&3,k&3)
      if self[idx] & mask == 0: return False
      else:
         self[idx] &= ~mask
         return True

   def get( self, i, j, k ):
      assert( 0 <= i <= 15 and 0 <= j <= 15 and 0 <= k <= 15 )
      return self[ijk2b_to_idx0_63(i>>2,j>>2,k>>2)] & (1<<ijk2b_to_idx0_63(i&3,j&3,k&3)) != 0


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

   def sub( self, i, j, k ):
      idx = ijk2b_to_idx0_63(i>>self.bits,j>>self.bits,k>>self.bits)
      if self[idx] is None: return False
      else:
         mask = (1<<self.bits)-1
         return self[idx].sub( i&mask, j&mask, k&mask )

   def get( self, i, j, k ):
      idx = ijk2b_to_idx0_63(i>>self.bits,j>>self.bits,k>>self.bits)
      if self[idx] is None: return False
      else:
         mask = (1<<self.bits)-1
         return self[idx].get( i&mask, j&mask, k&mask )

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
