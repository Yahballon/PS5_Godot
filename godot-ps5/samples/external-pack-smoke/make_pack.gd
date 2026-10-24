extends SceneTree

# Produce a standalone project PCK; no rebuilt native PS5 title needed.
func _initialize() -> void:
    var packer := PCKPacker.new()
    var output := ProjectSettings.globalize_path("res://external-smoke.pck")
    var result: Error = packer.pck_start(output)
    if result != OK:
        push_error("GODOT_PS5_EXTERNAL_PACK_FAILED start=" + str(result))
        quit(1)
        return
    for name in ["project.godot", "main.tscn", "main.gd", "second.tscn", "second.gd", "palette.json"]:
        result = packer.add_file("res://" + name,
                ProjectSettings.globalize_path("res://" + name))
        if result != OK:
            push_error("GODOT_PS5_EXTERNAL_PACK_FAILED file=" + name + " status=" + str(result))
            quit(2)
            return
    result = packer.flush()
    if result != OK:
        push_error("GODOT_PS5_EXTERNAL_PACK_FAILED flush=" + str(result))
        quit(3)
        return
    print("GODOT_PS5_EXTERNAL_PCK_WRITTEN")
    quit(0)
