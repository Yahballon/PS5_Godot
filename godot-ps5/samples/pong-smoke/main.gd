extends Node2D

# Godot 4.7.2 native Canvas2D Pong: real draw_* calls, not a native GL demo.
# No Label/FreeType dependencies or PhysicsServer2D (still dummy on PS5).
const WIDTH := 1920.0
const HEIGHT := 1080.0
const PADDLE_H := 176.0
const PADDLE_W := 29.0
const PLAYER_X := 120.0
const BOT_X := 1800.0
const BALL_R := 18.0
const PLAYER_SPEED := 900.0
const BOT_SPEED := 710.0
const SCORE_LIMIT := 9
const TIME_LIMIT := 180.0
const SEGMENTS := [63, 6, 91, 79, 102, 109, 125, 7, 127, 111]
const SKY := Color(0.015, 0.026, 0.075)
const CYAN := Color(0.12, 0.94, 1.0)
const MAGENTA := Color(1.0, 0.18, 0.56)
const WHITE := Color(0.89, 0.96, 1.0)

var player_y := HEIGHT * 0.5
var bot_y := HEIGHT * 0.5
var ball_pos := Vector2(WIDTH * 0.5, HEIGHT * 0.5)
var ball_velocity := Vector2(580.0, -230.0)
var playing := false
var game_time := 0.0
var play_time := 0.0
var serve_delay := 0.0
var player_score := 0
var bot_score := 0
var ready_x_previous := false
var reset_circle_previous := false
var start_previous := false
var frame_count := 0
var paddle_seen := false
var hits := 0

func _ready() -> void:
    print("GODOT_PS5_PONG_READY")
    print("GODOT_PS5_PONG_CONTROLS LEFT_STICK_OR_DPAD_UP_DOWN X_SERVE CIRCLE_RESET OPTIONS_EXIT")
    queue_redraw()

func _process(delta: float) -> void:
    var dt := minf(maxf(delta, 0.0), 0.05)
    game_time += dt
    frame_count += 1

    # Actual DualSense → upstream Godot Input singleton.
    var analog: float = Input.get_joy_axis(0, JOY_AXIS_LEFT_Y)
    var movement := analog if absf(analog) > 0.17 else 0.0
    if Input.is_joy_button_pressed(0, JOY_BUTTON_DPAD_UP):
        movement -= 1.0
    if Input.is_joy_button_pressed(0, JOY_BUTTON_DPAD_DOWN):
        movement += 1.0
    movement = clampf(movement, -1.0, 1.0)
    if absf(movement) > 0.01:
        if not paddle_seen:
            print("GODOT_PS5_PONG_PADDLE_INPUT")
            paddle_seen = true
        player_y = clampf(player_y + movement * PLAYER_SPEED * dt,
                          80.0 + PADDLE_H * 0.5, HEIGHT - 80.0 - PADDLE_H * 0.5)

    var x_now := Input.is_joy_button_pressed(0, JOY_BUTTON_A)
    if x_now and not ready_x_previous and not playing and serve_delay <= 0.0:
        playing = true
        ball_pos = Vector2(WIDTH * 0.5, HEIGHT * 0.5)
        var direction := -1.0 if ((player_score + bot_score) % 2) == 0 else 1.0
        ball_velocity = Vector2(580.0 * direction, -230.0)
        print("GODOT_PS5_PONG_SERVE")
    ready_x_previous = x_now

    var circle_now := Input.is_joy_button_pressed(0, JOY_BUTTON_B)
    if circle_now and not reset_circle_previous:
        player_score = 0
        bot_score = 0
        hits = 0
        playing = false
        serve_delay = 0.0
        ball_pos = Vector2(WIDTH * 0.5, HEIGHT * 0.5)
        print("GODOT_PS5_PONG_RESET")
    reset_circle_previous = circle_now

    var start_now := Input.is_joy_button_pressed(0, JOY_BUTTON_START)
    if start_now and not start_previous:
        print("GODOT_PS5_PONG_OPTIONS_EXIT")
        get_tree().quit(0)
    start_previous = start_now

    var bot_target := ball_pos.y if playing and ball_velocity.x > 0.0 else HEIGHT * 0.5
    bot_y = move_toward(bot_y, bot_target, BOT_SPEED * dt)
    bot_y = clampf(bot_y, 80.0 + PADDLE_H * 0.5,
                    HEIGHT - 80.0 - PADDLE_H * 0.5)

    if serve_delay > 0.0:
        serve_delay = maxf(0.0, serve_delay - dt)

    if playing:
        play_time += dt
        ball_pos += ball_velocity * dt
        if ball_pos.y - BALL_R < 76.0:
            ball_pos.y = 76.0 + BALL_R
            ball_velocity.y = absf(ball_velocity.y)
        elif ball_pos.y + BALL_R > HEIGHT - 76.0:
            ball_pos.y = HEIGHT - 76.0 - BALL_R
            ball_velocity.y = -absf(ball_velocity.y)

        var player_hit := ball_velocity.x < 0.0 and absf(ball_pos.x - (PLAYER_X + PADDLE_W * 0.5)) < BALL_R + PADDLE_W * 0.5 and absf(ball_pos.y - player_y) < PADDLE_H * 0.5 + BALL_R
        var bot_hit := ball_velocity.x > 0.0 and absf(ball_pos.x - (BOT_X - PADDLE_W * 0.5)) < BALL_R + PADDLE_W * 0.5 and absf(ball_pos.y - bot_y) < PADDLE_H * 0.5 + BALL_R
        if player_hit or bot_hit:
            ball_velocity.x = -ball_velocity.x
            var offset := (ball_pos.y - (player_y if player_hit else bot_y)) / (PADDLE_H * 0.5)
            ball_velocity.y = offset * 380.0
            ball_velocity = ball_velocity.limit_length(1020.0)
            ball_velocity *= 1.045
            hits += 1
            if hits == 1 or hits % 10 == 0:
                print("GODOT_PS5_PONG_HIT count=", hits)
        if ball_pos.x < -BALL_R:
            bot_score += 1
            _on_score()
        elif ball_pos.x > WIDTH + BALL_R:
            player_score += 1
            _on_score()

    if frame_count == 60:
        print("GODOT_PS5_PONG_60_FRAMES")
    if frame_count % 600 == 0:
        print("GODOT_PS5_PONG_HEARTBEAT frames=", frame_count,
              " player=", player_score, " bot=", bot_score)
    if game_time >= TIME_LIMIT:
        print("GODOT_PS5_PONG_TIMELIMIT_EXIT")
        get_tree().quit(0)
    queue_redraw()

