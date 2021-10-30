import random
import pygame

print("Not legit Tetris plz dont sue me")

pygame.init()
FONT = pygame.font.SysFont('calibri', 24)

pygame.mixer.init()
pygame.mixer.music.load("Tetris 99 - Main Theme.wav")
pygame.mixer.music.set_volume(0.10)
pygame.mixer.music.play(-1)

# Game size and display constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
WINDOW_SIZE = BLOCK_SIZE * GRID_HEIGHT
GRID_OFFSET = WINDOW_SIZE // 4
GRIDLINE_THICKNESS = 2
DISPLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE
DISPLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# Game texts displayed in the right of the display
TEXT_NEXT_PIECE_DISPLAY_POSITION = (
	int(15 * BLOCK_SIZE + BLOCK_SIZE // (3/2)), BLOCK_SIZE)
NEXT_PIECE_DISPLAY_POSITION = (
	int((WINDOW_SIZE // BLOCK_SIZE - 2)), int((WINDOW_SIZE // BLOCK_SIZE) // 4))

# Games texts displayed in the left of the display
TEXT_HELD_PIECE_DISPLAY_POSITION = (BLOCK_SIZE // (3/2), BLOCK_SIZE)
HELD_PIECE_DISPLAY_POSITION = (3, int((WINDOW_SIZE // BLOCK_SIZE) // 4))
TEXT_SCORE_DISPLAY_POSITION = (int(1.5 * BLOCK_SIZE), 6 * BLOCK_SIZE)
SCORE_DISPLAY_POSITION = (BLOCK_SIZE, 7 * BLOCK_SIZE)
SCORE_MAX_LEN = 8

TEXT_LEVEL_DISPLAY_POSITION = (int(1.5 * BLOCK_SIZE), 9 * BLOCK_SIZE)
LEVEL_DISPLAY_POSITION = (2 * BLOCK_SIZE, 10 * BLOCK_SIZE)
LEVEL_MAX_LEN = 2

TEXT_LINES_DISPLAY_POSITION = (int(1.5 * BLOCK_SIZE), 12 * BLOCK_SIZE)
LINES_DISPLAY_POSITION = (int(1.25 * BLOCK_SIZE), 13 * BLOCK_SIZE)
LINES_MAX_LEN = 6

# Game constants
EMPTY_BLOCK_SIGN = '*'
FORMAT_SIGN = '@'
TYPES = ['o', 's', 'z', 'j', 'l', 'i', 't']
LEVEL_FALL_SPEED = [800, 720, 630, 550, 470, 380, 300,
					250, 220, 200, 180, 165, 150, 130, 110]  # Miliseconds

# Colors in RGB representation
BLACK = (0, 0, 0)
GRAY = (64, 64, 64)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 51)
GREEN = (114, 242, 59)
BLUE = (3, 65, 174)
ORANGE = (255, 151, 28)
RED = (255, 50, 19)
CYAN = (0, 255, 255)
PURPLE = (130, 43, 226)
COLORS = {'o': YELLOW, 's': GREEN, 'z': RED,
	'j': BLUE, 'l': ORANGE, 'i': CYAN, 't': PURPLE}

# Game varriables
wait_time_after_set = 0
hold_twice = False
hold = False
held_piece_type = ''
score = 0
lines_cleared_total = 0
level = 0
lost = False
QUIT = False
grid = [[EMPTY_BLOCK_SIGN for i in range(
	GRID_WIDTH)] for j in range(GRID_HEIGHT)]

tetris_display = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Tetris!")

shuffled_types = TYPES[:]  # creating a copy
random.shuffle(shuffled_types)


SHAPES = {
	's': [['.@@',
		   '@@.',
		   '...'],
		  ['.@.',
		   '.@@',
		   '..@', ],
		  ['...',
		   '.@@',
		   '@@.', ],
		  ['@..',
		   '@@.',
		   '.@.', ]],

	'z': [['@@.',
		   '.@@',
		   '...'],
		  ['..@',
		   '.@@',
		   '.@.', ],
		  ['...',
		   '@@.',
		   '.@@', ],
		  ['.@.',
		   '@@.',
		   '@..', ]],

	'i': [['....',
		   '@@@@',
		   '....',
		   '....'],
		  ['..@.',
		   '..@.',
		   '..@.',
		   '..@.'],
		  ['....',
		   '....',
		   '@@@@',
		   '....'],
		  ['.@..',
		   '.@..',
		   '.@..',
		   '.@..']],

	'o': [['....',
		   '.@@.',
		   '.@@.',
		   '....']],

	'j': [['@..',
		   '@@@',
		   '...', ],
		  ['.@@',
		   '.@.',
		   '.@.', ],
		  ['...',
		   '@@@',
		   '..@', ],
		  ['.@.',
		   '.@.',
		   '@@.', ]],

	'l': [['..@',
		   '@@@',
		   '...', ],
		  ['.@.',
		   '.@.',
		   '.@@', ],
		  ['...',
		   '@@@',
		   '@..', ],
		  ['@@.',
		   '.@.',
		   '.@.', ]],

	't': [['.@.',
		   '@@@',
		   '...', ],
		  ['.@.',
		   '.@@',
		   '.@.', ],
		  ['...',
		   '@@@',
		   '.@.', ],
		  ['.@.',
		   '@@.',
		   '.@.', ]],
}


class Piece():
	def __init__(self, type, x, y):
		self.type = type
		self.x = x * BLOCK_SIZE
		self.y = y * BLOCK_SIZE
		self.orientation = 0
		self.shape = SHAPES[self.type]
		self.positions = []

	# Check if a piece (all of its blocks) are in vlalid positions in the grid and not touching other pieces
	def valid_positions(self, grid):
		self.format_to_shape()

		valid_positions = [
							[[BLOCK_SIZE * j, BLOCK_SIZE * i] for j in range(GRID_WIDTH) if grid[i][j] == EMPTY_BLOCK_SIGN] for i in range(GRID_HEIGHT)
					]

		# Convert the 2d list into 1d list
		valid_positions = [j for sub in valid_positions for j in sub]

		# Checking valid positions when the piece is in the game display
		for position in self.positions:
			if position not in valid_positions and position[1] > -1:
				return False
		# Check that the piece still bounded by the game display even when its off screen (above)
			elif position[1] <= -1:
				if position[0] < 0 or position[0] >= DISPLAY_WIDTH:
						return False

		return True

	# Only checking if a piece in the bound of the display	
	def in_bound(self, axis):
		self.format_to_shape()
		if axis == 'x':
			for position in self.positions:
				if position[0] < 0 or position[0] >= DISPLAY_WIDTH:
					return False
			return True

		elif axis == 'y':
			for position in self.positions:
				if position[1] >= DISPLAY_HEIGHT:
					return False
			return True

	# Move the piece down, left, right
	def move_piece(self):

		keys_pressed = pygame.key.get_pressed()

		if keys_pressed [pygame.K_LEFT]:
			self.x -= BLOCK_SIZE

			if not self.valid_positions(grid):
				self.x += BLOCK_SIZE

		elif keys_pressed[pygame.K_RIGHT]:
			self.x += BLOCK_SIZE

			if not self.valid_positions(grid):
				self.x -= BLOCK_SIZE
		
		elif keys_pressed[pygame.K_DOWN]:
			self.y += BLOCK_SIZE
			wait_time_after_set = LEVEL_FALL_SPEED[level] if level < len (LEVEL_FALL_SPEED) else LEVEL_FALL_SPEED[-1]
			if not self.valid_positions (grid):
				self.y -= BLOCK_SIZE

	# Rotating the Piece
	def rotate(self):

			original_x = self.x
			original_y = self.y
			self.orientation += 1
			self.orientation = self.orientation % len(
						SHAPES[self.type]) # Modulo of the number of possible orientations of given peice type i.e i 2 and 't'
			self.format_to_shape()
					
			# Fixing the Piece position if it escapes the display boundries because of the rotation
			while not self.in_bound('x'):
					if self.x <= DISPLAY_WIDTH // 2: # Checking wether the piece is besides the Left or right wall
						self.x += BLOCK_SIZE
					else:
						self.x -= BLOCK_SIZE
								
			while not self.in_bound('y'):
								
					self.y -= BLOCK_SIZE
					
			# Checking wether the touches another piece i.e we cant preforme the rotation and need to revert back.
			if not self.valid_positions (grid):
					self.x = original_x
					self.y = original_y
					self.orientation -= 1
					self.orientation = self.orientation % len(SHAPES[self.type])
					self.format_to_shape()
	
	# Dropping the piece down as far as it can go
	def drop_piece(self):
		# Moving the piece down until its in an invalid position
		while self.valid_positions(grid):
			self.y += BLOCK_SIZE
		# Bringing the piece one BLOCK_SIZE up to be in the lowerst valid position (aka where you want to drop the piece)
		self.y -= BLOCK_SIZE

	def auto_fall(self):
		self.y += BLOCK_SIZE
		if not self.valid_positions(grid):
			self.y -= BLOCK_SIZE

	def is_set(self, grid):
		for position in self.positions:
			# Continuing if the block position is more than 2 BLOCK_SIZE over the grid
			if position[1] < - BLOCK_SIZE:
				continue
			# Collision with floor
			elif position[1] + BLOCK_SIZE >= DISPLAY_HEIGHT:
				return True
			# Coilision with other pieces
			elif grid[position[1] // BLOCK_SIZE + 1][position[0] // BLOCK_SIZE] != EMPTY_BLOCK_SIGN:
				return True
		return False

	def format_to_shape(self):
		self.positions = []
		shape_format = self.shape[self.orientation]

		for i in range(len(shape_format)):
			for j in range(len(shape_format[i])):
				if shape_format[i][j] == FORMAT_SIGN:
					self.positions.append([self.x + (j - 2) * BLOCK_SIZE, self.y + (i - 2) * BLOCK_SIZE])
	
	def draw_piece(self, display, offset=0, fill=0):
		for position in self.positions:
			pygame.draw.rect(display, COLORS[self.type], (
			position[0] + offset + GRIDLINE_THICKNESS, position[1] + GRIDLINE_THICKNESS, BLOCK_SIZE - GRIDLINE_THICKNESS,
			BLOCK_SIZE - GRIDLINE_THICKNESS), fill)

def draw_grid(grid):
	for i in range(len(grid)):
		for j in range(len(grid[0])):
			if grid[i][j] != EMPTY_BLOCK_SIGN:
				block_color = grid[i][j]
				pygame.draw.rect(tetris_display, block_color, (
					j * BLOCK_SIZE + GRID_OFFSET + GRIDLINE_THICKNESS,
					i * BLOCK_SIZE + GRIDLINE_THICKNESS, BLOCK_SIZE - GRIDLINE_THICKNESS,
					BLOCK_SIZE - GRIDLINE_THICKNESS))

def draw_gridlines():
	for i in range(0, DISPLAY_HEIGHT, BLOCK_SIZE):
		start_point = (GRID_OFFSET, i)
		end_point = (GRID_OFFSET + DISPLAY_WIDTH, i)
		pygame.draw.line(tetris_display, GRAY, start_point, end_point, GRIDLINE_THICKNESS)

	for i in range(0, DISPLAY_WIDTH + BLOCK_SIZE, BLOCK_SIZE):
		start_point = (GRID_OFFSET + i, 0)
		end_point = (GRID_OFFSET + i, DISPLAY_HEIGHT)
		pygame.draw.line(tetris_display, GRAY, start_point, end_point, GRIDLINE_THICKNESS)

def calc_score(old_score, new_cleared_lines):
	scores = [0, 40, 100, 300, 1200]
	new_score = old_score + scores[new_cleared_lines] * (level + 1)
	return new_score

def clear_lines(grid):
	lines_cleared = 0
	new_grid = []
	empty_row = ['*' for _ in range(GRID_WIDTH)]

	for row in grid:
		# Adding all the non cleared lines to the new grid
		if EMPTY_BLOCK_SIGN in row:
			new_grid.append(row)
		# Adding empy rows in the beggining of the grid inplace of the cleared lines
		else:
			# We use empty_row[:] to create a new copy of that list. if we didnt use [:]
			# when we would change empty_row it would change every instace of it like in the new grid
			new_grid.insert(0, empty_row[:])
			lines_cleared += 1
	return new_grid, lines_cleared


def draw_text(text, screen, font, pos):
	text_img = font.render(text, True, WHITE)
	screen.blit(text_img, pos)
	return

def pause():
	pause_text_position = ((DISPLAY_WIDTH - 1 * BLOCK_SIZE) // 2, (DISPLAY_HEIGHT - 7 * BLOCK_SIZE) // 2)
	font = pygame.font.SysFont('calibri', 20)
	pygame.mixer.music.pause()
	paused = True
	while paused:
		draw_text("Game paused... Press P again to unpause", tetris_display, font, pause_text_position)
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			elif event.type == pygame.KEYDOWN:
				keys_pressed = pygame.key.get_pressed()
				if keys_pressed[pygame.K_p]:
					pygame.mixer.music.unpause()
					paused = False

	return


while not QUIT:

	clock = pygame.time.Clock()
	# Setting an event for the piece to fall 1 block every *fall_speed* miliseconds
	AUTO_FALL = pygame.USEREVENT + 1
	fall_speed = LEVEL_FALL_SPEED[level] if level < len(LEVEL_FALL_SPEED) else LEVEL_FALL_SPEED[-1]
	pygame.time.set_timer(AUTO_FALL, fall_speed)

	time_passed = 0
	wait_time_over = False
	# Creating new piece
	if len(shuffled_types) == 1:
		last_item = shuffled_types[-1]
		shuffled_types = TYPES[:]
		random.shuffle(shuffled_types)
		shuffled_types.insert(0, last_item)
	piece_type = shuffled_types.pop(0)

	# Spawning new random Tetronimo in the top middle of the screen
	current_piece = Piece(piece_type, (DISPLAY_WIDTH // 2) // BLOCK_SIZE - 1, 0)

	# Player can move the new piece until its set
	while not (current_piece.is_set(grid) and wait_time_over):
		# Setting a delay if a piece was set by AUTO_FALL or user pressing K_DOWN (any case execpt drop/space)
		# to let the player manuver the piece a little bit
		if current_piece.is_set(grid):
			time_passed += clock.get_time()
			if time_passed >= wait_time_after_set:
				wait_time_over = True
				time_passed = 0
		# Event Handeler
		for event in pygame.event.get():
			# Quits if the player presses on the X of the window
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			# Dropping the piece 1 block every *fall_speed* miliseconds
			if event.type == AUTO_FALL:
				current_piece.auto_fall()
				wait_time_after_set = LEVEL_FALL_SPEED[level] if level < len(LEVEL_FALL_SPEED) else LEVEL_FALL_SPEED[-1]
			# Handling rotation and dropping the Piece. because we want the play not be able to hold
			# the key down for rotation and dropping, we gotta have the pygame.KEYDOWN event
			if event.type == pygame.KEYDOWN:
				keys_pressed = pygame.key.get_pressed()

				if keys_pressed[pygame.K_UP]:
					current_piece.rotate()
				elif keys_pressed[pygame.K_SPACE]:
					current_piece.drop_piece()
					wait_time_over = True
				elif keys_pressed[pygame.K_p]:
					pause()
				elif keys_pressed[pygame.K_c]:
					if hold_twice == False: #After pressing 'hold' the player can't press hold again until he places some piece.
						held_piece = Piece(current_piece.type, HELD_PIECE_DISPLAY_POSITION[0], HELD_PIECE_DISPLAY_POSITION[1])
						if held_piece_type == '': # if its the first time the player presses hold
							if len(shuffled_types) == 1:
								last_item= shuffled_types[-1]
								shuffled_types = TYPES[:]
								random.shuffle(shuffled_types)
								shuffled_types.insert(0, last_item)
							current_piece = Piece(shuffled_types.pop(0), (DISPLAY_WIDTH // 2) // BLOCK_SIZE-1, 0)
						else:
							current_piece = Piece(held_piece_type, (DISPLAY_WIDTH // 2) // BLOCK_SIZE - 1, 0)
						held_piece_type = held_piece.type
						hold_twice = True
 
		#Creating the Next piece and Shadow piece instances
		next_peice = Piece(shuffled_types [0], NEXT_PIECE_DISPLAY_POSITION [0], NEXT_PIECE_DISPLAY_POSITION[1])
		shadow_piece = Piece(current_piece.type, current_piece.x, current_piece.y)
		
		current_piece.move_piece()
		current_piece.format_to_shape()
		shadow_piece.x = current_piece.x
		shadow_piece.y = current_piece.y
		shadow_piece.orientation = current_piece.orientation
		shadow_piece.drop_piece()
		shadow_piece.format_to_shape()
		
		tetris_display.fill(BLACK)
		
		# Drawing texts for the game:
		draw_text('NEXT PIECE', tetris_display, FONT, TEXT_NEXT_PIECE_DISPLAY_POSITION)
		draw_text('HELD PIECE', tetris_display, FONT, TEXT_HELD_PIECE_DISPLAY_POSITION)

		draw_text('SCORE', tetris_display, FONT, TEXT_SCORE_DISPLAY_POSITION)
		score_formatted = (SCORE_MAX_LEN - len(str(score))) * '0' + str(score) if len(str(score)) <= SCORE_MAX_LEN else '9' * SCORE_MAX_LEN
		draw_text(score_formatted, tetris_display, FONT, SCORE_DISPLAY_POSITION)
		
		draw_text('LEVEL', tetris_display, FONT, TEXT_LEVEL_DISPLAY_POSITION)
		level_formatted = (LEVEL_MAX_LEN - len(str(level))) * '0' + str(level) if len(str(level)) <= SCORE_MAX_LEN else '9' * LEVEL_MAX_LEN
		draw_text(level_formatted, tetris_display, FONT, LEVEL_DISPLAY_POSITION)
		
		draw_text('LINES', tetris_display, FONT, TEXT_LINES_DISPLAY_POSITION)
		cleared_lines_formatted = (LINES_MAX_LEN - len(str(lines_cleared_total))) * '0' + str(lines_cleared_total) if len(str(lines_cleared_total)) <= LINES_MAX_LEN else '9' * LINES_MAX_LEN
		draw_text(cleared_lines_formatted, tetris_display, FONT, LINES_DISPLAY_POSITION)
		
		# Displaying what the next piece will be
		next_peice.format_to_shape()
		next_peice.draw_piece(tetris_display)
		# Drawing the piece (we use the GRIDLINE OFFSET in order for the piece to fit mirly inside the drawn grid)
		current_piece.draw_piece(tetris_display, GRID_OFFSET)
		# Drawing the shadow of the piece (where it will drop), we use GRIDLINE__THICKNESS so the piece would be hollow
		shadow_piece.draw_piece(tetris_display, GRID_OFFSET, GRIDLINE_THICKNESS)
		
		if held_piece_type != '':
			held_piece.format_to_shape()
			held_piece.draw_piece(tetris_display)
		
		# Drawing the grid
		draw_grid(grid)
		#Drawing the grid Lines
		draw_gridlines()
		pygame.display.update()
		clock.tick(14)
	# The player placed a piece therefore he can now press hold again.
	hold_twice = False
 
	# Check if u lost?
	for position in current_piece.positions:
		if position [1] < 0:
			exit()
 
	#Adding piece to the grid after its been set
	for position in current_piece.positions:
		grid[position [1] // BLOCK_SIZE][position [0] // BLOCK_SIZE] = COLORS[current_piece.type]
	
	# Clearing finished Lines
	grid, lines_cleared = clear_lines (grid)
	lines_cleared_total += lines_cleared
	score = calc_score(score, lines_cleared)
	if lines_cleared_total // 10 > level:
		level += 1