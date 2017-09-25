from panda3d.core import Vec3
from odvm.edges import edge, edges
from odvm.grid import square, grid, same_corners
from odvm.groupby import GroupByNormal


def slice_by_sqr(v0,v1,v2,v3,i1,i2):
   if   abs(v1[0]-v2[0]) <= abs(v1[1]-v2[1]) >= abs(v1[2]-v2[2]): a = 1
   elif abs(v1[0]-v2[0]) <= abs(v1[2]-v2[2]) >= abs(v1[0]-v2[0]): a = 2
   else                                                         : a = 0
   m  = (v1+v2)*0.5
   d1 = abs(i1[a]-m[a])
   d2 = abs(i2[a]-m[a])
   ia = -1
   if d1 <= d2:
      if d1+d1 >= abs(v1[a]-v2[a]): ia = a
      else                        : p  = i1[a]
   else:
      if d2+d2 >= abs(v1[a]-v2[a]): ia = a
      else                        : p  = i2[a]
   if ia != -1:
      if   ia != 1 and v1[1] != v2[1]: a = 1
      elif ia != 2 and v1[2] != v2[2]: a = 2
      else                           : a = 0
      if abs(i1[a]-m[a]) <= abs(i2[a]-m[a]): p = i1[a]
      else                                 : p = i2[a]
   if v0[a] == v1[a]:
      c2    = Vec3(v2)
      c3    = Vec3(v3)
      c2[a] = p
      c3[a] = p
      if abs(i2[a]-i1[a])+abs(p-v0[a]) <= abs((i2[a]-p)+(i1[a]-v0[a])): return ( (v0,v1,c2,c3), (c2,c3,v2,v3) )
      else                                                            : return ( (c2,c3,v2,v3), (v0,v1,c2,c3) )
   else:
      c1    = Vec3(v1)
      c3    = Vec3(v3)
      c1[a] = p
      c3[a] = p
      if abs(i2[a]-i1[a])+abs(p-v0[a]) <= abs((i2[a]-p)+(i1[a]-v0[a])): return ( (v0,c1,v2,c3), (c1,v1,c3,v3) )
      else                                                            : return ( (c1,v1,c3,v3), (v0,c1,v2,c3) )


