extends SceneTree

func _initialize() -> void:
    var p := PCKPacker.new()
    var rc: Error = p.pck_start(ProjectSettings.globalize_path("res://m11-saves-v2.pck"))
    if rc != OK:
        push_error("GODOT_PS5_M11B2_PACK_ERROR start=" + str(rc))
        quit(91)
        return
    for filename in ["project.godot", "main.tscn", "main.gd",
                     "PressStart2P-Regular.ttf", "OFL.txt", "FONTLOG.txt"]:
        rc = p.add_file("res://" + filename, ProjectSettings.globalize_path("res://" + filename))
        if rc != OK:
            push_error("GODOT_PS5_M11B2_PACK_ERROR " + filename)
            quit(92)
            return
    rc = p.flush()
    if rc != OK:
        push_error("GODOT_PS5_M11B2_PACK_ERROR flush=" + str(rc))
        quit(93)
        return
    print("GODOT_PS5_M11B2_PCK_WRITTEN")
    quit(0)
