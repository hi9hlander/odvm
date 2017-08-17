from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from math import tan, radians

def glsl_check_for_use(glsl,feature): return ''.join(feature.split()) in ''.join(glsl.split())

class viewport:
   def __init__(self,idx=0):
      self.index         = idx

      win_props          = WindowProperties()
      props              = FrameBufferProperties()
      props.srgb_color   = True
      props.stencil_bits = 1
      props.alpha_bits   = 0
      props.aux_hrgba    = 1
      self.output = base.graphics_engine.make_output(
         base.pipe, 'viewport{}-output'.format(self.index), -2,
         props, win_props,
         GraphicsPipe.BF_size_track_host | GraphicsPipe.BF_resizeable | GraphicsPipe.BF_refuse_window,
         base.win.gsg, base.win )

      Texture.set_textures_power_2(ATS_none) # otherwise fullscreen triangle won't work

      self.depth_stencil = Texture()
      self.output.get_fb_properties().setup_depth_texture(self.depth_stencil)
      self.depth_stencil.wrap_u = self.depth_stencil.wrap_v = self.depth_stencil.wrap_w = SamplerState.WM_clamp
      self.depth_stencil.magfilter = self.depth_stencil.minfilter = SamplerState.FT_nearest
      self.output.add_render_texture( self.depth_stencil, GraphicsOutput.RTM_bind_or_copy, GraphicsOutput.RTP_depth_stencil )

      self.color = Texture()
      self.output.get_fb_properties().setup_color_texture(self.color)
      self.color.wrap_u = self.color.wrap_v = self.color.wrap_w = SamplerState.WM_clamp
      self.color.magfilter = self.color.minfilter = SamplerState.FT_nearest
      self.output.add_render_texture( self.color, GraphicsOutput.RTM_bind_or_copy, GraphicsOutput.RTP_color )

      self.output.sort = self.index
      self.output.disable_clears()
      self.output.display_regions[0].disable_clears()
      self.output.set_clear_depth_active(True)
      self.output.clear_color = Vec4(0.0,0.5,0.0,0.0)
      self.output.set_clear_color_active(True)
      self.output.clear_delete_flag()

      base.make_camera( self.output, useCamera=base.cam )
      base.cam.node().display_regions[-1].disable_clears()

      self.viewport_inputs = []

   def add_shader(self,vertex,fragment):
      if glsl_check_for_use( fragment, 'gl_FragData[1] =' ):
         self.aux0 = Texture()
         self.aux0.wrap_u = self.aux0.wrap_v = self.aux0.wrap_w = SamplerState.WM_clamp
         self.aux0.magfilter = self.aux0.minfilter = SamplerState.FT_nearest
         self.output.add_render_texture( self.aux0, GraphicsOutput.RTM_bind_or_copy, GraphicsOutput.RTP_aux_hrgba_0 )
         self.output.set_clear_value(GraphicsOutput.RTP_aux_hrgba_0,Vec4(0.0,0.0,1024.0,0.0))
         self.output.set_clear_active(GraphicsOutput.RTP_aux_hrgba_0,True)
      self.shader = ShaderAttrib.make().set_shader(Shader.make( Shader.SLGLSL, vertex, fragment ))
      if glsl_check_for_use( fragment, 'uniform vec4 viewport;' ): self.add_viewport_input(self)
      else                                                       : base.cam.node().set_initial_state(RenderState.make_empty().add_attrib(self.shader))

   def calc_viewport_input(self,win):
      sclx = tan( radians( 0.5 * base.cam.node().get_lens().get_hfov() ) )
      scly = tan( radians( 0.5 * base.cam.node().get_lens().get_vfov() ) )
      self.viewport = Vec4( -2.0*sclx/(win.get_x_size()-1), -2.0*scly/(win.get_y_size()-1), sclx*(1.0+1.0/(win.get_x_size()-1)), scly*(1.0+1.0/(win.get_y_size()-1)) )

   def add_viewport_input(self,obj):
      if not self.viewport_inputs:
         base.accept( 'window-event', self.hook_window_event )
         self.calc_viewport_input(base.win)
      self.viewport_inputs.append(obj)
      obj.set_viewport_input(self.viewport)

   def hook_window_event(self,win):
      base.windowEvent(win)
      self.calc_viewport_input(win)
      for o in self.viewport_inputs: o.set_viewport_input(self.viewport)

   def set_viewport_input(self,viewport):
      self.shader = self.shader.set_shader_input( 'viewport', viewport )
      base.cam.node().set_initial_state(RenderState.make_empty().add_attrib(self.shader))


class composer:
   def __init__(self):
      geom = Geom(GeomVertexData( 'empty-vertices', GeomVertexFormat.get_empty(), GeomEnums.UH_static ))
      tri  = GeomTriangles(GeomEnums.UH_static)
      tri.add_next_vertices(3)
      geom.add_primitive(tri)
      node = GeomNode('composer-full-screen-triangle')
      node.add_geom(geom)
      node.set_bounds(OmniBoundingVolume())
      node.final = True
      self.output = render2d.attach_new_node(node)

   def attach_viewport(self,viewport):
      self.viewport = viewport
      self.output.set_texture(self.viewport.color)

   def add_shader(self,vertex,fragment):
      self.output.set_shader(Shader.make( Shader.SLGLSL, vertex, fragment ))
      if glsl_check_for_use( fragment, 'uniform sampler2D aux0;' ) and hasattr( self.viewport, 'aux0' ): self.output.set_shader_input( 'aux0', self.viewport.aux0 )
      if glsl_check_for_use( fragment, 'uniform vec4 viewport;' ): self.viewport.add_viewport_input(self)

   def set_viewport_input(self,viewport): self.output.set_shader_input( 'viewport', viewport )


class Renderer(ShowBase):
   def __init__(self): 
      load_prc_file_data('','coordinate-system yup_right' )
      load_prc_file_data('','gl-coordinate-system default')
      ShowBase.__init__(self)

      render.set_texture( loader.load_texture('white.png'), 0 )

      base.win.sort = 2
      base.win.disable_clears()
      base.win.display_regions[0].disable_clears()
      base.win.display_regions[0].active = False

      base.cam.node().display_regions[0].disable_clears()
      base.cam.node().display_regions[0].active = False

      base.cam2d.node().display_regions[0].disable_clears()

      render2d.set_two_sided(False)
      render2d.set_depth_write(False)
      render2d.set_depth_test(False)

      self.viewport = viewport()
      self.composer = composer()
      self.composer.attach_viewport(self.viewport)
