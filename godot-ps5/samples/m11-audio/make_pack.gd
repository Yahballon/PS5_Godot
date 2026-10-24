extends SceneTree

func _initialize() -> void:
    var packer := PCKPacker.new()
    var output := ProjectSettings.globalize_path("res://m11-audio.pck")
    var status: Error = packer.pck_start(output)
    if status != OK:
        push_error("GODOT_PS5_M11_AUDIO_PACK_FAIL start=" + str(status))
        quit(81)
        return
    for filename in ["project.godot", "main.tscn", "main.gd"]:
        status = packer.add_file("res://" + filename, ProjectSettings.globalize_path("res://" + filename))
        if status != OK:
            push_error("GODOT_PS5_M11_AUDIO_PACK_FAIL file=" + filename)
            quit(82)
            return
    status = packer.flush()
    if status != OK:
        push_error("GODOT_PS5_M11_AUDIO_PACK_FAIL flush=" + str(status))
        quit(83)
        return
    print("GODOT_PS5_M11_AUDIO_PCK_WRITTEN")
    quit(0)