class quad:
   def __init__(self,v0,v1,v2,v3,colour):
      self.diag12 = (v1,v2)
      self.diag03 = (v0,v3)
      self.colour = colour

   def match(self,v1,v2): return same_corners(self.diag12[0],self.diag12[1],v1,v2)

   def attach(self,quads):
      x0,y0,z0 = self.diag12[0]
      x1,y1,z1 = self.diag12[1]
      if   y0 == y1: normal = Vec3(0.0,(1.0 if (x0-x1)*(z1-z0) >= 0.0 else -1.0),0.0) # == -ux*vz, u=(x1-x0,0,z1-z0), v=(0,0,z1-z0)
      elif x0 == x1: normal = Vec3((1.0 if (z0-z1)*(y1-y0) >= 0.0 else -1.0),0.0,0.0) # == -uz*vy, u=(0,y1-y0,z1-z0), v=(0,y1-y0,0)
      else         : normal = Vec3(0.0,0.0,(1.0 if (x1-x0)*(y1-y0) >= 0.0 else -1.0)) # ==  ux*vy, u=(x1-x0,y1-y0,0), v=(0,y1-y0,0)
      self.quads = quads
      self.geom  = quads.planes[normal]
      self.rect  = ( [self.diag03[0],self.diag12[0],self.quads.add_edge(self.diag03[0],self.diag12[0],self)],  # v0 -> v1 : left
                     [self.diag12[0],self.diag03[1],self.quads.add_edge(self.diag12[0],self.diag03[1],self)],  # v1 -> v3 : bottom
                     [self.diag03[1],self.diag12[1],self.quads.add_edge(self.diag03[1],self.diag12[1],self)],  # v3 -> v2 : right
                     [self.diag12[1],self.diag03[0],self.quads.add_edge(self.diag12[1],self.diag03[0],self)] ) # v2 -> v0 : top
      self.geom.update_q.add(self)
      self.geom.faces.add(self)

   def detach(self):
      if hasattr(self,'edges'):
         del self.edges
         del self.points
      if hasattr(self,'vertices'):
         self.geom.unused_v.extend(self.vertices )
         self.geom.unused_t.extend(self.triangles)
         del self.vertices
         del self.triangles
      if self.quads is not None:
         for e in self.rect: self.quads.sub_edge(e[0],e[1],e[2],self)
         del self.rect
         self.geom.faces.discard(self)
         self.geom.update_q.discard(self)
         self.geom  = None
         self.quads = None

   def update(self): self.geom.update_q.add(self)

   def change_edge(self,f,t):
      for e in self.rect:
         if e[2] is f: e[2] = t

   def query_edges(self):
      if not hasattr(self,'edges'):
         self.edges  = ( [], [], [], [] )
         self.points = ( [], [], [], [] )
      build_rqrd = False
      for i,e in enumerate(self.rect):
         if   e[0][0] != e[1][0]: ps = e[2].query_points(e[0][0],e[1][0])
         elif e[0][1] != e[1][1]: ps = e[2].query_points(e[0][1],e[1][1])
         else                   : ps = e[2].query_points(e[0][2],e[1][2])

         if not self.edges[i] or self.points[i] != ps:
            self.points[i][:] = ps
            build_rqrd = True

            del self.edges[i][:]
            self.edges[i].append(e[0])
            if   e[0][0] != e[1][0]:
               pp = e[0][0]
               for p in ps:
                  if p != pp:
                     self.edges[i].append(Vec3(p,e[0][1],e[0][2]))
                     pp = p
            elif e[0][1] != e[1][1]:
               pp = e[0][1]
               for p in ps:
                  if p != pp:
                     self.edges[i].append(Vec3(e[0][0],p,e[0][2]))
                     pp = p
            else:
               pp = e[0][2]
               for p in ps:
                  if p != pp:
                     self.edges[i].append(Vec3(e[0][0],e[0][1],p))
                     pp = p
            self.edges[i].append(e[1])
      return build_rqrd

   def add_triangle(self,e0,k0,e1,k1,e2,k2):
      i0 = self.imap[e0][k0]
      if i0 < 0:
         i0 = self.geom.add_vertex(self.edges[e0][k0],self.colour)
         self.imap[e0][k0] = i0
      i1 = self.imap[e1][k1]
      if i1 < 0:
         i1 = self.geom.add_vertex(self.edges[e1][k1],self.colour)
         self.imap[e1][k1] = i1
      i2 = self.imap[e2][k2]
      if i2 < 0:
         i2 = self.geom.add_vertex(self.edges[e2][k2],self.colour)
         self.imap[e2][k2] = i2
      if e0 != e1 or k1 > k0: self.geom.add_triangle(i0,i1,i2)
      else                  : self.geom.add_triangle(i1,i0,i2)

   def build(self):
      if not self.query_edges(): return

      assert( not self.geom.used_v )
      assert( not self.geom.used_t )

      if hasattr(self,'vertices'):
         self.geom.unused_v.extend(self.vertices )
         self.geom.unused_t.extend(self.triangles)
      else:
         self.vertices  = []
         self.triangles = []

      lsts      = ( len(self.edges[0])-1, len(self.edges[1])-1, len(self.edges[2])-1, len(self.edges[3])-1 )
      idxs      = ( [ 0, lsts[0], 0x7f ], [ 0, lsts[1], 0x7f ], [ 0, lsts[2], 0x7f ], [ 0, lsts[3], 0x7f ] )
      attach    = ( -1, 0, 0, 1, -1, -1, 1 )
      self.imap = ( [-1]*len(self.edges[0]), [-2]*len(self.edges[1]), [-3]*len(self.edges[2]), [-4]*len(self.edges[3]) )
      self.imap[0][ 0] = self.imap[3][-1] = self.geom.add_vertex(self.edges[0][0],self.colour)
      self.imap[0][-1] = self.imap[1][ 0] = self.geom.add_vertex(self.edges[1][0],self.colour)
      self.imap[2][-1] = self.imap[3][ 0] = self.geom.add_vertex(self.edges[3][0],self.colour)
      self.imap[1][-1] = self.imap[2][ 0] = self.geom.add_vertex(self.edges[2][0],self.colour)

      while True:
         sel = ( 1e9, )
         for e0 in range(4):
            if idxs[e0][2] and idxs[e0][0] != idxs[e0][1]:
               for e in (3,1,2,6):
                  if idxs[e0][2]&(1<<e) != 0:
                     if e&3 == 2: # opposite
                        ea = (e0+(3 if e == 6 else 1))&3
                        if idxs[ea][0] != idxs[ea][1] or idxs[ea][0] == idxs[ea][1] and 0 < idxs[ea][0] < lsts[ea] and idxs[ea][2]&((1<<1)|(1<<3)) == ((1<<1)|(1<<3)): continue
                     e2 = (e0+e)&3
                     j2 = attach[e]
                     j0 = j2^1
                     k0 = idxs[e0][j0]
                     k2 = idxs[e2][j2]
                     dk = 1-j0-j0 # +1 or -1
                     k1 = k0+dk
                     if e&3 == 2 and ( k2 == 0 and k1 == lsts[e0] or k2 == lsts[e2] and k1 == 0 ): continue # opposite, corner to corner
                     if self.imap[e0][k0] == self.imap[e2][k2]: # contains corner
                        if k2 == idxs[e2][j0]: continue
                        k2 -= dk
                     d  = max( (self.edges[e2][k2]-self.edges[e0][k0]).length_squared(), (self.edges[e2][k2]-self.edges[e0][k1]).length_squared() )
                     # v01  = self.edges[e0][k1]-self.edges[e0][k0]
                     # v02  = self.edges[e2][k2]-self.edges[e0][k0]
                     # v12  = self.edges[e2][k2]-self.edges[e0][k1]
                     # lenc = max(v02.length_squared(),v12.length_squared())
                     # v01.normalize()
                     # v02.normalize()
                     # v12.normalize()
                     # d102 = abs(v01.dot(v02))
                     # d120 = abs(v02.dot(v12))
                     # d210 = abs(v12.dot(-v01))
                     # # d = min( max(d102,d120)/v02.length(), max(d210,d120)/v12.length() ) 
                     # # d = max(d102,d120,d210)
                     # d = max(d102,d120,d210)*lenc
                     if d < sel[0]: sel = (d,e0,j0,k0,k1,e2,j2,k2,e)
         if len(sel) == 1:
            for e0 in range(4):
               if idxs[e0][0] == idxs[e0][1] and 0 < idxs[e0][0] < lsts[e0] and idxs[e0][2]&((1<<1)|(1<<3)) == ((1<<1)|(1<<3)):
                  e1 = (e0+1)&3
                  e2 = (e0+3)&3
                  if idxs[e1][0] == idxs[e1][1] and idxs[e1][2]&(1<<3) != 0 and idxs[e2][0] == idxs[e2][1] and idxs[e2][2]&(1<<1) != 0: break
            else: break
            idxs[e0][2]  = 0
            idxs[e1][2] &= ~(1<<3)
            idxs[e2][2] &= ~(1<<1)
            self.add_triangle(e0,idxs[e0][0],e1,idxs[e1][0],e2,idxs[e2][0])
            continue
         d,e0,j0,k0,k1,e2,j2,k2,e = sel
         self.add_triangle(e0,k0,e0,k1,e2,k2)
         idxs[e0][j0] = k1
         idxs[e2][j2] = k2
         if   e == 6: # from left to opposite left
            idxs[(e0+1)&3][2] &= ~((1<<2)|(1<<6))        # right   : disable opposite
            idxs[ e0     ][2] &= ~(1<<3)                 # current : disable left
            idxs[(e0+3)&3][2] &= ~((1<<2)|(1<<6)|(1<<1)) # left    : disable opposite and right
            idxs[ e2     ][2] &= ~(1<<1)                 # opposite: disable right
         elif e == 2: # from right to opposite right
            idxs[(e0+3)&3][2] &= ~((1<<2)|(1<<6))        # left    : disable opposite
            idxs[ e0     ][2] &= ~(1<<1)                 # current : disable right
            idxs[(e0+1)&3][2] &= ~((1<<2)|(1<<6)|(1<<3)) # right   : disable opposite and left
            idxs[ e2     ][2] &= ~(1<<3)                 # opposite: disable left

      del self.imap
      self.vertices    = self.geom.used_v
      self.triangles   = self.geom.used_t
      self.geom.used_v = []
      self.geom.used_t = []

   def change_triangles(self,imap):
      for i in range(len(self.triangles)): self.triangles[i] = imap.pop(self.triangles[i],self.triangles[i])


