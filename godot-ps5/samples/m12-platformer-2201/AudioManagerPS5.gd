extends Node
# Lazy equivalent of original AudioManager, keeps jump_sfx.play() API.
# Never tries to decode original WAVs before a visible loader exists.
var jump_sfx: AudioStreamPlayer
var coin_pickup_sfx: AudioStreamPlayer
var death_sfx: AudioStreamPlayer
var respawn_sfx: AudioStreamPlayer
var level_complete_sfx: AudioStreamPlayer
var _audio_tick: int = 0
var _audio_started: bool = false

func _ready() -> void:
    jump_sfx = _make_player("JumpSfx", -3.0)
    coin_pickup_sfx = _make_player("CoinPickup", 0.0)
    death_sfx = _make_player("DeathSfx", -3.0)
    respawn_sfx = _make_player("RespawnSfx", 0.0)
    level_complete_sfx = _make_player("LevelCompleteSfx", -4.0)
    print("GODOT_PS5_M12B_AUDIO_MANAGER_LIGHT_READY")

func _make_player(name: String, volume_db: float) -> AudioStreamPlayer:
    var player := AudioStreamPlayer.new()
    player.name = name
    player.volume_db = volume_db
    add_child(player)
    return player

func _process(_delta: float) -> void:
    if _audio_started:
        return
    var scene := get_tree().current_scene
    if scene == null or not scene.name.begins_with("Level_"):
        return
    _audio_tick += 1
    if _audio_tick < 15:
        return
    _audio_started = true
    print("GODOT_PS5_M12B_AUDIO_LOAD_BEGIN")
    _assign(jump_sfx, "res://Assets/Sound/FX/jump.wav")
    _assign(coin_pickup_sfx, "res://Assets/Sound/FX/coin_pickup.wav")
    _assign(death_sfx, "res://Assets/Sound/FX/hurt.wav")
    _assign(level_complete_sfx, "res://Assets/Sound/FX/level_complete.wav")
    _assign(respawn_sfx, "res://Assets/Sound/FX/hurt.wav")
    print("GODOT_PS5_M12B_AUDIO_LOAD_COMPLETE")

func _assign(player: AudioStreamPlayer, path: String) -> void:
    print("GODOT_PS5_M12B_AUDIO_FILE_BEGIN ", path)
    var sound := ResourceLoader.load(path)
    if sound is AudioStream:
        player.stream = sound
        print("GODOT_PS5_M12B_AUDIO_FILE_OK ", path)
    else:
        print("GODOT_PS5_M12B_AUDIO_FILE_FAIL ", path)
