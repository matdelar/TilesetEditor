import sys
from array import array

import pygame
import moderngl
import src.globals as g


class ShaderManager:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
        self.scenes = None
        self.display = pygame.Surface((800, 600))
        self.ctx = moderngl.create_context()
        self.clock = pygame.time.Clock()
        self.quad_buffer = self.ctx.buffer(data=array('f', [
        # position (x, y), uv coords (x, y)
        -1.0, 1.0, 0.0, 0.0,  # topleft
        1.0, 1.0, 1.0, 0.0,   # topright
        -1.0, -1.0, 0.0, 1.0, # bottomleft
        1.0, -1.0, 1.0, 1.0,  # bottomright
        ]))

        self.vert_shader = '''
        #version 330 core

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(vert, 0.0, 1.0);
        }
        '''

        self.frag_shader = '''
        #version 330 core

        uniform sampler2D tex;
        uniform float fe;

        in vec2 uvs;
        out vec4 f_color;

        void main() {

            vec2 fishuv;
            float fishyness = fe;

            vec2 uv = vec2(uvs.xy - 0.5) * 2.0;
            
            fishuv.x = (1.0 - uv.y*uv.y) * fishyness * uv.x;
            fishuv.y = (1.0 - uv.x*uv.x) * fishyness * uv.y;

            float cr = texture(tex, uvs - fishuv*0.8).x;
            vec2 cgb = texture(tex, uvs - fishuv).yz;
            vec3 c = vec3(cr, cgb);

            float uvMagSqrd = dot(uv,uv);
            float vignette = 1.0 - uvMagSqrd * fishyness;
            c *= vignette;

            f_color = vec4(c, 1.0);
        }
        '''

        self.program = self.ctx.program(vertex_shader=self.vert_shader, fragment_shader=self.frag_shader)
        self.render_object = self.ctx.vertex_array(self.program, [(self.quad_buffer, '2f 2f', 'vert', 'texcoord')])
    
    def surf_to_texture(self,surf):
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))
        return tex

    def start(self):
        while True:
            self.display.fill((0, 0, 0))
            self.scenes.update(self.display)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            frame_tex = self.surf_to_texture(self.display)
            frame_tex.use(0)
            self.program['tex'] = 0
            self.program['fe'] = g.fisheye
            self.render_object.render(mode=moderngl.TRIANGLE_STRIP)
            
            pygame.display.flip()
            
            frame_tex.release()
            
            self.clock.tick(60)