func _on_score() -> void:
    print("GODOT_PS5_PONG_SCORE player=", player_score, " bot=", bot_score)
    playing = false
    ball_pos = Vector2(WIDTH * 0.5, HEIGHT * 0.5)
    serve_delay = 0.55
    if player_score >= SCORE_LIMIT or bot_score >= SCORE_LIMIT:
        player_score = 0
        bot_score = 0
        print("GODOT_PS5_PONG_MATCH_COMPLETE")

func _draw_digit(pos: Vector2, number: int, tint: Color) -> void:
    # Tiny 7-segment vector score. No font APIs; renderer draw_rect only.
    var bits: int = SEGMENTS[clampi(number, 0, 9)]
    var slots := [
        Rect2(12, 0, 49, 9), Rect2(61, 11, 9, 46),
        Rect2(61, 66, 9, 46), Rect2(12, 112, 49, 9),
        Rect2(0, 66, 9, 46), Rect2(0, 11, 9, 46),
        Rect2(12, 56, 49, 9)]
    for segment in range(7):
        if (bits & (1 << segment)) != 0:
            var rect: Rect2 = slots[segment]
            draw_rect(Rect2(rect.position + pos, rect.size), tint, true)

func _draw() -> void:
    draw_rect(Rect2(0, 0, WIDTH, HEIGHT), SKY, true)
    # Simple real Godot CanvasItem lines, circles, rectangles, transparency.
    for x in range(0, 1920, 120):
        draw_line(Vector2(x, 75), Vector2(x, HEIGHT - 75),
                  Color(0.15, 0.24, 0.37, 0.23), 1.0)
    for y in range(75, 1000, 120):
        draw_line(Vector2(0, y), Vector2(WIDTH, y),
                  Color(0.15, 0.24, 0.37, 0.23), 1.0)
    draw_rect(Rect2(20, 55, WIDTH - 40, HEIGHT - 110),
              Color(0.13, 0.33, 0.54, 0.9), false, 3.0)
    for y in range(88, 985, 42):
        draw_rect(Rect2(WIDTH * 0.5 - 3.0, y, 6, 24),
                  Color(0.46, 0.6, 0.8, 0.55), true)

    draw_rect(Rect2(PLAYER_X - PADDLE_W * 0.5 - 8,
                    player_y - PADDLE_H * 0.5 - 8,
                    PADDLE_W + 16, PADDLE_H + 16),
              Color(0.0, 0.55, 0.75, 0.2), true)
    draw_rect(Rect2(PLAYER_X - PADDLE_W * 0.5,
                    player_y - PADDLE_H * 0.5,
                    PADDLE_W, PADDLE_H), CYAN, true)
    draw_rect(Rect2(BOT_X - PADDLE_W * 0.5,
                    bot_y - PADDLE_H * 0.5,
                    PADDLE_W, PADDLE_H), MAGENTA, true)
    draw_circle(ball_pos, BALL_R + 12.0, Color(0.96, 0.8, 0.18, 0.13))
    draw_circle(ball_pos, BALL_R, Color(1.0, 0.9, 0.45))

    _draw_digit(Vector2(750, 112), player_score, CYAN)
    _draw_digit(Vector2(1102, 112), bot_score, MAGENTA)

    # Distinct controller legend in PS5-colored shape icons, zero fonts.
    draw_rect(Rect2(740, HEIGHT - 45, 450, 6), Color(0.08, 0.28, 0.38), true)
    draw_rect(Rect2(740, HEIGHT - 45, clampf(play_time / TIME_LIMIT, 0.0, 1.0) * 450, 6), CYAN, true)
    if not playing:
        draw_circle(Vector2(WIDTH * 0.5, HEIGHT * 0.5), 53.0,
                    Color(0.02, 0.08, 0.2, 0.56))
        draw_circle(Vector2(WIDTH * 0.5, HEIGHT * 0.5), 27.0,
                    Color(0.14, 0.83, 1.0, 0.6))
