extends SceneTree
# Pack the ORIGINAL upstream Godot project + imported engine resources.
# A Python script generates ps5_m12_manifest.txt after headless editor import.
func _initialize() -> void:
    var manifest_path := "res://ps5_m12_manifest.txt"
    var output := ProjectSettings.globalize_path("res://m12d-platformer-asset2201.pck")
    var manifest := FileAccess.get_file_as_string(manifest_path)
    if manifest.is_empty():
        push_error("GODOT_PS5_M12_MANIFEST_MISSING")
        quit(91)
        return
    var packer := PCKPacker.new()
    var result := packer.pck_start(output)
    if result != OK:
        push_error("GODOT_PS5_M12_PACK_START_FAIL rc=" + str(result))
        quit(92)
        return
    var count := 0
    for name in manifest.split("\n", false):
        var path: String = name.strip_edges()
        if path.is_empty():
            continue
        result = packer.add_file("res://" + path, ProjectSettings.globalize_path("res://" + path))
        if result != OK:
            push_error("GODOT_PS5_M12_PACK_FILE_FAIL path=" + path + " rc=" + str(result))
            quit(93)
            return
        count += 1
    result = packer.flush()
    if result != OK:
        push_error("GODOT_PS5_M12_PACK_FLUSH_FAIL rc=" + str(result))
        quit(94)
        return
    print("GODOT_PS5_M12D_PCK_WRITTEN files=", count)
    quit(0)
