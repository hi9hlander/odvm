from panda3d.core import *
from direct.interval.IntervalGlobal import *
from odvm.renderer import Renderer
from odvm.optimizedvm import OptimizedVM
import cProfile
import pstats


viewport_vert_glsl = """ 
#version 130

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;
uniform vec3 gnormal;

in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

     out vec2  texcoord;
flat out vec4  color;
flat out vec2  pnormal;
     out float pos_w;

void main() 
{ 
   vec4    pos = p3d_ModelViewProjectionMatrix*p3d_Vertex;
   gl_Position = pos;
   texcoord    = p3d_MultiTexCoord0;
   color       = p3d_Color;
   vec3 nrm    = p3d_NormalMatrix*gnormal;
   pnormal     = nrm.xy*inversesqrt(0.5*nrm.z+0.5);
   pos_w       = 0.01*pos.w;
}
""" 

viewport_frag_glsl = """ 
#version 130

uniform sampler2D p3d_Texture0; 

     in vec2  texcoord;
flat in vec4  color;
flat in vec2  pnormal;
     in float pos_w;

void main() 
{ 
   vec4 clr = texture2D(p3d_Texture0,texcoord)*color;
   gl_FragData[0] = clr;
   gl_FragData[1] = vec4( pnormal, pos_w, step(0.5,clr.a) );
} 
""" 

composer_vert_glsl = """ 
#version 130

out vec2 texcoord;

void main()
{
   vec2     ij = vec2(float((gl_VertexID&1)<<2),float((gl_VertexID&2)<<1));
   gl_Position = vec4(ij-1.0,0.0,1.0);
   texcoord    = ij*0.5;
} 
""" 

composer_frag_glsl = """ 
#version 130

uniform sampler2D p3d_Texture0; 
uniform sampler2D aux0;
uniform vec4      viewport;
uniform float     thickness;

in vec2 texcoord;

void main() 
{ 
   vec4    clr = texture2D(p3d_Texture0,texcoord);
   vec3 nxy_pz = texture2D(aux0,texcoord).xyz;
   float  x2y2 = dot(nxy_pz.xy,nxy_pz.xy);
   vec3    nrm = vec3( nxy_pz.xy*sqrt(1.0-0.25*x2y2), 1.0-0.5*x2y2 );
   vec3    eye = normalize(vec3(gl_FragCoord.xy*viewport.st+viewport.pq,1.0));
   float   dne = max(dot(nrm,eye),0.0);
   float   pti = dne*0.5;
   vec3    dtl = vec3(0.0,1.0,0.0);
   float   dti = max(dot(nrm,dtl)*0.5,0.0);
   float   fni = pti+dti+0.2;

   float  ds = thickness*dFdx(texcoord.s);
   float  dt = thickness*dFdy(texcoord.t);

   float z01 = texture2D(aux0,vec2(texcoord.s   ,texcoord.t-dt)).z;
   float z10 = texture2D(aux0,vec2(texcoord.s-ds,texcoord.t   )).z;
   float z12 = texture2D(aux0,vec2(texcoord.s+ds,texcoord.t   )).z;
   float z21 = texture2D(aux0,vec2(texcoord.s   ,texcoord.t+dt)).z;

   float e   = abs(nxy_pz.z-max(max(z01,z21),max(z10,z12)))*dne;
   float g   = step(0.01*nxy_pz.z,e);

   gl_FragColor = clr*fni*(1.0-g);
} 
""" 


def unlock_camera(): base.disable_mouse()


def lock_camera():
   mat = Mat4(base.camera.get_mat())
   mat.invert_in_place()
   base.mouseInterfaceNode.set_mat(mat)
   base.enable_mouse()


