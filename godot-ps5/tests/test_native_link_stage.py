#!/usr/bin/env python3
"""Offline test of the real Godot-to-PS5DevBridge linker staging."""
import importlib.util
import json
from pathlib import Path
import tempfile

path=Path(__file__).resolve().parents[1]/"scripts/stage_native_link.py"
spec=importlib.util.spec_from_file_location("godot_link",path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    gd=root/"godot"
    app=root/"app"
    (app/"tools").mkdir(parents=True)
    (app/"sce_sys").mkdir()
    (app/"tooling/native").mkdir(parents=True)
    (app/"tooling/native/sce_module_writer.cpp").write_text(
        "const ProgramHeader text = {kProgramLoad, kFlagExecute, text.file_offset, 0, text_end, text_end, kPage};\n"
    )
    (app/"tooling/native/app_crt.cpp").write_text(
        'extern "C" {\n'
        '    void jb_startup_mark(const char*) __attribute__((weak));\n'
        '}\n'
        'void smoke_crt(){\n'
        '  if(jb_startup_mark)jb_startup_mark("before runtime");\n'
        '  if (jb_startup_mark) jb_startup_mark("after runtime");\n'
        '  if (jb_startup_mark) jb_startup_mark("before constructors");\n'
        '  if(jb_startup_mark)jb_startup_mark("after constructors");\n'
        '  if (jb_startup_mark) jb_startup_mark("thread entered");\n'
        '}\n'
        'namespace\n{\nstruct MainArguments {int argc;};\n'
        'void run_application(void *opaque) {\n'
        '    args->status = application_main(args->argc, args->argv, nullptr);\n'
        '}\n'
        'void _start() {\n'
        '    _init_env(process_parameters);\n'
        '    _init();\n'
        '    int rc = pthread_attr_init(&attr);\n'
        '    rc = pthread_join(thread, nullptr);\n'
        '}\n'
    )
    entry=root/"main.cpp"
    entry.write_text('extern "C" int godot_ps5_run_pack(const char*);')
    (app/"sce_sys/param.json").write_text(json.dumps({"localizedParameters":{"en-US":{}}}))
    (app/"tools/build.sh").write_text(
      'link_inputs=("$build/obj/app_crt.o" "$build/obj/app_cpp_runtime.o" "${objects[@]}")\n'
      'for archive in "${archives[@]}"; do\n'
      '    [[ $archive =~ ^[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)*\\.a$ && -f $root/$archive ]] || exit 2\n'
      "for name in ['ZSTD_trace_decompress_begin','ZSTD_trace_decompress_end','__dlopen']:\n"
      '    link_inputs+=("$root/$archive")\n'
      'done\n')
    files=[]
    for i in range(52):
        name="libcore" if i==0 else "libmain" if i==1 else "libmodule_gdscript" if i==2 else "libother"+str(i)
        location=("bin/obj/core/" if i==0 else "bin/obj/main/" if i==1 else
                  "bin/obj/modules/" if i==2 else "bin/obj/misc/")
        rel=location+name+".ps5.template_debug.x86_64.a"
        f=gd/rel
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_bytes(b"!<arch>\n"+b"X"*128)
        files.append({"path":rel,"size_bytes":f.stat().st_size})
    (gd/"godot-ps5-full-manifest.json").write_text(json.dumps({
        "format":"godot-ps5-static-libs", "target":"x86_64-sie-ps5",
        "archive_count":len(files), "archives":files
    }))
    sdk = app/".deps/native/ps5-payload-sdk/target/lib"
    sdk.mkdir(parents=True)
    for lib in ("libc++.a", "libc++abi.a", "libunwind.a", "libc.a"):
        (sdk/lib).write_bytes(b"!<arch>\n"+b"Q"*128)
    builtins=root/"libclang_rt.builtins-x86_64.a"
    builtins.write_bytes(b"!<arch>\n"+b"R"*128)
    assert module.stage(gd,app,entry,builtins_override=builtins) is None
    crt=(app/"tooling/native/app_crt.cpp").read_text()
    assert "jb_startup_mark" not in crt
    self_writer=(app/"tooling/native/sce_module_writer.cpp").read_text()
    assert "{kProgramLoad, kFlagExecute, text.file_offset, 0, text_end, text_end, kPage}" in self_writer
    assert "kFlagRead | kFlagExecute, text.file_offset" not in self_writer
    assert "LIBC_INIT_RETURNED" in crt
    assert "AFTER_STATIC_CONSTRUCTORS" in crt
    assert "BEFORE_THREAD_CREATION" in crt
    assert "APP_THREAD_ENTER" in crt
    assert "engine-boot-v022.log" in crt
    assert "void smoke_crt()" in crt
    b=(app/"tools/build.sh").read_text()
    assert '--start-group' in b and '--end-group' in b
    assert '[A-Za-z0-9_.+-]+' in b, "PS5 libc++.a filenames rejected by old regex"
    assert "'ZSTD_trace_compress_begin','ZSTD_trace_compress_end'" in b
    assert '--defsym=_ZTHN14ResourceLoader12load_nestingE=0' in b
    assert 'APP_STATIC_ARCHIVES :=' in (app/"GNUmakefile").read_text()
    assert 'libmodule_gdscript' in (app/"GNUmakefile").read_text()
    assert (app/"godot-libs"/files[0]["path"]).is_file()
    assert (app/"godot-libs/runtime/libc++abi.a").is_file()
    assert json.loads((app/"sce_sys/param.json").read_text())["titleId"]=="PPSA99843"
    assert (app/"src/godot-smoke/main.cpp").is_file()
print("PASS: All 52 Godot libraries staged for grouped headless PS5 link")
