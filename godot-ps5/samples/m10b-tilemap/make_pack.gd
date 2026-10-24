extends SceneTree

func _initialize() -> void:
    var packer := PCKPacker.new()
    var file_out := ProjectSettings.globalize_path("res://m10b-tilemap.pck")
    var status: Error = packer.pck_start(file_out)
    if status != OK:
        push_error("GODOT_PS5_M10B_TILE_PACK_FAIL start=" + str(status))
        quit(80)
        return
    for file in ["project.godot", "main.tscn", "main.gd"]:
        status = packer.add_file("res://" + file, ProjectSettings.globalize_path("res://" + file))
        if status != OK:
            push_error("GODOT_PS5_M10B_TILE_PACK_FAIL file=" + file)
            quit(81)
            return
    status = packer.flush()
    if status != OK:
        push_error("GODOT_PS5_M10B_TILE_PACK_FAIL flush=" + str(status))
        quit(82)
        return
    print("GODOT_PS5_M10B_TILE_PCK_WRITTEN")
    quit(0)
