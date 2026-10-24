extends SceneTree

func _initialize() -> void:
    var packer := PCKPacker.new()
    var output := ProjectSettings.globalize_path("res://pong.pck")
    var status := packer.pck_start(output)
    if status != OK:
        push_error("PONG_PACK_START_ERROR " + str(status))
        quit(1)
        return
    for name in ["project.godot", "main.tscn", "main.gd"]:
        status = packer.add_file("res://" + name,
                ProjectSettings.globalize_path("res://" + name))
        if status != OK:
            push_error("PONG_PACK_FILE_ERROR " + name + " " + str(status))
            quit(2)
            return
    status = packer.flush()
    if status != OK:
        push_error("PONG_PACK_FLUSH_ERROR " + str(status))
        quit(3)
        return
    print("GODOT_PS5_PONG_PCK_WRITTEN")
    quit(0)
