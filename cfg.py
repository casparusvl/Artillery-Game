hres = 1280
vres = 720
tickrate = 120
gravity = -9.81
input_scale = 700 / hres
time_scale = hres / 200



screen_color = (0, 0, 0)
ground_color = (255, 0, 0)
projectile_color = (25, 25, 25)

crater_color = (255, 240, 0)
blastsize = 27
# menu
name = ''

# State counters setup
state = {'menu' : 1, 'title_menu' : 1, 'main_menu' : 0,
    'pause_menu': 0, 'end_menu' : 0, 'gameplay' : 0}

init_new = True
hit = p1_hit = p2_hit = False
reset_score = False
main_count = 0
turn = 0

# field generator setup
minsamples = 5
iterations = 4

# Player generator setup
default_color = ((0, 0, 255), (86, 130, 3),(255, 0, 0))
p1color = (0, 0, 255)
p2color = (86, 130, 0)
player_list = []


# Setup fps counter
frame_count = 0
frame_time_count = 0
frame_time_avg = '0'
fps_avg = '0'
update_interval = tickrate // 2


