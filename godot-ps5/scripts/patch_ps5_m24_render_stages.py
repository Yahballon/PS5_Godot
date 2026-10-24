#!/usr/bin/env python3
"""M24: lightweight seven-section original Godot RenderingServerDefault::_draw profiler.

Purpose: M23 hardware TAR #43 captures 7.65s inside RenderingServer::draw, but
55 timed GL API functions consume under 5ms in the frozen frames. Attribute the
remaining time to Godot's actual RSG stages, without GL API wrappers or extra
GPU synchronization. Builds only in original pinned Godot 4.7.2 and PS5 GLES3.
"""
from pathlib import Path
import sys

MARK = "GODOT_PS5_M24_RENDER_5S"
G = "#if defined(PS5_ENABLED) && defined(GODOT_PS5_NATIVE_GLES3)"
def guard(s):
    return G+"\n"+s+"\n#endif\n"

def once(s,old,new):
    n=s.count(old)
    if n!=1:
        raise ValueError("Godot 4.7.2 M24 rendering source drift (count=%d): %s" % (n,old[:120]))
    return s.replace(old,new,1)

def patch(source):
    if MARK in source:
        if "GODOT_PS5_M24_RENDER_SPIKE" not in source:
            raise ValueError("Partial M24 stage instrumented Godot source")
        return source
    start="void RenderingServerDefault::_draw(bool p_swap_buffers, double frame_step) {\n"
    stop="void RenderingServerDefault::_"
    a=source.index(start)
    b=source.find(stop,a+len(start))
    if b<0:
        raise ValueError("M24 expected following rendering server function missing")
    before,body,after=source[:a],source[a:b],source[b:]
    before=once(before,'#include "rendering_server_default.h"\n',
       '#include "rendering_server_default.h"\n'+G+'\n#include <cstdio>\n#include <cstdint>\n#endif\n')
    body=once(body,start,start+guard('\tconst uint64_t m24_t0=OS::get_singleton()->get_ticks_usec();'))
    anchors=[
        ('\tRSG::rasterizer->begin_frame(frame_step);\n',1),
        ('\tRSG::canvas->update();\n',2),
        ('\tRSG::scene->render_probes();\n',3),
        ('\tRSG::viewport->draw_viewports(p_swap_buffers);\n',4),
        ('\tRSG::rasterizer->end_frame(p_swap_buffers);\n',5),
    ]
    for anchor,i in anchors:
        body=once(body,anchor,anchor+guard('\tconst uint64_t m24_t%d=OS::get_singleton()->get_ticks_usec();'%i))
    post_anchor='''\tif (create_thread) {
\t\tcallable_mp(this, &RenderingServerDefault::_run_post_draw_steps).call_deferred();
\t} else {
\t\t_run_post_draw_steps();
\t}
'''
    body=once(body,post_anchor,post_anchor+guard('\tconst uint64_t m24_t6=OS::get_singleton()->get_ticks_usec();'))
    finale='\tRSG::utilities->update_memory_info();\n'
    report=r'''
#if defined(PS5_ENABLED) && defined(GODOT_PS5_NATIVE_GLES3)
    const uint64_t m24_t7=OS::get_singleton()->get_ticks_usec();
    const uint64_t m24_ticks[8]={m24_t0,m24_t1,m24_t2,m24_t3,m24_t4,m24_t5,m24_t6,m24_t7};
    static uint64_t m24_epoch=0;
    static uint64_t m24_sums[7]={},m24_peaks[7]={};
    static unsigned m24_frames=0,m24_spikes=0,m24_spike_lines=0;
    const char *m24_names[7]={"begin","scene","prepare","viewport","end","post","profile"};
    uint64_t m24_frame_total=0;
    for(unsigned i=0;i<7;++i) {
        const uint64_t elapsed=m24_ticks[i+1]>=m24_ticks[i]?
            m24_ticks[i+1]-m24_ticks[i]:0;
        m24_sums[i]+=elapsed;
        if(elapsed>m24_peaks[i])m24_peaks[i]=elapsed;
        m24_frame_total+=elapsed;
        if(elapsed>=80000 && m24_spike_lines<3) {
            ++m24_spike_lines;
            std::printf("GODOT_PS5_M24_RENDER_SPIKE stage=%s elapsed_ms=%.2f frame_ms=%.2f\n",
                m24_names[i],elapsed/1000.0,m24_frame_total/1000.0);
        }
    }
    ++m24_frames;
    if(m24_frame_total>=80000)++m24_spikes;
    if(!m24_epoch) {
        m24_epoch=m24_t7;
        std::printf("GODOT_PS5_M24_RENDER_READY stages=begin,scene,prepare,viewport,end,post,profile baseline=no_gl_api_wrappers\n");
    }
    if(m24_t7>=m24_epoch && m24_t7-m24_epoch>=5000000) {
        std::printf("GODOT_PS5_M24_RENDER_5S frames=%u spikes_80ms=%u "
            "max_begin_ms=%.2f max_scene_ms=%.2f max_prepare_ms=%.2f max_viewport_ms=%.2f "
            "max_end_ms=%.2f max_post_ms=%.2f max_profile_ms=%.2f "
            "avg_begin_ms=%.2f avg_scene_ms=%.2f avg_prepare_ms=%.2f avg_viewport_ms=%.2f "
            "avg_end_ms=%.2f avg_post_ms=%.2f avg_profile_ms=%.2f\n",
            m24_frames,m24_spikes,
            m24_peaks[0]/1000.0,m24_peaks[1]/1000.0,m24_peaks[2]/1000.0,
            m24_peaks[3]/1000.0,m24_peaks[4]/1000.0,m24_peaks[5]/1000.0,
            m24_peaks[6]/1000.0,
            double(m24_sums[0])/double(m24_frames)/1000.0,
            double(m24_sums[1])/double(m24_frames)/1000.0,
            double(m24_sums[2])/double(m24_frames)/1000.0,
            double(m24_sums[3])/double(m24_frames)/1000.0,
            double(m24_sums[4])/double(m24_frames)/1000.0,
            double(m24_sums[5])/double(m24_frames)/1000.0,
            double(m24_sums[6])/double(m24_frames)/1000.0);
        m24_epoch=m24_t7;
        m24_frames=m24_spikes=m24_spike_lines=0;
        for(unsigned i=0;i<7;++i)m24_sums[i]=m24_peaks[i]=0;
    }
#endif
'''
    body=once(body,finale,finale+report)
    return before+body+after

if __name__=="__main__":
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path("servers/rendering/rendering_server_default.cpp")
    original=path.read_text()
    result=patch(original)
    if result!=original:
        path.write_text(result)
        print("GODOT_PS5_M24_ORIGINAL_RENDER_STAGES_PATCHED")
    else:
        print("GODOT_PS5_M24_ORIGINAL_RENDER_STAGES_ALREADY_PATCHED")
