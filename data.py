from matplotlib.figure import Figure

LARGE_FONT = ('Roboto', 12, 'bold')
sim_running = bool

# Dimensions
# Left upper tank:
LU_LENGTH = 7
LU_WIDTH = 5
LU_HEIGHT = 5

# Right upper tank:
RU_LENGTH = 15
RU_WIDTH = 7
RU_HEIGHT = 5

# Bottom tank:
B_LENGTH = 23
B_WIDTH = 18
B_HEIGHT = 10

Q = 300

fig = Figure(figsize=(5, 5), dpi=100)
sub = fig.add_subplot(111)
