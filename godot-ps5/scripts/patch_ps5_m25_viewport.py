#!/usr/bin/env python3
"""M25 PS5-only: time Godot RendererViewport's canvas, blit, present and other work.

Original pinned Godot 4.7.2, real GLES3 renderer, no GL call wrappers or
render mutations. M24 TAR #44 localized every bad frame to draw_viewports().
Do not conflate DisplayServer EGL swap duration with rasterizer framebuffer
blit or Godot canvas renderer cost.
"""
from pathlib import Path
import sys

TAG="GODOT_PS5_M25_VIEWPORT_5S"
G="#if defined(PS5_ENABLED) && defined(GODOT_PS5_NATIVE_GLES3)"
E="#endif // PS5 native GLES3 M25"

def patch(s):
    if TAG in s:
        if s.count(TAG)!=1 or "GODOT_PS5_M25_VIEWPORT_READY" not in s:
            raise ValueError("M25 partial patch")
        return s
    def once(a,b):
        nonlocal s
        if s.count(a)!=1:
            raise ValueError(f"Godot 4.7.2 viewport source drift ({s.count(a)}): {a[:120]}")
        s=s.replace(a,b,1)
    marker='#include "renderer_viewport.h"\n'
    globals=rf"""
{G}
#include <cstdio>
// Small counters only. For native GLES3, Godot draws through one PS5
// graphics context/thread; all sums reset once per draw_viewports() call.
static uint64_t m25_canvas_us=0;
static uint64_t m25_context_us=0;
static uint64_t m25_draw_us=0;
static uint64_t m25_blit_us=0;
static uint64_t m25_present_us=0;
static uint64_t m25_draw_total_us=0;
static uint64_t m25_report_epoch=0;
static uint64_t m25_total_us[6]={{}};
static uint64_t m25_peak_us[6]={{}};
static unsigned m25_frames=0;
static unsigned m25_spikes=0;
static unsigned m25_reported=0;
static void m25_account(unsigned i,uint64_t value) {{
    m25_total_us[i]+=value;
    if(value>m25_peak_us[i])m25_peak_us[i]=value;
}}
{E}
"""
    once(marker,marker+globals)
    openfunc='void RendererViewport::draw_viewports(bool p_swap_buffers) {\n'
    once(openfunc,openfunc+f"""{G}
    const uint64_t m25_begin=OS::get_singleton()->get_ticks_usec();
    m25_canvas_us=m25_context_us=m25_draw_us=m25_blit_us=m25_present_us=0;
{E}
""")
    makecur='\t\tDisplayServer::get_singleton()->gl_window_make_current(p_viewport->viewport_to_screen);'
    once(makecur,f"""{G}
        const uint64_t m25_cur_before=OS::get_singleton()->get_ticks_usec();
{E}
{makecur}
{G}
        m25_context_us+=OS::get_singleton()->get_ticks_usec()-m25_cur_before;
{E}""")
    pre='\t\t\tRENDER_TIMESTAMP("> Render Canvas " + itos(canvas_idx));'
    post='\t\t\tRENDER_TIMESTAMP("< Render Canvas " + itos(canvas_idx));'
    once(pre,pre+f"""
{G}
            const uint64_t m25_canvas_before=OS::get_singleton()->get_ticks_usec();
{E}""")
    once(post,f"""{G}
            m25_canvas_us+=OS::get_singleton()->get_ticks_usec()-m25_canvas_before;
{E}
{post}""")
    draw='\t\t\t// render standard mono camera\n\t\t\t_draw_viewport(vp);'
    once(draw,f"""\t\t\t// render standard mono camera
{G}
            const uint64_t m25_draw_before=OS::get_singleton()->get_ticks_usec();
{E}
            _draw_viewport(vp);
{G}
            m25_draw_us+=OS::get_singleton()->get_ticks_usec()-m25_draw_before;
{E}""")
    pair='\t\t\t\t\tRSG::rasterizer->blit_render_targets_to_screen(vp->viewport_to_screen, &blit, 1);\n\t\t\t\t\tRSG::rasterizer->gl_end_frame(p_swap_buffers);'
    once(pair,f"""{G}
                    const uint64_t m25_blit_before=OS::get_singleton()->get_ticks_usec();
{E}
                    RSG::rasterizer->blit_render_targets_to_screen(vp->viewport_to_screen, &blit, 1);
{G}
                    m25_blit_us+=OS::get_singleton()->get_ticks_usec()-m25_blit_before;
                    const uint64_t m25_present_before=OS::get_singleton()->get_ticks_usec();
{E}
                    RSG::rasterizer->gl_end_frame(p_swap_buffers);
{G}
                    m25_present_us+=OS::get_singleton()->get_ticks_usec()-m25_present_before;
{E}""")
    terminator='\n}\n\nRID RendererViewport::viewport_allocate()'
    reporter=r"""
#if defined(PS5_ENABLED) && defined(GODOT_PS5_NATIVE_GLES3)
    const uint64_t m25_end=OS::get_singleton()->get_ticks_usec();
    const uint64_t m25_wall=m25_end>=m25_begin?m25_end-m25_begin:0;
    // Unprofiled time includes the viewport list setup/culling, XR and
    // any additional screen blits, so it MUST be reported explicitly.
    const uint64_t m25_known=m25_draw_us+m25_blit_us+m25_present_us;
    const uint64_t m25_other=m25_wall>m25_known?m25_wall-m25_known:0;
    const uint64_t m25_canvas=m25_canvas_us;
    const uint64_t m25_draw_other=m25_draw_us>m25_canvas+m25_context_us?
        m25_draw_us-m25_canvas-m25_context_us:0;
    const uint64_t values[6]={m25_wall,m25_canvas,m25_draw_other,m25_blit_us,m25_present_us,m25_other};
    for(unsigned i=0;i<6;++i)m25_account(i,values[i]);
    ++m25_frames;
    if(m25_wall>=80000) {
        ++m25_spikes;
        if(m25_reported<3) {
            ++m25_reported;
            std::printf("GODOT_PS5_M25_VIEWPORT_SPIKE wall_ms=%.2f canvas_ms=%.2f draw_other_ms=%.2f context_ms=%.2f blit_ms=%.2f gl_end_ms=%.2f other_ms=%.2f\n",
                m25_wall/1000.0,m25_canvas/1000.0,m25_draw_other/1000.0,m25_context_us/1000.0,
                m25_blit_us/1000.0,m25_present_us/1000.0,m25_other/1000.0);
        }
    }
    if(m25_report_epoch==0) {
        m25_report_epoch=m25_end;
        std::printf("GODOT_PS5_M25_VIEWPORT_READY stages=canvas,draw_other,context,blit,gl_end,other original_gles3=1\n");
    }
    if(m25_end>=m25_report_epoch && m25_end-m25_report_epoch>=5000000) {
        std::printf("GODOT_PS5_M25_VIEWPORT_5S frames=%u spikes_80ms=%u max_wall_ms=%.2f max_canvas_ms=%.2f max_draw_other_ms=%.2f max_blit_ms=%.2f max_gl_end_ms=%.2f max_other_ms=%.2f avg_wall_ms=%.2f avg_canvas_ms=%.2f avg_draw_other_ms=%.2f avg_blit_ms=%.2f avg_gl_end_ms=%.2f avg_other_ms=%.2f\n",
            m25_frames,m25_spikes,
            m25_peak_us[0]/1000.0,m25_peak_us[1]/1000.0,m25_peak_us[2]/1000.0,
            m25_peak_us[3]/1000.0,m25_peak_us[4]/1000.0,m25_peak_us[5]/1000.0,
            double(m25_total_us[0])/double(m25_frames)/1000.0,
            double(m25_total_us[1])/double(m25_frames)/1000.0,
            double(m25_total_us[2])/double(m25_frames)/1000.0,
            double(m25_total_us[3])/double(m25_frames)/1000.0,
            double(m25_total_us[4])/double(m25_frames)/1000.0,
            double(m25_total_us[5])/double(m25_frames)/1000.0);
        m25_report_epoch=m25_end;
        m25_frames=m25_spikes=m25_reported=0;
        for(unsigned i=0;i<6;++i)m25_total_us[i]=m25_peak_us[i]=0;
    }
#endif
"""
    once(terminator,"\n"+reporter+terminator)
    return s

if __name__=="__main__":
    f=Path(sys.argv[1]) if len(sys.argv)>1 else Path("servers/rendering/renderer_viewport.cpp")
    a=f.read_text()
    b=patch(a)
    if b!=a:
        f.write_text(b)
        print("GODOT_PS5_M25_VIEWPORT_BLIT_STAGES_PATCHED")
    else:
        print("GODOT_PS5_M25_VIEWPORT_BLIT_ALREADY_PATCHED")
