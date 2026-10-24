extends Node2D

# M11a tests the ACTUAL Godot AudioStreamPlayer and AudioServer path.
# The scene creates a real PCM AudioStreamWAV; there is NO PS5 native
# sound-effect shortcut or visual-only pretend sound.
# IMPORTANT: playing==true and host CI do NOT prove that PS5 speakers work.
# The player must audibly hear the rising notes on hardware to accept M11a.

const SAMPLE_RATE: int = 44100
const SECONDS: int = 6
const MAX_VISUAL_FRAMES: int = 660

var player: AudioStreamPlayer
var frames: int = 0
var x_was_down: bool = false
var wave_ready: bool = false
var started: bool = false

func _ready() -> void:
    print("GODOT_PS5_M11_AUDIO_BOOT")
    print("GODOT_PS5_M11_AUDIO_MIX_RATE=", AudioServer.get_mix_rate())
    var stream := AudioStreamWAV.new()
    stream.format = AudioStreamWAV.FORMAT_16_BITS
    stream.mix_rate = SAMPLE_RATE
    stream.stereo = false
    stream.loop_mode = AudioStreamWAV.LOOP_DISABLED
    var pcm := PackedByteArray()
    pcm.resize(SAMPLE_RATE * SECONDS * 2)
    var frequencies := [440.0, 554.37, 659.25, 783.99, 659.25, 440.0]
    # Six one-second notes; each starts with a short fade-in and a short
    # fade-out. Hardware audibility must be confirmed by the person testing.
    for index in range(SAMPLE_RATE * SECONDS):
        var segment: int = int(index / SAMPLE_RATE)
        var fraction: float = float(index % SAMPLE_RATE) / float(SAMPLE_RATE)
        var envelope: float = minf(1.0, fraction * 15.0) * minf(1.0, (0.78 - fraction) * 15.0)
        envelope = clampf(envelope, 0.0, 1.0)
        var sample: float = sin(TAU * frequencies[segment] * fraction) * envelope * 0.36
        pcm.encode_s16(index * 2, int(clampf(sample, -1.0, 1.0) * 32767.0))
    stream.data = pcm
    if stream.data.size() != SAMPLE_RATE * SECONDS * 2:
        print("GODOT_PS5_M11_AUDIO_FAIL_PCM_BYTES")
        get_tree().quit(61)
        return
    wave_ready = true
    print("GODOT_PS5_M11_AUDIO_PCM_READY bytes=", stream.data.size(), " sample_rate=", SAMPLE_RATE)
    player = AudioStreamPlayer.new()
    player.name = "OriginalGodotAudioStreamPlayer"
    player.stream = stream
    player.volume_db = -4.0
    add_child(player)
    player.play()
    if not player.playing:
        print("GODOT_PS5_M11_AUDIO_FAIL_PLAYER_NOT_PLAYING")
        get_tree().quit(62)
        return
    started = true
    print("GODOT_PS5_M11_AUDIO_PLAYER_STARTED")
    print("GODOT_PS5_M11_AUDIO_LISTEN_REQUIRED")
    queue_redraw()

func _process(_delta: float) -> void:
    if not started:
        return
    frames += 1
    var pressed: bool = Input.is_joy_button_pressed(0, JOY_BUTTON_A)
    if pressed and not x_was_down:
        player.play()
        print("GODOT_PS5_M11_AUDIO_X_REPLAY")
    x_was_down = pressed
    if frames == 180:
        print("GODOT_PS5_M11_AUDIO_PLAYBACK_WINDOW frames=", frames, " playing=", player.playing)
    if frames == 420:
        print("GODOT_PS5_M11_AUDIO_END_WINDOW frames=", frames, " playing=", player.playing)
    if frames >= MAX_VISUAL_FRAMES:
        print("GODOT_PS5_M11_AUDIO_HOST_API_PASS")
        print("GODOT_PS5_M11_AUDIO_HARDWARE_AUDIBILITY_UNCONFIRMED")
        get_tree().quit(0)
    queue_redraw()

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, Vector2(1920, 1080)), Color(0.015, 0.027, 0.056), true)
    draw_rect(Rect2(240, 270, 1440, 20), Color(0.97, 0.22, 0.51), true)
    for bar in range(6):
        var glow: bool = started and (frames / 60) % 6 == bar
        var h: float = 100.0 + float(bar) * 62.0
        draw_rect(Rect2(375 + bar * 210, 780 - h, 110, h),
            Color(0.15, 0.96, 0.53) if glow else Color(0.14, 0.81, 0.97), true)
    draw_circle(Vector2(960, 170), 56,
        Color(0.15, 0.96, 0.53) if wave_ready and started else Color(0.96, 0.2, 0.27))