def point_shift(p,df,dt):
   if   df[0] != dt[0]: return Vec3(p[0]+(1.0 if dt[0] > df[0] else -1.0),p[1],p[2])
   elif df[1] != dt[1]: return Vec3(p[0],p[1]+(1.0 if dt[1] > df[1] else -1.0),p[2])
   else               : return Vec3(p[0],p[1],p[2]+(1.0 if dt[2] > df[2] else -1.0))


class quads:
   def __init__( self, planes ):
      self.planes    = planes
      self.plane_x   = grid()
      self.plane_y   = grid()
      self.plane_z   = grid()
      self.line_x    = edges()
      self.line_y    = edges()
      self.line_z    = edges()
      self.new_quads = set()
      self.updating  = 0

   def reset(self):
      self.new_quads.clear()
      self.line_z.clear()
      self.line_y.clear()
      self.line_x.clear()
      self.plane_z.clear()
      self.plane_y.clear()
      self.plane_x.clear()
      self.planes.reset()

   def __enter__(self):
      if self.updating == 0: 
         assert( not self.new_quads            )
         assert( not self.planes.is_updating() )
      self.updating += 1
      return self

   def __exit__(self,exc_type,exc_value,traceback): 
      self.updating -= 1
      if self.updating == 0:
         while self.new_quads: self.new_quads.pop().attach(self)
         self.planes.update()

   def add_sqr(self,quad):
      self.new_quads.add(quad)
      if   quad.diag12[0][0] == quad.diag12[1][0]: self.plane_x.set(quad.diag12[0][1],quad.diag12[0][2],quad.diag12[1][1],quad.diag12[1][2],quad.diag12[0][0],quad)
      elif quad.diag12[0][1] == quad.diag12[1][1]: self.plane_y.set(quad.diag12[0][0],quad.diag12[0][2],quad.diag12[1][0],quad.diag12[1][2],quad.diag12[0][1],quad)
      else                                       : self.plane_z.set(quad.diag12[0][0],quad.diag12[0][1],quad.diag12[1][0],quad.diag12[1][1],quad.diag12[0][2],quad)

   def sel_sqr(self,v1,v2):
      if   v1[0] == v2[0]:
         self.plane1 = self.plane_x
         return self.plane1.pop1(v1[1],v1[2],v2[1],v2[2],v1[0])
      elif v1[1] == v2[1]:
         self.plane1 = self.plane_y
         return self.plane1.pop1(v1[0],v1[2],v2[0],v2[2],v1[1])
      else:
         self.plane1 = self.plane_z
         return self.plane1.pop1(v1[0],v1[1],v2[0],v2[1],v1[2])

   def sub_sqr(self,sqr):
      self.plane1.popR(sqr)
      try            : self.new_quads.remove(sqr.cover)
      except KeyError: sqr.cover.detach()

   def ret_sqr(self,sqr): self.plane1.set1(sqr)

   def add_edge(self,v0,v1,quad):
      if   v0[0] != v1[0]: return self.line_x.add(v0[0],v1[0],v0[1],v0[2],quad)
      elif v0[1] != v1[1]: return self.line_y.add(v0[1],v1[1],v0[0],v0[2],quad)
      else               : return self.line_z.add(v0[2],v1[2],v0[0],v0[1],quad)

   def sub_edge(self,v0,v1,e,quad):
      if   v0[0] != v1[0]: self.line_x.sub(v0[0],v1[0],e,quad)
      elif v0[1] != v1[1]: self.line_y.sub(v0[1],v1[1],e,quad)
      else               : self.line_z.sub(v0[2],v1[2],e,quad)

   def add_quad(self,v0,v1,v2,v3,colour):
      quad_rqrd = True
      s = self.sel_sqr(v1,v2)
      while s is not None:
         q = s.cover
         if q.match(v1,v2):
            if q.colour[3] == 1.0 and colour[3] == 1.0 or q.colour[3] < 1.0 and colour[3] < 1.0:
               self.sub_sqr(s)
               quad_rqrd = False
            elif colour[3] == 1.0:
               self.sub_sqr(s)
            else:
               self.ret_sqr(s)
               quad_rqrd = False
            break
         elif abs(q.diag12[0][0]-q.diag12[1][0]) < abs(v1[0]-v2[0]) or abs(q.diag12[0][1]-q.diag12[1][1]) < abs(v1[1]-v2[1]) or abs(q.diag12[0][2]-q.diag12[1][2]) < abs(v1[2]-v2[2]):
            qs = slice_by_sqr(v0,v1,v2,v3,q.diag12[0],q.diag12[1])
            if q.match(qs[1][1],qs[1][2]):
               self.sub_sqr(s) # need alpha processing
            else:
               self.ret_sqr(s)
               self.add_quad(qs[1][0],qs[1][1],qs[1][2],qs[1][3],colour)
            v0,v1,v2,v3 = qs[0]
         else:
            self.sub_sqr(s) # need alpha processing
            qs = slice_by_sqr(q.diag03[0],q.diag12[0],q.diag12[1],q.diag03[1],v1,v2)
            if not same_corners(qs[1][1],qs[1][2],v1,v2):
               self.add_sqr(quad(qs[1][0],qs[1][1],qs[1][2],qs[1][3],q.colour))
               self.add_quad(v0,v1,v2,v3,colour)
            v0,v1,v2,v3 = qs[0]
            colour      = q.colour
            break
         s = self.sel_sqr(v1,v2)
      if quad_rqrd:
         while True:
            lr_idx = 0 if (v1-v0).length_squared() >= (v2-v0).length_squared() else 1
            for idx in range(2):
               if idx == lr_idx:
                  s = self.sel_sqr(point_shift(v1,v3,v1),v0) # left
                  if s is not None:
                     q = s.cover
                     if q.diag12[1] == v0 and q.diag03[1] == v1 and q.colour == colour:
                        self.sub_sqr(s)
                        v0,v1 = q.diag03[0],q.diag12[0]
                        break
                     else: self.ret_sqr(s)
                  s = self.sel_sqr(v3,point_shift(v2,v0,v2)) # right
                  if s is not None:
                     q = s.cover
                     if q.diag03[0] == v2 and q.diag12[0] == v3 and q.colour == colour:
                        self.sub_sqr(s)
                        v2,v3 = q.diag12[1],q.diag03[1]
                        break
                     else: self.ret_sqr(s)
               else:
                  s = self.sel_sqr(point_shift(v1,v0,v1),v3) # top
                  if s is not None:
                     q = s.cover
                     if q.diag03[0] == v1 and q.diag12[1] == v3 and q.colour == colour:
                        self.sub_sqr(s)
                        v1,v3 = q.diag12[0],q.diag03[1]
                        break
                     else: self.ret_sqr(s)
                  s = self.sel_sqr(v0,point_shift(v2,v3,v2)) # bottom
                  if s is not None:
                     q = s.cover
                     if q.diag12[0] == v0 and q.diag03[1] == v2 and q.colour == colour:
                        self.sub_sqr(s)
                        v0,v2 = q.diag03[0],q.diag12[1]
                        break
                     else: self.ret_sqr(s)
            else: break
         self.add_sqr(quad(v0,v1,v2,v3,colour))

   def add(self,scale,i0,j0,k0,vs):
      with self:
         for v in vs:
            x0,y0,z0 = v[0][0],v[0][1],v[0][2]
            x1,y1,z1 = v[0][3],v[0][4],v[0][5]

            x0 = (x0+i0)*scale
            y0 = (y0+j0)*scale
            z0 = (z0+k0)*scale
            x1 = (x1+i0)*scale
            y1 = (y1+j0)*scale
            z1 = (z1+k0)*scale
            if   y0 == y1:
               v0 = Vec3(x0,y0,z1)
               v1 = Vec3(x0,y0,z0)
               v2 = Vec3(x1,y1,z1)
               v3 = Vec3(x1,y1,z0)
            elif x0 == x1:
               v0 = Vec3(x0,y1,z0)                           
               v1 = Vec3(x0,y0,z0)
               v2 = Vec3(x1,y1,z1)
               v3 = Vec3(x1,y0,z1)
            else:
               v0 = Vec3(x0,y1,z1)
               v1 = Vec3(x0,y0,z0)
               v2 = Vec3(x1,y1,z1)
               v3 = Vec3(x1,y0,z0)

            self.add_quad(v0,v1,v2,v3,v[1])
