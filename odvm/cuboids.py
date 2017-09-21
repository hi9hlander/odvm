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


mask_to_2x2x2 = [(0,0,0,0)]*8
mask_to_1x2x2 = [(0,0,0,0)]*16
mask_to_2x1x2 = [(0,0,0,0)]*16
mask_to_2x2x1 = [(0,0,0,0)]*16
mask_to_2x1x1 = [(0,0,0,0)]*32
mask_to_1x2x1 = [(0,0,0,0)]*32
mask_to_1x1x2 = [(0,0,0,0)]*32
mask_to_i2_j2 = [(0,0,0,0,0,0,0)]*64
mask_to_i2_k2 = [(0,0,0,0,0,0,0)]*64
mask_to_j2_k2 = [(0,0,0,0,0,0,0)]*64

def calc_mask_to_xxxxx():
   idx0 = 0   
   idx1 = 0   
   idx2 = 0   
   idx3 = 0   
   for k in (0,2):
      for j in (0,2):
         for i in (0,2):
            m000 = 1<<ijk2b_to_idx0_63( i  , j  , k   )
            m010 = 1<<ijk2b_to_idx0_63( i  , j+1, k   )
            m001 = 1<<ijk2b_to_idx0_63( i  , j  , k+1 )
            m011 = 1<<ijk2b_to_idx0_63( i  , j+1, k+1 )
            m100 = 1<<ijk2b_to_idx0_63( i+1, j  , k   )
            m110 = 1<<ijk2b_to_idx0_63( i+1, j+1, k   )
            m101 = 1<<ijk2b_to_idx0_63( i+1, j  , k+1 )
            m111 = 1<<ijk2b_to_idx0_63( i+1, j+1, k+1  )
            mask_to_2x2x2[idx0] = (m000|m010|m001|m011|m100|m110|m101|m111,i,j,k)
            idx0 += 1
            mask_to_1x2x2[idx1+0] = (m000|m010|m001|m011,i  ,j  ,k  )
            mask_to_1x2x2[idx1+1] = (m100|m110|m101|m111,i+1,j  ,k  )

            mask_to_2x1x2[idx1+0] = (m000|m100|m001|m101,i  ,j  ,k  )
            mask_to_2x1x2[idx1+1] = (m010|m110|m011|m111,i  ,j+1,k  )

            mask_to_2x2x1[idx1+0] = (m000|m100|m010|m110,i  ,j  ,k  )
            mask_to_2x2x1[idx1+1] = (m001|m101|m011|m111,i  ,j  ,k+1)
            idx1 += 2
            mask_to_2x1x1[idx2+0] = (m000|m100,i  ,j  ,k  )
            mask_to_2x1x1[idx2+1] = (m010|m110,i  ,j+1,k  )
            mask_to_2x1x1[idx2+2] = (m001|m101,i  ,j  ,k+1)
            mask_to_2x1x1[idx2+3] = (m011|m111,i  ,j+1,k+1)

            mask_to_1x2x1[idx2+0] = (m000|m010,i  ,j  ,k  )
            mask_to_1x2x1[idx2+1] = (m100|m110,i+1,j  ,k  )
            mask_to_1x2x1[idx2+2] = (m001|m011,i  ,j  ,k+1)
            mask_to_1x2x1[idx2+3] = (m101|m111,i+1,j  ,k+1)

            mask_to_1x1x2[idx2+0] = (m000|m001,i  ,j  ,k  )
            mask_to_1x1x2[idx2+1] = (m100|m101,i+1,j  ,k  )
            mask_to_1x1x2[idx2+2] = (m010|m011,i  ,j+1,k  )
            mask_to_1x1x2[idx2+3] = (m110|m111,i+1,j+1,k  )
            idx2 += 4
            mask_to_i2_j2[idx3+0] = (m000|m100|m001|m011,i  ,j  ,k  ,i  ,j  ,k+1)
            mask_to_i2_j2[idx3+1] = (m000|m100|m101|m111,i  ,j  ,k  ,i+1,j  ,k+1)
            mask_to_i2_j2[idx3+2] = (m010|m110|m001|m011,i  ,j+1,k  ,i  ,j  ,k+1)
            mask_to_i2_j2[idx3+3] = (m010|m110|m101|m111,i  ,j+1,k  ,i+1,j  ,k+1)
            mask_to_i2_j2[idx3+4] = (m001|m101|m000|m010,i  ,j  ,k+1,i  ,j  ,k  )
            mask_to_i2_j2[idx3+5] = (m001|m101|m100|m110,i  ,j  ,k+1,i+1,j  ,k  )
            mask_to_i2_j2[idx3+6] = (m011|m111|m000|m010,i  ,j+1,k+1,i  ,j  ,k  )
            mask_to_i2_j2[idx3+7] = (m011|m111|m100|m110,i  ,j+1,k+1,i+1,j  ,k  )

            mask_to_i2_k2[idx3+0] = (m000|m100|m010|m011,i  ,j  ,k  ,i  ,j+1,k  )
            mask_to_i2_k2[idx3+1] = (m000|m100|m110|m111,i  ,j  ,k  ,i+1,j+1,k  )
            mask_to_i2_k2[idx3+2] = (m010|m110|m000|m001,i  ,j+1,k  ,i  ,j  ,k  )
            mask_to_i2_k2[idx3+3] = (m010|m110|m100|m101,i  ,j+1,k  ,i+1,j  ,k  )
            mask_to_i2_k2[idx3+4] = (m001|m101|m010|m011,i  ,j  ,k+1,i  ,j+1,k  )
            mask_to_i2_k2[idx3+5] = (m001|m101|m110|m111,i  ,j  ,k+1,i+1,j+1,k  )
            mask_to_i2_k2[idx3+6] = (m011|m111|m000|m001,i  ,j+1,k+1,i  ,j  ,k  )
            mask_to_i2_k2[idx3+7] = (m011|m111|m100|m101,i  ,j+1,k+1,i+1,j  ,k  )

            mask_to_j2_k2[idx3+0] = (m000|m010|m100|m101,i  ,j  ,k  ,i+1,j  ,k  )
            mask_to_j2_k2[idx3+1] = (m000|m010|m110|m111,i  ,j  ,k  ,i+1,j+1,k  )
            mask_to_j2_k2[idx3+2] = (m100|m110|m000|m001,i+1,j  ,k  ,i  ,j  ,k  )
            mask_to_j2_k2[idx3+3] = (m100|m110|m010|m011,i+1,j  ,k  ,i  ,j+1,k  )
            mask_to_j2_k2[idx3+4] = (m000|m011|m100|m101,i  ,j  ,k+1,i+1,j  ,k  )
            mask_to_j2_k2[idx3+5] = (m000|m011|m110|m111,i  ,j  ,k+1,i+1,j+1,k  )
            mask_to_j2_k2[idx3+6] = (m101|m111|m000|m001,i+1,j  ,k+1,i  ,j  ,k  )
            mask_to_j2_k2[idx3+7] = (m101|m111|m010|m011,i+1,j  ,k+1,i  ,j+1,k  )
            idx3 += 8

calc_mask_to_xxxxx()


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

   def compact(self):
      empty = 0
      if self.bits == 4:
         for idx,cs in enumerate(self):
            if cs is not None:
               if not any(mask for mask in cs): self[idx] = cs = None
            if cs is None: empty += 1
      else:
         for idx,cs in enumerate(self):
            if cs is not None:
               if cs.compact(): self[idx] = cs = None
            if cs is None: empty += 1
      return empty == len(self)


   def items(self):
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