class Demo(Renderer):
   def __init__(self):
      Renderer.__init__(self)
      self.viewport.add_shader( viewport_vert_glsl, viewport_frag_glsl )
      self.composer.add_shader( composer_vert_glsl, composer_frag_glsl )
      base.set_frame_rate_meter(True)

      self.model = OptimizedVM( 'VoxelModel', GeomVertexFormat.get_v3c4(), 1 )
      self.model.set_shader_input( Vec3( 1.0,0.0,0.0), 'gnormal', Vec3( 1.0,0.0,0.0) )
      self.model.set_shader_input( Vec3(-1.0,0.0,0.0), 'gnormal', Vec3(-1.0,0.0,0.0) )
      self.model.set_shader_input( Vec3(0.0, 1.0,0.0), 'gnormal', Vec3(0.0, 1.0,0.0) )
      self.model.set_shader_input( Vec3(0.0,-1.0,0.0), 'gnormal', Vec3(0.0,-1.0,0.0) )
      self.model.set_shader_input( Vec3(0.0,0.0, 1.0), 'gnormal', Vec3(0.0,0.0, 1.0) )
      self.model.set_shader_input( Vec3(0.0,0.0,-1.0), 'gnormal', Vec3(0.0,0.0,-1.0) )

      self.model_path = render.attach_new_node(self.model)
      self.model_path.set_color_off()
      self.model_path.set_attrib(CullFaceAttrib.make(CullFaceAttrib.MCullClockwise))
      self.model_path.set_transparency(TransparencyAttrib.MDual)
      self.model_path.set_render_mode_filled()
      self.composer.output.set_shader_input( 'thickness', 2.0 )
      
      self.model_path.hprInterval(10.0,Point3(-360,0,0)).loop()
      Sequence(Wait(3.0),Func(self.toggle_wireframe)).loop()

      unlock_camera()
      base.camera.set_pos(32,32,32)
      base.camera.look_at(0,0,0)
      lock_camera()

      base.accept( 'w', self.toggle_wireframe )

      base.bufferViewer.position = 'llcorner'
      base.bufferViewer.setCardSize(0,0.5)
      base.bufferViewer.layout   = 'vline'

      base.accept( 'v', self.toggle_cards )

   def toggle_wireframe(self):
      if   self.model_path.get_render_mode() == 2:
         self.model_path.set_render_mode_filled()
         self.composer.output.set_shader_input( 'thickness', 2.0 )
      elif self.model_path.get_render_mode() == 1 or self.model_path.get_render_mode() == 0:
         self.model_path.set_render_mode_wireframe()
         self.composer.output.set_shader_input( 'thickness', 0.0 )

   def toggle_cards(self):
      render.analyze()
      print( self.viewport.depth_stencil, self.viewport.color )
      if hasattr(self.viewport,'aux0'): print( self.viewport.aux0 )
      base.bufferViewer.toggleEnable()

   def geometry_test1(self):
      self.model.add(4,  0,0,0, Vec4(1.0,1.0,1.0,1.0))
      self.model.add(4, -1,0,0, Vec4(1.0,1.0,1.0,1.0))
      self.model.add(4, -1,0,1, Vec4(1.0,1.0,1.0,1.0))
      self.model.add(1 , 3,3,1, Vec4(1.0,1.0,1.0,1.0))
      self.model.add(1 , 3,4,1, Vec4(1.0,1.0,1.0,1.0))
      self.model.optimize()

   def geometry_test2(self):
      with self.model.quads:
         for (i,j,k) in ( (i,j,k) for i in range(-8,9) for j in range(-8,9) for k in range(-8,9) ):
            if i*i+j*j+k*k <= 144: self.model.add(0,i,j,k,Vec4(1.0,1.0,1.0,1.0))
         self.model.optimize()

   def geometry_test3(self):
      with self.model.quads:
         for (i,j,k) in ( (i,j,k) for i in range(-8,9) for j in range(-8,9) for k in range(-8,9) ):
            if i*i+j*j+k*k <= 9: self.model.add(0,i,j,k,Vec4(1.0,1.0,1.0,1.0))
         self.model.optimize()

   def geometry_test4(self):
      with self.model.quads:
         for (i,j,k) in ( (i,j,k) for i in range(-8,9) for j in range(-8,9) for k in range(-8,9) ):
            if i*i+j*j+k*k <= 25: self.model.add(0,i,j,k,Vec4(1.0,1.0,1.0,1.0))
         self.model.optimize()

   def geometry_test5(self):
      with self.model.quads:
         for (i,j,k) in ( (i,j,k) for i in range(-8,9) for j in range(-8,9) for k in range(-8,9) ):
            if all( s[0]*s[0]+s[1]*s[1]+s[2]*s[2] <= 36 for s in ( (i,j,k), (i+1,j+1,k-1), (i+1,j,k), (i,j+1,k), (i,j,k-1), (i+1,j+1,k), (i+1,j,k-1), (i,j+1,k-1) ) ): self.model.add(0,i,j,k,Vec4(1.0,1.0,1.0,1.0))
         self.model.optimize()

   def geometry_test6(self):
      with self.model.quads:
         for (i,j,k) in ( (i,j,k) for i in range(-8,9) for j in range(-8,9) for k in range(-8,9) ):
            x = i+0.5
            y = j+0.5
            z = k+0.5
            if x*x+y*y+z*z <= 36: self.model.add(0,i,j,k,Vec4(1.0,1.0,1.0,1.0))
         self.model.optimize()

   def geometry_test7(self):
      cmap   = { 'd': Vec4(0.235,0.235,0.141,1.0), 'w': Vec4(1.0,0.992,0.941,1.0), 'g': Vec4(0.447,0.678,0.176,1.0) }

      layers = (('......',
                 '.gggg.',
                 '.gggg.',
                 '.gggg.',
                 '.gggg.',
                 '......'),

                ('.gggg.',
                 'gggggg',
                 'gggggg',
                 'gggggg',
                 'gggggg',
                 '.gggg.'),

                ('.gggg.',
                 'gggggg',
                 'gggggg',
                 'gggggg',
                 'gggggg',
                 '.gggg.'),

                ('......',
                 '.gggg.',
                 '.gggg.',
                 '.gggg.',
                 '.gggg.',
                 '......'),

                ('......',
                 '......',
                 '..ww..',
                 '..ww..',
                 '......',
                 '......'),

                ('......',
                 '......',
                 '..wd..',
                 '..dw..',
                 '......',
                 '......'),

                ('......',
                 '......',
                 '..ww..',
                 '..ww..',
                 '......',
                 '......'),

                ('......',
                 '......',
                 '..dw..',
                 '..wd..',
                 '......',
                 '......'),

                ('......',
                 '......',
                 '..ww..',
                 '..ww..',
                 '......',
                 '......'),

                ('......',
                 '..ww..',
                 '.wwww.',
                 '.wwww.',
                 '..ww..',
                 '......'))

      with self.model.quads:
         for j,p in enumerate(reversed(layers)):
            for k,r in enumerate(p):
               for i,c in enumerate(r):
                  if c in cmap: self.model.add(0,i-3,j-5,k-2,cmap[c])
         self.model.optimize()

   def geometry_test8(self):
      srgba = [Vec4(1.0,1.0,1.0,1.0)]*256
      rgba_prcd = False
      xyzi_pmtd = False
      with open( 'teapot.vox', 'rb' ) as f:
      # with open( 'monu7.vox', 'rb' ) as f:
         if f.read(4) != b'VOX ': raise IOError
         version = int.from_bytes(f.read(4),byteorder='little')
         while f:
            chunk_id = f.read(4)
            if not chunk_id:
               if not rgba_prcd:
                  srgba[0] = Vec4(0.0,0.0,0.0,0.0)
                  # load default palette
                  rgba_prcd = True
               if not xyzi_pmtd:
                  xyzi_pmtd = True
                  f.seek(8,0)
                  continue
               else: break
            cn = int.from_bytes(f.read(4),byteorder='little')
            cm = int.from_bytes(f.read(4),byteorder='little')
            print(chunk_id.decode(),cn,cm)
            if chunk_id == b'MAIN': continue
            if chunk_id == b'SIZE':
               sx = int.from_bytes(f.read(4),byteorder='little')
               sz = int.from_bytes(f.read(4),byteorder='little')
               sy = int.from_bytes(f.read(4),byteorder='little')
               print(sx,sy,sz)
               continue
            if chunk_id == b'XYZI' and xyzi_pmtd:
               n = int.from_bytes(f.read(4),byteorder='little')
               with self.model.quads:
                  for i in range(n):
                     x = int.from_bytes(f.read(1),byteorder='little')
                     z = int.from_bytes(f.read(1),byteorder='little')
                     y = int.from_bytes(f.read(1),byteorder='little')
                     c = int.from_bytes(f.read(1),byteorder='little')
                     self.model.add(0,x-(sx>>1),y-(sy>>1),z-(sz>>1),srgba[c])
                  self.model.optimize()
               continue
            if chunk_id == b'RGBA' and not rgba_prcd:
               for i in range(1,257):
                  r = int.from_bytes(f.read(1),byteorder='little')
                  g = int.from_bytes(f.read(1),byteorder='little')
                  b = int.from_bytes(f.read(1),byteorder='little')
                  a = int.from_bytes(f.read(1),byteorder='little')
                  srgba[i&255] = Vec4(r/255.0,g/255.0,b/255.0,a/255.0) # need to convert to srgb color space
               rgba_prcd = True
               continue
            f.seek( cn+cm, 1 )
      unlock_camera()
      base.camera.set_pos(128,128,128)
      lock_camera()

   def geometry_test9(self):
      for (i,j,k) in ( (i,j,k) for i in range(20,-22,-2) for j in range(20,-22,-2) for k in range(20,-22,-2) ):
         self.model.add(0,i,j,k,Vec4(1.0,1.0,1.0,1.0))
      self.model.optimize()


game = Demo()
# cProfile.run('game.geometry_test1()','demo.profile')
# cProfile.run('game.geometry_test2()','demo.profile')
# cProfile.run('game.geometry_test3()','demo.profile')
# cProfile.run('game.geometry_test4()','demo.profile')
# cProfile.run('game.geometry_test5()','demo.profile')
# cProfile.run('game.geometry_test6()','demo.profile')
# cProfile.run('game.geometry_test7()','demo.profile')
try: cProfile.run('game.geometry_test8()','demo.profile')
except FileNotFoundError: cProfile.run('game.geometry_test7()','demo.profile')
# cProfile.run('game.geometry_test9()','demo.profile')

pstats.Stats('demo.profile').strip_dirs().sort_stats('time').print_stats()
game.run()
