extends SceneTree

func _initialize() -> void:
    var packer := PCKPacker.new()
    var output := ProjectSettings.globalize_path("res://physics-smoke.pck")
    var result: Error = packer.pck_start(output)
    if result != OK:
        push_error("GODOT_PS5_M9_PACK_FAILED start=" + str(result))
        quit(1)
        return
    for filename in ["project.godot", "main.tscn", "main.gd"]:
        result = packer.add_file("res://" + filename,
               ProjectSettings.globalize_path("res://" + filename))
        if result != OK:
            push_error("GODOT_PS5_M9_PACK_FAILED file=" + filename)
            quit(2)
            return
    result = packer.flush()
    if result != OK:
        push_error("GODOT_PS5_M9_PACK_FAILED flush=" + str(result))
        quit(3)
        return
    print("GODOT_PS5_M9_PCK_WRITTEN")
    quit(0)
