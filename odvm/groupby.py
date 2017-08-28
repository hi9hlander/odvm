from panda3d.core import *


class GeomPlanes(Geom):
   def __init__( self, fmt ):
      Geom.__init__( self, GeomVertexData( 'vertices', fmt, Geom.UH_static ) )
      self.faces    = set()
      self.used_v   = []
      self.used_t   = []
      self.unused_v = []
      self.unused_t = []
      self.update_q = set()
      self.tris     = GeomTriangles(Geom.UH_static)
      self.tris.make_indexed()
      self.add_primitive(self.tris)

   def reset(self):
      self.update_q.clear()
      self.unused_v = list(range(self.get_vertex_data().get_num_rows()-1,-1,-1))
      self.unused_t = list(range(self.tris.get_vertices().get_num_rows()-3,-3,-3))
      self.faces.clear()

   def update(self):
      if not self.update_q and not self.unused_v and not self.unused_t: return

      self.vertices = self.modify_vertex_data()
      self.vertex   = GeomVertexWriter( self.vertices, 'vertex' )
      self.colour   = GeomVertexWriter( self.vertices, 'color'  )
      indices       = self.tris.modify_vertices()
      self.index    = GeomVertexRewriter(indices,0)
      while self.update_q: self.update_q.pop().build()

      if self.unused_v:
         self.unused_v.sort()
         num_v    = self.vertices.get_num_rows()
         shrink_v = num_v
         while self.unused_v and self.unused_v[-1] == shrink_v-1:
            self.unused_v.pop()
            shrink_v -= 1
         if shrink_v != num_v: self.vertices.set_num_rows(shrink_v)

      if self.unused_t:
         self.unused_t.sort()
         num_t = indices.get_num_rows()
         refs  = {}
         while self.unused_t:
            num_t -= 3
            idx    = self.unused_t.pop()
            if idx != num_t: refs[idx] = refs.pop(num_t,num_t)
         if refs:
            tmap = {}
            for t,f in refs.items(): 
               self.index.set_row(f)
               i0 = self.index.get_data1i()
               i1 = self.index.get_data1i()
               i2 = self.index.get_data1i()
               self.index.set_row(t)
               self.index.set_data1i(i0)
               self.index.set_data1i(i1)
               self.index.set_data1i(i2)
               tmap[f] = t
            for q in self.faces:
               q.change_triangles(tmap)
               if not tmap: break
            assert( not tmap )
         indices.set_num_rows(num_t)

      del self.index
      del indices
      del self.colour
      del self.vertex
      del self.vertices

   def add_vertex(self,v,c):
      if self.unused_v:
         idx = self.unused_v.pop()
         self.vertex.set_row(idx)
         self.vertex.set_data3f(v)
         self.colour.set_row(idx)
         self.colour.set_data4f(c)
      else:
         idx = self.vertices.get_num_rows()
         self.vertex.set_row(idx)
         self.vertex.add_data3f(v)
         self.colour.set_row(idx)
         self.colour.add_data4f(c)
      self.used_v.append(idx)
      return idx

   def add_triangle(self,i0,i1,i2):
      if self.unused_t:
         idx = self.unused_t.pop()
         self.index.set_row(idx)
         self.index.set_data1i(i0)
         self.index.set_data1i(i1)
         self.index.set_data1i(i2)
      else:
         idx = self.tris.get_vertices().get_num_rows()
         self.tris.add_vertices(i0,i1,i2)
      self.used_t.append(idx)
      return idx


class GroupByNormal(GeomNode):
   def __init__( self, name, fmt ):
      GeomNode.__init__( self, name )
      self.fmt     = fmt
      self.nrm2idx = dict()

   def __getitem__( self, normal ):
      try: return self.nrm2idx[normal][1]
      except KeyError:
         planes = GeomPlanes(self.fmt)
         self.add_geom(planes)
         self.nrm2idx[normal] = ( self.get_num_geoms()-1, planes )
         return planes

   def set_shader_input( self, normal, variable, value ):
      rs = RenderState.make_empty().add_attrib(ShaderAttrib.make().set_shader_input( variable, value ))
      try: self.set_geom_state( self.nrm2idx[normal][0], rs )
      except KeyError:
         planes = GeomPlanes(self.fmt)
         self.add_geom( planes, rs )
         self.nrm2idx[normal] = ( self.get_num_geoms()-1, planes )

   def is_updating(self): return any( v[1].update_q for v in self.nrm2idx.values() )

   def update(self):
      for v in self.nrm2idx.values(): v[1].update()

   def reset(self):
      for v in self.nrm2idx.values(): v[1].reset()
