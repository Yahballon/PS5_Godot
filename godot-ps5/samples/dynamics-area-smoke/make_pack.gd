extends SceneTree

func _initialize() -> void:
    var packer := PCKPacker.new()
    var output := ProjectSettings.globalize_path("res://dynamics-area-smoke.pck")
    var error: Error = packer.pck_start(output)
    if error != OK:
        push_error("GODOT_PS5_M10A_PACK_FAILED start=" + str(error))
        quit(61)
        return
    for filename in ["project.godot", "main.tscn", "main.gd"]:
        error = packer.add_file("res://" + filename,
                ProjectSettings.globalize_path("res://" + filename))
        if error != OK:
            push_error("GODOT_PS5_M10A_PACK_FAILED file=" + filename)
            quit(62)
            return
    error = packer.flush()
    if error != OK:
        push_error("GODOT_PS5_M10A_PACK_FAILED flush=" + str(error))
        quit(63)
        return
    print("GODOT_PS5_M10A_PCK_WRITTEN")
    quit(0)
