import pygame
import sys
import os
import math
import random
import datetime
from pygame.locals import *

class OneDayApp:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Get display info for default window size
        display_info = pygame.display.Info()
        
        # Window size options
        self.window_size_options = [
            (800, 240),   # Small
            (1200, 240),  # Medium
            (display_info.current_w, 240),  # Full width
            (1600, 300),  # Large
            (1920, 360),  # Extra Large
        ]
        self.selected_window_size_index = 2  # Default to full width
        
        # Game constants
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = self.window_size_options[self.selected_window_size_index]
        self.FPS = 30
        self.DEFAULT_WALK_DURATION = 60  # Default seconds
        self.walk_duration = self.DEFAULT_WALK_DURATION  # Can be changed by user
        self.MAX_WALK_DURATION = 1800  # 30 minutes max
        
        # Initialize window-dependent variables
        self.update_window_dependent_variables()
        
        print(f"Window size: {self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}, Bench position: {self.bench_x}")
        
        # Get current date and time
        self.current_datetime = datetime.datetime.now()
        self.hour = self.current_datetime.hour
        self.month = self.current_datetime.month
        
        # Determine time of day and season
        self.time_of_day = self.get_time_of_day()
        self.season = self.get_season()
        
        # Colors based on time of day
        self.colors = self.get_colors_for_time()
        
        # Set up the window with resizable flag
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(f"One Day - {self.time_of_day} {self.season}")
        self.clock = pygame.time.Clock()
        
        # UI elements - Time input system
        self.min_duration = 180  # 3 minutes minimum
        self.max_duration = 3600 # 60 minutes maximum
        self.input_duration = 180 # Default 3 minutes in seconds
        self.duration_input_text = "3"  # Display text (in minutes)
        self.is_inputting = False
        self.input_active = False
        
        # Load assets
        self.load_assets()
        
        # Character variables
        self.character_x = -self.character_frames[0].get_width()  # Start off-screen
        self.character_y = self.bench_y - 30  # Same level as bench
        self.walk_speed = 0  # Will be calculated when game starts
        self.current_frame = 0
        self.animation_speed = 8  # Frames before changing animation
        
        # Sea movement
        self.sea_offset = 0
        
        # Game state
        self.game_started = False
        self.game_finished = False
        self.start_time = 0
        self.elapsed_time = 0
        self.in_menu = True
        self.current_phase = 1  # 1: walk to bench, 2: rest, 3: walk to end
        
        # Room to walk transition system
        self.transition_phase = "room"  # room -> standing -> walking -> window -> game
        self.transition_progress = 0.0
        self.transition_duration = 8.0  # 8 seconds total (increased from 6)
        self.transition_start_time = 0  # Track actual start time
        self.camera_x = 0
        self.camera_y = 0
        self.walking_bob = 0  # Walking up/down movement
        self.window_scale = 0.3  # Initial window size in room
        self.last_transition_time = 0  # Initialize transition timer
        
        # Font setup - use system font that supports Japanese
        self.setup_fonts()
        
        # Initialize particles
        self.particles = []
        self.seasonal_objects = []
    
    def update_window_dependent_variables(self):
        """Update variables that depend on window size"""
        # Bench position for resting
        self.bench_x = self.WINDOW_WIDTH // 2
        self.bench_y = self.WINDOW_HEIGHT - 50
        
        # Character Y position - always on the ground level (same as bench)
        self.character_y = self.bench_y - 30  # Slightly above ground to align with bench
        
        # Resting state variables
        self.is_resting = False
        self.rest_start_time = 0
        self.rest_duration = 0
        
        # Resting activities
        self.current_activity = "sitting"  # Current activity while resting
        self.activity_start_time = 0
        self.activity_duration = 0
        self.looking_up = False
        self.look_up_timer = 0
    
    def setup_fonts(self):
        """Setup fonts with Japanese support"""
        # Try to find a font that supports Japanese
        font_candidates = [
            "Arial Unicode MS",
            "Hiragino Sans GB",
            "Hiragino Kaku Gothic Pro",
            "MS Gothic",
            "Yu Gothic",
            "Meiryo",
            "AppleGothic",
            "Osaka",
            "Arial"
        ]
        
        # Try each font until one works
        for font_name in font_candidates:
            try:
                self.font_small = pygame.font.SysFont(font_name, 36)
                self.font_large = pygame.font.SysFont(font_name, 48)
                print(f"Using font: {font_name}")
                return
            except:
                continue
        
        # If no font works, use default
        print("No suitable font found, using default")
        self.font_small = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        
    def change_window_size(self, new_size_index):
        """Change window size and regenerate assets"""
        if new_size_index != self.selected_window_size_index:
            self.selected_window_size_index = new_size_index
            old_width, old_height = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
            
            # Update window dimensions
            self.WINDOW_WIDTH, self.WINDOW_HEIGHT = self.window_size_options[new_size_index]
            
            # Update window-dependent variables
            self.update_window_dependent_variables()
            
            # Recreate the window
            self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            pygame.display.set_caption(f"One Day - {self.time_of_day} {self.season} ({self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT})")
            
            # Regenerate assets that depend on window size
            self.clouds = self.create_clouds()
            self.sea = self.create_sea()
            self.path = self.create_path()
            self.seasonal_objects = []
            self.create_seasonal_objects()
            
            # Adjust character position proportionally if game is running
            if self.game_started and not self.game_finished:
                # Scale character position proportionally
                position_ratio = self.character_x / old_width if old_width > 0 else 0
                self.character_x = position_ratio * self.WINDOW_WIDTH
                
                # Recalculate walk speeds based on current phase
                if self.current_phase == 1:
                    # Phase 1: Recalculate speed to bench
                    distance_to_bench = self.bench_x - self.character_x
                    remaining_time = 60 - self.elapsed_time
                    if remaining_time > 0:
                        self.walk_speed = distance_to_bench / (remaining_time * self.FPS)
                elif self.current_phase == 3:
                    # Phase 3: Recalculate speed to end
                    remaining_distance = self.WINDOW_WIDTH - self.character_x
                    remaining_time = self.walk_duration - self.elapsed_time
                    if remaining_time > 0:
                        self.walk_speed = remaining_distance / (remaining_time * self.FPS)
            
    def handle_window_resize(self, new_width, new_height):
        """Handle window resize event and adjust game accordingly"""
        # Minimum size constraints
        min_width, min_height = 600, 200
        new_width = max(new_width, min_width)
        new_height = max(new_height, min_height)
        
        # Store old dimensions for proportional scaling
        old_width, old_height = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        
        # Update window dimensions
        self.WINDOW_WIDTH = new_width
        self.WINDOW_HEIGHT = new_height
        
        # Update window-dependent variables
        self.update_window_dependent_variables()
        
        # Recreate the screen surface
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(f"One Day - {self.time_of_day} {self.season} ({self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT})")
        
        # Regenerate assets that depend on window size
        self.regenerate_assets()
        
        # Adjust character position and speed if game is running
        if self.game_started and not self.game_finished:
            self.adjust_game_state_for_resize(old_width, old_height)
        
        print(f"Window resized to: {self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}, New bench position: {self.bench_x}")
    
    def regenerate_assets(self):
        """Regenerate assets that depend on window size"""
        self.clouds = self.create_clouds()
        self.sea = self.create_sea()
        self.path = self.create_path()
        
        # Regenerate seasonal objects with new positions
        self.seasonal_objects = []
        self.create_seasonal_objects()
    
    def adjust_game_state_for_resize(self, old_width, old_height):
        """Adjust game state when window is resized during gameplay"""
        if old_width <= 0:  # Avoid division by zero
            return
            
        # Scale character position proportionally
        position_ratio = self.character_x / old_width
        self.character_x = position_ratio * self.WINDOW_WIDTH
        
        # Recalculate walk speeds based on current phase
        if self.current_phase == 1:
            # Phase 1: Recalculate speed to reach bench in remaining time
            remaining_time = max(60 - self.elapsed_time, 1)  # At least 1 second
            distance_to_bench = self.bench_x - self.character_x
            self.walk_speed = distance_to_bench / (remaining_time * self.FPS)
            print(f"Phase 1 speed adjusted: {self.walk_speed:.4f} px/frame, {remaining_time:.1f}s to bench")
            
        elif self.current_phase == 3:
            # Phase 3: Recalculate speed to reach end in remaining time
            remaining_time = max(self.walk_duration - self.elapsed_time, 1)  # At least 1 second
            remaining_distance = self.WINDOW_WIDTH - self.character_x
            self.walk_speed = remaining_distance / (remaining_time * self.FPS)
            print(f"Phase 3 speed adjusted: {self.walk_speed:.4f} px/frame, {remaining_time:.1f}s to end")
        
        # If character is resting, just update position to bench
        if self.is_resting:
            self.character_x = self.bench_x
    
    def get_resting_activities(self):
        """Get list of possible activities while resting on bench"""
        activities = [
            {"name": "looking_up", "duration": 3, "description": "Looking up at the sky"},
            {"name": "stretching", "duration": 2, "description": "Stretching arms"},
            {"name": "petting_dog", "duration": 4, "description": "Petting the dog"},
            {"name": "checking_phone", "duration": 5, "description": "Checking phone"},
            {"name": "drinking_water", "duration": 3, "description": "Drinking water"},
            {"name": "deep_breathing", "duration": 4, "description": "Taking deep breaths"},
            {"name": "watching_scenery", "duration": 6, "description": "Watching the scenery"},
            {"name": "adjusting_clothes", "duration": 2, "description": "Adjusting clothes"},
        ]
        return activities
    
    def start_random_activity(self, current_time):
        """Start a random resting activity"""
        activities = self.get_resting_activities()
        activity = random.choice(activities)
        
        self.current_activity = activity["name"]
        self.activity_start_time = current_time
        self.activity_duration = activity["duration"]
        
        print(f"🎭 Started activity: {activity['description']} (for {activity['duration']}s)")
        
        # Set specific flags for activities
        if self.current_activity == "looking_up":
            self.looking_up = True
            self.look_up_timer = current_time
    
    def update_resting_activities(self, current_time):
        """Update current resting activity"""
        if not self.is_resting:
            return
            
        activity_elapsed = (current_time - self.activity_start_time) / 1000
        
        # Check if current activity is finished
        if activity_elapsed >= self.activity_duration:
            # End current activity
            if self.current_activity == "looking_up":
                self.looking_up = False
            
            # Start new activity with some probability
            if random.random() < 0.3:  # 30% chance to start new activity
                self.start_random_activity(current_time)
            else:
                # Just sit normally
                self.current_activity = "sitting"
                self.activity_start_time = current_time
                self.activity_duration = random.randint(5, 15)  # Sit normally for 5-15 seconds
    
    
    
    def get_time_of_day(self):
        """Determine time of day based on current hour"""
        hour = self.hour
        if 5 <= hour < 10:
            return "Morning"  # Morning
        elif 10 <= hour < 16:
            return "Day"  # Day
        elif 16 <= hour < 19:
            return "Evening"  # Evening
        else:
            return "Night"  # Night
    
    def get_season(self):
        """Determine season based on current month"""
        month = self.month
        if 3 <= month <= 5:
            return "Spring"  # Spring
        elif 6 <= month <= 8:
            return "Summer"  # Summer
        elif 9 <= month <= 11:
            return "Autumn"  # Autumn
        else:
            return "Winter"  # Winter
    
    def get_colors_for_time(self):
        """Get color palette based on time of day"""
        colors = {}
        
        # Sky colors based on time of day
        if self.time_of_day == "Morning":  # Morning
            colors["sky_top"] = (135, 206, 250)  # Light sky blue
            colors["sky_bottom"] = (255, 200, 150)  # Light orange/pink
            colors["cloud"] = (255, 240, 240)  # Pinkish white
        elif self.time_of_day == "Day":  # Day
            colors["sky_top"] = (0, 150, 255)  # Deep blue
            colors["sky_bottom"] = (135, 206, 235)  # Sky blue
            colors["cloud"] = (255, 255, 255)  # White
        elif self.time_of_day == "Evening":  # Evening
            colors["sky_top"] = (70, 100, 150)  # Darker blue
            colors["sky_bottom"] = (255, 140, 100)  # Orange
            colors["cloud"] = (255, 200, 150)  # Orange-tinted
        else:  # Night
            colors["sky_top"] = (10, 10, 50)  # Dark blue
            colors["sky_bottom"] = (50, 50, 100)  # Slightly lighter blue
            colors["cloud"] = (150, 150, 200)  # Dark clouds
        
        # Ground colors based on season
        if self.season == "Spring":  # Spring
            colors["grass"] = (120, 220, 100)  # Bright green
            colors["path"] = (200, 180, 140)  # Light brown
        elif self.season == "Summer":  # Summer
            colors["grass"] = (100, 200, 80)  # Deep green
            colors["path"] = (210, 190, 150)  # Lighter brown (dry)
        elif self.season == "Autumn":  # Autumn
            colors["grass"] = (180, 160, 80)  # Yellowish green
            colors["path"] = (190, 170, 130)  # Darker brown
        else:  # Winter
            colors["grass"] = (220, 220, 240)  # White-blue (snow)
            colors["path"] = (200, 200, 210)  # Light gray
        
        return colors
        
    def load_assets(self):
        """Load or create game assets"""
        # Character animation frames
        self.character_frames = self.create_character_frames()
        
        # Background elements
        self.clouds = self.create_clouds()
        self.sea = self.create_sea()
        self.path = self.create_path()
        
        # Create bench for resting
        self.bench = self.create_bench()
        
        # Create seasonal objects
        self.create_seasonal_objects()
        
        # Create celestial objects (sun/moon)
        self.celestial_object = self.create_celestial_object()
    
    def create_character_frames(self):
        """Create simple pixel art character frames for walking animation with dog"""
        frames = []
        
        # Colors based on season (clothing changes with season)
        if self.season == "Spring":  # Spring
            body_color = (255, 150, 150)  # Light red
            head_color = (255, 200, 150)  # Skin tone
            leg_color = (100, 100, 255)  # Blue
            dog_color = (240, 220, 180)  # Light brown dog
        elif self.season == "Summer":  # Summer
            body_color = (255, 255, 150)  # Yellow
            head_color = (255, 200, 150)  # Skin tone
            leg_color = (100, 200, 100)  # Green
            dog_color = (240, 220, 180)  # Light brown dog
        elif self.season == "Autumn":  # Autumn
            body_color = (200, 100, 50)  # Brown
            head_color = (255, 200, 150)  # Skin tone
            leg_color = (150, 100, 50)  # Dark brown
            dog_color = (200, 180, 150)  # Darker brown dog
        else:  # Winter
            body_color = (200, 200, 255)  # Light blue
            head_color = (255, 200, 150)  # Skin tone
            leg_color = (50, 50, 150)  # Dark blue
            dog_color = (240, 240, 240)  # White dog (winter coat)
        
        # Frame 1 - Standing
        char1 = pygame.Surface((64, 64), pygame.SRCALPHA)
        # Body
        pygame.draw.rect(char1, body_color, (16, 16, 16, 24))
        # Head
        pygame.draw.rect(char1, head_color, (16, 4, 16, 16))
        # Legs
        pygame.draw.rect(char1, leg_color, (16, 40, 8, 16))
        pygame.draw.rect(char1, leg_color, (24, 40, 8, 16))
        # Dog (to the right of person)
        pygame.draw.rect(char1, dog_color, (40, 40, 12, 8))  # Dog body
        pygame.draw.rect(char1, dog_color, (48, 36, 8, 8))   # Dog head
        pygame.draw.rect(char1, (50, 50, 50), (52, 38, 2, 2))  # Dog eye
        pygame.draw.rect(char1, (50, 50, 50), (40, 44, 4, 4))  # Dog legs front
        pygame.draw.rect(char1, (50, 50, 50), (48, 44, 4, 4))  # Dog legs back
        # Leash
        pygame.draw.line(char1, (150, 150, 150), (24, 30), (44, 38), 1)
        
        frames.append(char1)
        
        # Frame 2 - Walking
        char2 = pygame.Surface((64, 64), pygame.SRCALPHA)
        # Body
        pygame.draw.rect(char2, body_color, (16, 16, 16, 24))
        # Head
        pygame.draw.rect(char2, head_color, (16, 4, 16, 16))
        # Legs (walking position)
        pygame.draw.rect(char2, leg_color, (12, 40, 8, 16))
        pygame.draw.rect(char2, leg_color, (28, 40, 8, 16))
        # Dog (walking)
        pygame.draw.rect(char2, dog_color, (42, 40, 12, 8))  # Dog body
        pygame.draw.rect(char2, dog_color, (50, 36, 8, 8))   # Dog head
        pygame.draw.rect(char2, (50, 50, 50), (54, 38, 2, 2))  # Dog eye
        pygame.draw.rect(char2, (50, 50, 50), (42, 46, 4, 4))  # Dog legs front (walking)
        pygame.draw.rect(char2, (50, 50, 50), (50, 44, 4, 4))  # Dog legs back (walking)
        # Leash
        pygame.draw.line(char2, (150, 150, 150), (24, 30), (46, 38), 1)
        
        frames.append(char2)
        
        # Frame 3 - Another walking pose
        char3 = pygame.Surface((64, 64), pygame.SRCALPHA)
        # Body
        pygame.draw.rect(char3, body_color, (16, 16, 16, 24))
        # Head
        pygame.draw.rect(char3, head_color, (16, 4, 16, 16))
        # Legs (alternate walking position)
        pygame.draw.rect(char3, leg_color, (20, 40, 8, 16))
        pygame.draw.rect(char3, leg_color, (20, 40, 8, 16))
        # Dog (alternate walking)
        pygame.draw.rect(char3, dog_color, (38, 40, 12, 8))  # Dog body
        pygame.draw.rect(char3, dog_color, (46, 36, 8, 8))   # Dog head
        pygame.draw.rect(char3, (50, 50, 50), (50, 38, 2, 2))  # Dog eye
        pygame.draw.rect(char3, (50, 50, 50), (38, 44, 4, 4))  # Dog legs front
        pygame.draw.rect(char3, (50, 50, 50), (46, 46, 4, 4))  # Dog legs back (walking)
        # Dog tail wagging
        pygame.draw.line(char3, dog_color, (38, 40), (34, 36), 2)
        # Leash
        pygame.draw.line(char3, (150, 150, 150), (24, 30), (42, 38), 1)
        
        frames.append(char3)
        
        # Frame 4 - Walking with arm movement
        char4 = pygame.Surface((64, 64), pygame.SRCALPHA)
        # Body
        pygame.draw.rect(char4, body_color, (16, 16, 16, 24))
        # Head
        pygame.draw.rect(char4, head_color, (16, 4, 16, 16))
        # Legs
        pygame.draw.rect(char4, leg_color, (16, 40, 8, 16))
        pygame.draw.rect(char4, leg_color, (24, 40, 8, 16))
        # Arms
        pygame.draw.rect(char4, head_color, (8, 20, 8, 12))
        pygame.draw.rect(char4, head_color, (32, 20, 8, 12))
        # Dog (looking up at owner)
        pygame.draw.rect(char4, dog_color, (40, 40, 12, 8))  # Dog body
        pygame.draw.rect(char4, dog_color, (48, 34, 8, 8))   # Dog head (looking up)
        pygame.draw.rect(char4, (50, 50, 50), (52, 36, 2, 2))  # Dog eye
        pygame.draw.rect(char4, (50, 50, 50), (40, 44, 4, 4))  # Dog legs front
        pygame.draw.rect(char4, (50, 50, 50), (48, 44, 4, 4))  # Dog legs back
        # Leash
        pygame.draw.line(char4, (150, 150, 150), (32, 26), (48, 36), 1)
        
        frames.append(char4)
        
        # Add seasonal accessories
        for frame in frames:
            if self.season == "Winter":  # Winter - add hat
                pygame.draw.rect(frame, (255, 50, 50), (16, 0, 16, 6))
            elif self.season == "Summer":  # Summer - add sunglasses
                pygame.draw.rect(frame, (50, 50, 50), (16, 10, 16, 4))
        
        return frames
    
    def create_celestial_object(self):
        """Create sun or moon based on time of day"""
        size = 40
        celestial = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if self.time_of_day in ["Morning", "Day"]:  # Morning or Day - Sun
            # Sun
            pygame.draw.circle(celestial, (255, 255, 200), (size//2, size//2), size//2)
            if self.time_of_day == "Day":  # Brighter at noon
                pygame.draw.circle(celestial, (255, 255, 100), (size//2, size//2), size//2 - 5)
        elif self.time_of_day == "Evening":  # Evening - Setting sun
            # Orange sun
            pygame.draw.circle(celestial, (255, 150, 50), (size//2, size//2), size//2)
        else:  # Night - Moon
            # Moon
            pygame.draw.circle(celestial, (220, 220, 255), (size//2, size//2), size//2)
            # Moon crater details
            pygame.draw.circle(celestial, (200, 200, 235), (size//3, size//3), size//10)
            pygame.draw.circle(celestial, (200, 200, 235), (2*size//3, 2*size//3), size//8)
        
        return celestial
    
    def create_seasonal_objects(self):
        """Create objects that appear based on the season"""
        self.seasonal_objects = []
        
        # Number of objects to create
        num_objects = 20
        
        for _ in range(num_objects):
            obj = {
                'x': random.randint(0, self.WINDOW_WIDTH),
                'y': random.randint(self.WINDOW_HEIGHT - 120, self.WINDOW_HEIGHT - 60),
                'size': random.randint(5, 15),
                'type': random.choice(['ground', 'floating']),
                'speed': random.uniform(0.2, 0.8) if random.random() > 0.7 else 0,
                'color': (255, 255, 255)  # Default, will be set based on season
            }
            
            # Set object properties based on season
            if self.season == "Spring":  # Spring - flowers
                obj['color'] = random.choice([
                    (255, 150, 150),  # Pink
                    (255, 255, 150),  # Yellow
                    (150, 255, 150),  # Light green
                    (200, 150, 255)   # Purple
                ])
                obj['shape'] = 'flower'
            elif self.season == "Summer":  # Summer - butterflies, dragonflies
                obj['color'] = random.choice([
                    (255, 200, 50),   # Orange
                    (100, 200, 255),  # Light blue
                    (255, 255, 150),  # Yellow
                    (200, 255, 200)   # Light green
                ])
                obj['shape'] = 'insect'
                obj['type'] = 'floating'  # All summer objects float
            elif self.season == "Autumn":  # Autumn - fallen leaves
                obj['color'] = random.choice([
                    (200, 100, 50),   # Brown
                    (255, 150, 50),   # Orange
                    (200, 50, 50),    # Red
                    (255, 200, 50)    # Yellow
                ])
                obj['shape'] = 'leaf'
                # Some leaves on ground, some floating
            else:  # Winter - snowflakes
                obj['color'] = random.choice([
                    (250, 250, 255),  # White
                    (230, 230, 255),  # Slightly blue white
                    (255, 255, 255),  # Pure white
                ])
                obj['shape'] = 'snowflake'
                if random.random() > 0.7:
                    obj['type'] = 'falling'
                    obj['y'] = random.randint(0, self.WINDOW_HEIGHT // 2)
            
            self.seasonal_objects.append(obj)
    
    def create_sea(self):
        """Create a pixel art sea background"""
        sea_height = self.WINDOW_HEIGHT // 2
        sea = pygame.Surface((self.WINDOW_WIDTH * 2, sea_height), pygame.SRCALPHA)
        
        # Sea colors based on time of day and season
        if self.time_of_day == "Morning":
            base_color = (30, 144, 255)  # Bright blue
            highlight_color = (135, 206, 250)  # Light sky blue
        elif self.time_of_day == "Day":
            base_color = (0, 105, 148)  # Deep blue
            highlight_color = (64, 164, 223)  # Medium blue
        elif self.time_of_day == "Evening":
            base_color = (25, 25, 112)  # Midnight blue
            highlight_color = (70, 130, 180)  # Steel blue
        else:  # Night
            base_color = (0, 0, 80)  # Dark blue
            highlight_color = (30, 30, 100)  # Slightly lighter blue
        
        # Adjust for season
        if self.season == "Winter":
            # Colder, more desaturated sea
            base_color = (base_color[0] * 0.8, base_color[1] * 0.9, min(base_color[2] * 1.1, 255))
            highlight_color = (highlight_color[0] * 0.8, highlight_color[1] * 0.9, min(highlight_color[2] * 1.1, 255))
        elif self.season == "Summer":
            # Brighter, more vibrant sea
            base_color = (base_color[0] * 0.9, min(base_color[1] * 1.2, 255), min(base_color[2] * 1.1, 255))
            highlight_color = (highlight_color[0] * 0.9, min(highlight_color[1] * 1.2, 255), min(highlight_color[2] * 1.1, 255))
        
        # Fill the sea with base color
        sea.fill(base_color)
        
        # Create waves with highlight color
        wave_height = 4
        wave_spacing = 20
        wave_offset = 0
        
        for y in range(0, sea_height, wave_spacing):
            for x in range(0, self.WINDOW_WIDTH * 2):
                # Create a sine wave pattern
                wave_y = y + int(math.sin(x / 30) * wave_height)
                if 0 <= wave_y < sea_height:
                    # Draw wave line
                    sea.set_at((x, wave_y), highlight_color)
        
        # Add some random highlights for sparkle
        for _ in range(200):
            x = random.randint(0, self.WINDOW_WIDTH * 2 - 1)
            y = random.randint(0, sea_height - 1)
            brightness = random.randint(180, 255)
            sea.set_at((x, y), (brightness, brightness, brightness))
        
        return sea
    
    def create_bench(self):
        """Create a simple pixel art bench for resting - 3x wider but original height"""
        bench = pygame.Surface((180, 30), pygame.SRCALPHA)  # Width 3x (180), original height (30)
        
        # Bench color based on season
        if self.season == "Winter":
            bench_color = (150, 150, 170)  # Snow-covered bench
            detail_color = (120, 120, 140)
        else:
            bench_color = (120, 80, 40)  # Wooden bench
            detail_color = (100, 60, 20)
        
        # Bench seat (3x wider, original height)
        pygame.draw.rect(bench, bench_color, (15, 10, 150, 8))  # was (5, 10, 50, 8)
        
        # Bench back (3x wider, original height)
        pygame.draw.rect(bench, bench_color, (30, 0, 120, 10))   # was (10, 0, 40, 10)
        pygame.draw.rect(bench, detail_color, (30, 0, 120, 2))   # was (10, 0, 40, 2)
        
        # Bench legs (3x wider spacing, original height)
        pygame.draw.rect(bench, bench_color, (30, 18, 5, 12))    # Left leg
        pygame.draw.rect(bench, bench_color, (145, 18, 5, 12))   # Right leg (3x spacing)
        
        # Details (3x wider spacing, original positions)
        for i in range(5):  # More details for wider bench
            pygame.draw.line(bench, detail_color, (30 + i*30, 10), (30 + i*30, 18), 1)
        
        return bench
    
    def draw_character_sitting(self, x, y, activity="sitting"):
        """Draw the character sitting on the bench with different activities"""
        # Colors based on season (clothing changes with season)
        if self.season == "Spring":  # Spring
            body_color = (255, 150, 150)  # Light red
            head_color = (255, 200, 150)  # Skin tone
            leg_color = (100, 100, 255)  # Blue
            dog_color = (240, 220, 180)  # Light brown dog
        elif self.season == "Summer":  # Summer
            body_color = (255, 255, 150)  # Yellow
            head_color = (255, 200, 150)  # Skin tone
            leg_color = (100, 200, 100)  # Green
            dog_color = (240, 220, 180)  # Light brown dog
        elif self.season == "Autumn":  # Autumn
            body_color = (200, 100, 50)  # Brown
            head_color = (255, 200, 150)  # Skin tone
            leg_color = (150, 100, 50)  # Dark brown
            dog_color = (200, 180, 150)  # Darker brown dog
        else:  # Winter
            body_color = (200, 200, 255)  # Light blue
            head_color = (255, 200, 150)  # Skin tone
            leg_color = (50, 50, 150)  # Dark blue
            dog_color = (240, 240, 240)  # White dog (winter coat)
        
        # Create sitting character
        char = pygame.Surface((64, 64), pygame.SRCALPHA)
        
        # Body (sitting)
        pygame.draw.rect(char, body_color, (16, 16, 16, 20))
        
        # Head position and eyes based on activity
        if activity == "looking_up":
            # Head tilted back looking up
            pygame.draw.rect(char, head_color, (16, 2, 16, 16))
            # Eyes looking up
            pygame.draw.rect(char, (50, 50, 50), (19, 6, 3, 2))
            pygame.draw.rect(char, (50, 50, 50), (26, 6, 3, 2))
        elif activity == "checking_phone":
            # Head looking down at phone
            pygame.draw.rect(char, head_color, (16, 6, 16, 16))
            # Eyes looking down
            pygame.draw.rect(char, (50, 50, 50), (19, 14, 3, 2))
            pygame.draw.rect(char, (50, 50, 50), (26, 14, 3, 2))
            # Phone in hand
            pygame.draw.rect(char, (50, 50, 50), (10, 20, 4, 6))
        elif activity == "stretching":
            # Normal head position
            pygame.draw.rect(char, head_color, (16, 4, 16, 16))
            # Eyes
            pygame.draw.rect(char, (50, 50, 50), (19, 10, 3, 2))
            pygame.draw.rect(char, (50, 50, 50), (26, 10, 3, 2))
            # Arms stretched up
            pygame.draw.rect(char, head_color, (8, 8, 6, 12))   # Left arm up
            pygame.draw.rect(char, head_color, (34, 8, 6, 12))  # Right arm up
        elif activity == "drinking_water":
            # Head tilted slightly
            pygame.draw.rect(char, head_color, (16, 4, 16, 16))
            # Eyes
            pygame.draw.rect(char, (50, 50, 50), (19, 10, 3, 2))
            pygame.draw.rect(char, (50, 50, 50), (26, 10, 3, 2))
            # Water bottle
            pygame.draw.rect(char, (100, 150, 255), (8, 16, 4, 8))  # Blue bottle
            # Arm holding bottle
            pygame.draw.rect(char, head_color, (8, 18, 8, 8))
        elif activity == "petting_dog":
            # Head looking down at dog
            pygame.draw.rect(char, head_color, (16, 6, 16, 16))
            # Eyes looking down
            pygame.draw.rect(char, (50, 50, 50), (19, 14, 3, 2))
            pygame.draw.rect(char, (50, 50, 50), (26, 14, 3, 2))
            # Arm extended toward dog
            pygame.draw.rect(char, head_color, (32, 20, 12, 6))
        else:
            # Normal sitting position
            pygame.draw.rect(char, head_color, (16, 4, 16, 16))
            # Eyes
            pygame.draw.rect(char, (50, 50, 50), (19, 10, 3, 2))
            pygame.draw.rect(char, (50, 50, 50), (26, 10, 3, 2))
        
        # Legs (sitting position)
        pygame.draw.rect(char, leg_color, (12, 36, 8, 12))
        pygame.draw.rect(char, leg_color, (28, 36, 8, 12))
        
        # Dog position and behavior based on activity
        if activity == "petting_dog":
            # Dog closer to owner, looking up happily
            pygame.draw.rect(char, dog_color, (40, 32, 12, 12))  # Dog body (closer)
            pygame.draw.rect(char, dog_color, (44, 20, 8, 12))   # Dog head (looking up)
            pygame.draw.rect(char, (50, 50, 50), (46, 24, 2, 2))  # Dog eye
            # Wagging tail
            pygame.draw.line(char, dog_color, (40, 36), (36, 30), 2)
        else:
            # Dog sitting next to owner normally
            pygame.draw.rect(char, dog_color, (45, 36, 12, 12))  # Dog body (sitting)
            pygame.draw.rect(char, dog_color, (48, 24, 8, 12))   # Dog head
            pygame.draw.rect(char, (50, 50, 50), (50, 28, 2, 2))  # Dog eye
        
        # Leash
        if activity == "petting_dog":
            pygame.draw.line(char, (150, 150, 150), (32, 26), (44, 24), 1)
        else:
            pygame.draw.line(char, (150, 150, 150), (32, 26), (48, 28), 1)
        
        # Add seasonal accessories
        if self.season == "Winter":  # Winter - add hat
            pygame.draw.rect(char, (255, 50, 50), (16, 0, 16, 6))
        elif self.season == "Summer":  # Summer - add sunglasses
            pygame.draw.rect(char, (50, 50, 50), (16, 10, 16, 4))
        
        # Draw the character (centered on wider bench)
        self.screen.blit(char, (x - 32, y - 40))  # Original height position
    def create_clouds(self):
        """Create pixel art clouds"""
        clouds = pygame.Surface((self.WINDOW_WIDTH * 3, 80), pygame.SRCALPHA)
        
        # Get cloud color from time-based palette
        cloud_color = self.colors["cloud"]
        cloud_shadow = (cloud_color[0]-20, cloud_color[1]-20, cloud_color[2]-20)
        
        # Draw a few simple clouds with pixel art style
        for x in range(0, self.WINDOW_WIDTH * 3, 200):
            offset_y = (x % 400) // 40  # Vary cloud height slightly
            
            # Cloud base
            for i in range(5):
                cloud_x = x + i * 16
                cloud_y = 30 + offset_y * 5
                size = 12 if i in (0, 4) else 16
                pygame.draw.rect(clouds, cloud_color, (cloud_x, cloud_y, size, size))
                pygame.draw.rect(clouds, cloud_shadow, (cloud_x, cloud_y + size, size, 4))
        
        # Add stars at night
        if self.time_of_day == "Night":
            for _ in range(100):
                star_x = random.randint(0, self.WINDOW_WIDTH * 3)
                star_y = random.randint(0, 60)
                star_size = random.randint(1, 3)
                brightness = random.randint(200, 255)
                pygame.draw.rect(clouds, (brightness, brightness, brightness), 
                                (star_x, star_y, star_size, star_size))
        
        return clouds
    
    def create_path(self):
        """Create a pixel art path/ground"""
        path = pygame.Surface((self.WINDOW_WIDTH, 40), pygame.SRCALPHA)
        
        # Get path color from season-based palette
        path_color = self.colors["path"]
        path_detail = (path_color[0]-20, path_color[1]-20, path_color[2]-20)
        
        # Create a tiled path with pixel art details
        for x in range(0, self.WINDOW_WIDTH, 32):
            # Base tile
            pygame.draw.rect(path, path_color, (x, 0, 32, 40))
            
            # Tile borders
            pygame.draw.line(path, path_detail, (x, 0), (x, 40))
            
            # Add some pixel details to tiles
            if x % 96 == 0:  # Every 3rd tile has a stone
                pygame.draw.rect(path, (150, 150, 150), (x + 12, 20, 8, 6))
            elif x % 64 == 0:  # Some tiles have grass tufts
                if self.season != "Winter":  # No grass tufts in winter
                    pygame.draw.rect(path, (100, 200, 100), (x + 20, 5, 4, 8))
                    pygame.draw.rect(path, (120, 220, 120), (x + 22, 2, 2, 3))
            
            # Add seasonal details
            if self.season == "Autumn" and random.random() > 0.8:
                # Fallen leaves in autumn
                leaf_x = x + random.randint(5, 25)
                leaf_y = random.randint(5, 35)
                leaf_color = random.choice([
                    (200, 100, 50),  # Brown
                    (220, 160, 50),  # Orange
                    (200, 50, 50),   # Red
                ])
                pygame.draw.circle(path, leaf_color, (leaf_x, leaf_y), 2)
            elif self.season == "Winter" and random.random() > 0.8:
                # Snow patches in winter
                snow_x = x + random.randint(5, 25)
                snow_y = random.randint(5, 35)
                pygame.draw.circle(path, (255, 255, 255), (snow_x, snow_y), 3)
        
        return path
    def update_seasonal_objects(self):
        """Update seasonal objects (flowers, leaves, etc)"""
        for obj in self.seasonal_objects:
            if obj['type'] == 'floating':
                # Floating objects move in a sine wave pattern
                obj['x'] += math.sin(pygame.time.get_ticks() / 1000) * 0.5
                obj['y'] += math.cos(pygame.time.get_ticks() / 1000 + obj['x']) * 0.3
            elif obj['type'] == 'falling':
                # Falling objects (like snow) move downward
                obj['y'] += obj['speed']
                obj['x'] += math.sin(pygame.time.get_ticks() / 1000 + obj['y']) * 0.2
                
                # Reset if off screen
                if obj['y'] > self.WINDOW_HEIGHT:
                    obj['y'] = random.randint(-20, 0)
                    obj['x'] = random.randint(0, self.WINDOW_WIDTH)
    
    def draw_seasonal_objects(self):
        """Draw seasonal objects"""
        for obj in self.seasonal_objects:
            if obj['shape'] == 'flower':
                # Draw a simple flower
                pygame.draw.circle(self.screen, obj['color'], 
                                  (int(obj['x']), int(obj['y'])), 
                                  obj['size'] // 2)
                # Flower center
                pygame.draw.circle(self.screen, (255, 255, 150), 
                                  (int(obj['x']), int(obj['y'])), 
                                  obj['size'] // 4)
            elif obj['shape'] == 'leaf':
                # Draw a simple leaf
                points = [
                    (obj['x'], obj['y'] - obj['size'] // 2),
                    (obj['x'] + obj['size'] // 2, obj['y']),
                    (obj['x'], obj['y'] + obj['size'] // 2),
                    (obj['x'] - obj['size'] // 2, obj['y'])
                ]
                pygame.draw.polygon(self.screen, obj['color'], points)
            elif obj['shape'] == 'snowflake':
                # Draw a simple snowflake
                pygame.draw.circle(self.screen, obj['color'], 
                                  (int(obj['x']), int(obj['y'])), 
                                  obj['size'] // 3)
            elif obj['shape'] == 'insect':
                # Draw a simple butterfly/insect
                pygame.draw.circle(self.screen, obj['color'], 
                                  (int(obj['x']), int(obj['y'])), 
                                  obj['size'] // 3)
                # Wings
                wing_size = obj['size'] // 2
                wing_offset = int(math.sin(pygame.time.get_ticks() / 200) * wing_size)
                pygame.draw.circle(self.screen, obj['color'], 
                                  (int(obj['x'] - wing_offset), int(obj['y'])), 
                                  wing_size)
                pygame.draw.circle(self.screen, obj['color'], 
                                  (int(obj['x'] + wing_offset), int(obj['y'])), 
                                  wing_size)
    
    def draw_time_input(self):
        """Draw time input interface"""
        # Title
        title_text = self.font_small.render("Walking Duration (3-60 minutes):", True, (255, 255, 255))
        title_x = self.WINDOW_WIDTH // 2 - title_text.get_width() // 2
        title_y = self.WINDOW_HEIGHT // 2 - 60
        self.screen.blit(title_text, (title_x, title_y))
        
        # Input box
        input_box_width = 200
        input_box_height = 50
        input_box_x = self.WINDOW_WIDTH // 2 - input_box_width // 2
        input_box_y = title_y + 40
        
        self.input_box_rect = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
        
        # Draw input box
        box_color = (255, 255, 255) if self.input_active else (200, 200, 200)
        border_color = (100, 150, 255) if self.input_active else (100, 100, 100)
        
        pygame.draw.rect(self.screen, box_color, self.input_box_rect)
        pygame.draw.rect(self.screen, border_color, self.input_box_rect, 3)
        
        # Draw input text
        display_text = self.duration_input_text + (" min" if not self.input_active else "")
        if self.input_active:
            # Add cursor
            display_text += "|"
        
        text_surface = self.font_large.render(display_text, True, (0, 0, 0))
        text_x = self.input_box_rect.centerx - text_surface.get_width() // 2
        text_y = self.input_box_rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        # Instructions
        instructions = [
            "Click the box and type a number (3-60)",
            "Press ENTER to start walking"
        ]
        
        for i, instruction in enumerate(instructions):
            color = (200, 200, 200)
            font = pygame.font.SysFont("Arial Unicode MS", 24)
            inst_surface = font.render(instruction, True, color)
            inst_x = self.WINDOW_WIDTH // 2 - inst_surface.get_width() // 2
            inst_y = input_box_y + 70 + i * 30
            self.screen.blit(inst_surface, (inst_x, inst_y))
    
    def handle_time_input_click(self, pos):
        """Handle clicks on time input interface"""
        # Check CRT input box click (using screen coordinates)
        if hasattr(self, 'crt_input_box_rect') and self.crt_input_box_rect.collidepoint(pos):
            self.input_active = True
            print(f"🖱️  Input box clicked at {pos}, activating input")
            return True
        
        # Click outside - deactivate input
        if self.input_active:
            self.input_active = False
            print("🖱️  Clicked outside, deactivating input")
        return False
    
    def handle_text_input(self, text):
        """Handle text input for duration"""
        if not self.input_active:
            return
        
        print(f"📝 Text input: '{text}', current: '{self.duration_input_text}'")
        
        # Only allow digits
        if text.isdigit():
            new_text = self.duration_input_text + text
            # Check if within limits (3-60 minutes) - allow building up numbers
            if new_text.isdigit():
                new_value = int(new_text)
                # Allow any input that could potentially become valid (1-6 as first digits)
                if len(new_text) == 1 and new_value in [1, 2, 3, 4, 5, 6]:
                    # Allow single digits that could become valid 2-digit numbers
                    self.duration_input_text = new_text
                    self.input_duration = max(new_value * 60, 180)  # Minimum 3 minutes for calculation
                    print(f"✅ Single digit input: '{self.duration_input_text}' (building number)")
                elif 3 <= new_value <= 60:
                    # Valid complete number
                    self.duration_input_text = new_text
                    self.input_duration = new_value * 60
                    print(f"✅ Input updated: '{self.duration_input_text}' ({self.input_duration}s)")
                else:
                    print(f"❌ Input rejected: '{new_text}' (out of range 3-60)")
            else:
                print(f"❌ Input rejected: '{new_text}' (not a valid number)")
        else:
            print(f"❌ Input rejected: '{text}' (not a digit)")
    
    def handle_backspace(self):
        """Handle backspace in text input"""
        if not self.input_active:
            return
        
        print(f"⌫ Backspace pressed, current: '{self.duration_input_text}'")
        
        if len(self.duration_input_text) > 0:
            self.duration_input_text = self.duration_input_text[:-1]
            # Allow empty input - don't force minimum value
            if self.duration_input_text == "":
                self.input_duration = 180  # Default 3 minutes for calculation, but allow empty display
            else:
                self.input_duration = int(self.duration_input_text) * 60
            print(f"✅ After backspace: '{self.duration_input_text}'")
    
    def start_walking(self):
        """Start the room transition instead of immediately starting the game"""
        # Handle empty input
        if self.duration_input_text == "":
            print("❌ Empty input, using default 3 minutes")
            self.duration_input_text = "3"
            self.input_duration = 180
        
        if not self.duration_input_text.isdigit():
            return False
        
        minutes = int(self.duration_input_text)
        
        # If single digit less than 3, reject
        if minutes < 3:
            print(f"❌ {minutes} minutes is too short, minimum is 3 minutes")
            return False
        elif minutes > 60:
            print(f"❌ {minutes} minutes is too long, maximum is 60 minutes")
            return False
        
        # Start the room transition instead of the game directly
        self.start_room_transition()
        return True
    
    def start_room_transition(self):
        """Start the transition from room to walking scene"""
        self.transition_phase = "standing"
        self.transition_progress = 0.0
        self.transition_start_time = pygame.time.get_ticks()  # Record actual start time
        print(f"🚶 Starting transition: Standing up from chair... (Duration: {self.transition_duration}s)")
        print(f"   Start time: {self.transition_start_time}ms")
    
    def update_room_transition(self, dt):
        """Update the room to walk transition"""
        if self.transition_phase == "room":
            return
        
        # Calculate actual elapsed time since transition started
        current_time = pygame.time.get_ticks()
        elapsed_ms = current_time - self.transition_start_time
        elapsed_seconds = elapsed_ms / 1000.0
        
        progress_normalized = min(elapsed_seconds / self.transition_duration, 1.0)
        
        # Debug info every second
        if int(elapsed_seconds) != int(elapsed_seconds - dt/1000.0) and elapsed_seconds > 0:
            print(f"🕐 Transition: {elapsed_seconds:.1f}s elapsed ({progress_normalized*100:.1f}% complete)")
        
        if self.transition_phase == "standing":
            # Phase 1: Standing up (0.0 - 0.25 of total progress) - 2 seconds
            if progress_normalized <= 0.25:
                stand_progress = progress_normalized / 0.25
                self.update_standing_animation(stand_progress)
            else:
                self.transition_phase = "walking"
                print("🚶 Transition: Walking to window...")
                
        elif self.transition_phase == "walking":
            # Phase 2: Walking to window (0.25 - 0.8 of total progress) - 4.4 seconds
            if progress_normalized <= 0.8:
                walk_progress = (progress_normalized - 0.25) / 0.55
                self.update_walking_animation(walk_progress)
            else:
                self.transition_phase = "window"
                print("🪟 Transition: Focusing on window...")
                
        elif self.transition_phase == "window":
            # Phase 3: Window focus (0.8 - 1.0 of total progress) - 1.6 seconds
            if progress_normalized < 1.0:
                window_progress = (progress_normalized - 0.8) / 0.2
                self.update_window_focus_animation(window_progress)
            else:
                # Transition complete - start the game
                total_time = elapsed_seconds
                print(f"✅ Transition completed in {total_time:.1f} seconds")
                self.complete_transition()
    
    def update_standing_animation(self, progress):
        """Update standing up animation"""
        # Camera moves up as we stand
        self.camera_y = self.ease_in_out(progress) * -30
        
    def update_walking_animation(self, progress):
        """Update walking to window animation with walking bob"""
        # Camera moves toward window
        self.camera_x = self.ease_in_out(progress) * -200
        
        # Add walking bob (up and down movement)
        # Use progress to create walking rhythm
        walking_speed = progress * 20  # Walking cycles
        bob_amplitude = 8  # How much to bob up and down
        self.walking_bob = math.sin(walking_speed) * bob_amplitude * progress  # Increase bob as we walk more
        
        # Apply walking bob to camera
        self.camera_y = self.ease_in_out(progress) * -30 + self.walking_bob
        
        # Window starts to get larger
        self.window_scale = 0.3 + (self.ease_in_out(progress) * 0.4)  # 0.3 to 0.7
        
    def update_window_focus_animation(self, progress):
        """Update window focus animation"""
        # Window expands to full screen
        self.window_scale = 0.7 + (self.ease_in_out(progress) * 0.3)  # 0.7 to 1.0
        
    def complete_transition(self):
        """Complete the transition and start the walking game"""
        self.transition_phase = "game"
        self.in_menu = False
        self.game_started = True
        self.start_time = pygame.time.get_ticks()
        self.walk_duration = self.input_duration
        
        # Reset character position and game state
        self.character_x = -self.character_frames[0].get_width()
        self.is_resting = False
        self.current_phase = 1
        self.current_activity = "sitting"
        
        # Calculate speed to reach bench in exactly 1 minute (60 seconds)
        distance_to_bench = self.bench_x - self.character_x
        self.walk_speed = distance_to_bench / (60 * self.FPS)
        
        print(f"🎮 Game Started after transition!")
        print(f"   Duration: {self.walk_duration} seconds ({self.walk_duration//60} minutes)")
    
    def ease_in_out(self, t):
        """Smooth easing function"""
        return t * t * (3.0 - 2.0 * t)
    
    def get_window_sky_color(self):
        """Get sky color for room window (matches walking scene)"""
        colors = self.get_colors_for_time()
        return colors['sky_top']
    
    def draw_room_background(self):
        """Draw the room background with camera offset"""
        # Apply camera transformation
        room_offset_x = self.camera_x
        room_offset_y = self.camera_y
        
        # Room background color (warm indoor lighting)
        if self.time_of_day == "Night":
            room_bg = (40, 35, 30)  # Darker room at night
        else:
            room_bg = (60, 55, 45)  # Warm room lighting
            
        self.screen.fill(room_bg)
        
        # Draw wall
        wall_color = (80, 70, 60)
        pygame.draw.rect(self.screen, wall_color, 
                        (room_offset_x, room_offset_y, self.WINDOW_WIDTH, self.WINDOW_HEIGHT // 2))
        
        # Draw window
        window_rect = self.get_room_window_rect(room_offset_x, room_offset_y)
        self.draw_room_window(window_rect)
        
        # Draw desk (only visible when not fully transitioned)
        if self.transition_phase in ["room", "standing"]:
            self.draw_desk(room_offset_x, room_offset_y)
        
        # Draw CRT screen (fades out during transition)
        if self.transition_phase in ["room", "standing"]:
            alpha = 255
            if self.transition_phase == "standing":
                alpha = int(255 * (1.0 - (self.transition_progress / self.transition_duration) / 0.4))
            self.draw_crt_screen(room_offset_x, room_offset_y, alpha)
            
        # Ensure input box is created even if CRT is not drawn
        elif not hasattr(self, 'crt_input_box_rect'):
            # Create a default input box for testing
            screen_x = self.WINDOW_WIDTH//2 - 150
            screen_y = self.WINDOW_HEIGHT - 200
            input_box_x = screen_x + (300 - 120) // 2
            input_box_y = screen_y + 85
            self.crt_input_box_rect = pygame.Rect(input_box_x, input_box_y, 120, 40)
    
    def get_room_window_rect(self, offset_x, offset_y):
        """Get window rectangle - large window behind the display"""
        # Large window positioned behind/above the CRT display
        base_window_width = 500   # Much larger window
        base_window_height = 180  # Taller window
        
        # Position window behind the display
        window_x = self.WINDOW_WIDTH // 2 - base_window_width // 2 + offset_x
        window_y = 20 + offset_y  # Higher up, behind the display
        
        base_window_rect = pygame.Rect(window_x, window_y, base_window_width, base_window_height)
        
        if self.transition_phase in ["walking", "window"]:
            # Scale and center window during transition, but keep it large
            center_x = self.WINDOW_WIDTH // 2
            center_y = self.WINDOW_HEIGHT // 2
            
            # Don't scale too much - keep window substantial
            scale_factor = 1.0 + (self.window_scale - 0.3) * 2.0  # More gradual scaling
            scaled_width = int(base_window_width * scale_factor)
            scaled_height = int(base_window_height * scale_factor)
            
            return pygame.Rect(
                center_x - scaled_width // 2,
                center_y - scaled_height // 2,
                scaled_width,
                scaled_height
            )
        
        return base_window_rect
    
    def draw_room_window(self, window_rect):
        """Draw room window with sky color - always show window frame and cross"""
        # Window content (sky color from walking scene)
        sky_color = self.get_window_sky_color()
        pygame.draw.rect(self.screen, sky_color, window_rect)
        
        # Add some simple outdoor elements if window is not too large
        if self.window_scale < 1.5:  # Show horizon when window is not fully expanded
            # Simple horizon line
            horizon_y = window_rect.y + int(window_rect.height * 0.7)
            ground_color = self.get_colors_for_time()['grass']  # Use 'grass' instead of 'ground'
            ground_rect = pygame.Rect(window_rect.x, horizon_y, 
                                    window_rect.width, window_rect.height - (horizon_y - window_rect.y))
            pygame.draw.rect(self.screen, ground_color, ground_rect)
        
        # Use the same overlay method for consistency
        self.draw_window_frame_overlay(window_rect)
    
    def draw_desk(self, offset_x, offset_y):
        """Draw the desk and computer setup - desktop PC style"""
        desk_y = self.WINDOW_HEIGHT - 80 + offset_y  # Back to original height
        desk_color = (60, 45, 30)  # Dark wood
        
        # Desk surface
        desk_rect = pygame.Rect(offset_x, desk_y, self.WINDOW_WIDTH, 80)
        pygame.draw.rect(self.screen, desk_color, desk_rect)
        
        # Desk edge highlight
        pygame.draw.line(self.screen, (80, 65, 50), 
                        (offset_x, desk_y), (self.WINDOW_WIDTH + offset_x, desk_y), 2)
        
        # Draw detailed keyboard
        self.draw_keyboard(offset_x, desk_y + 35)
        
        # Mouse - positioned to the right of keyboard
        mouse_rect = pygame.Rect(self.WINDOW_WIDTH//2 + 120 + offset_x, desk_y + 40, 25, 35)
        pygame.draw.rect(self.screen, (50, 50, 50), mouse_rect)
        pygame.draw.rect(self.screen, (70, 70, 70), mouse_rect, 1)
        
        # Mouse buttons
        pygame.draw.line(self.screen, (30, 30, 30), 
                        (mouse_rect.left + 12, mouse_rect.top + 5),
                        (mouse_rect.left + 12, mouse_rect.top + 20), 1)
        
        # Mouse scroll wheel
        pygame.draw.rect(self.screen, (30, 30, 30), 
                        (mouse_rect.left + 10, mouse_rect.top + 8, 4, 8))
    
    def draw_keyboard(self, offset_x, keyboard_y):
        """Draw detailed desktop keyboard with realistic layout"""
        keyboard_width = 280  # Wider keyboard
        keyboard_height = 45  # Taller keyboard
        keyboard_x = self.WINDOW_WIDTH//2 - keyboard_width//2 + offset_x
        
        # Keyboard base with gradient effect
        keyboard_rect = pygame.Rect(keyboard_x, keyboard_y, keyboard_width, keyboard_height)
        pygame.draw.rect(self.screen, (45, 45, 45), keyboard_rect)
        pygame.draw.rect(self.screen, (35, 35, 35), keyboard_rect, 3)
        
        # Keyboard brand label
        brand_font = pygame.font.SysFont("Arial", 8)
        brand_text = brand_font.render("RETRO-KB", True, (80, 80, 80))
        self.screen.blit(brand_text, (keyboard_x + 5, keyboard_y + 2))
        
        # Key dimensions
        key_width = 14
        key_height = 10
        key_spacing = 2
        
        # Function keys row (F1-F12)
        f_key_width = 18
        f_key_y = keyboard_y + 5
        for i in range(12):
            key_x = keyboard_x + 15 + i * (f_key_width + key_spacing)
            if i >= 4 and i < 8:  # F5-F8 group
                key_x += 8
            elif i >= 8:  # F9-F12 group
                key_x += 16
            
            key_rect = pygame.Rect(key_x, f_key_y, f_key_width, key_height - 2)
            pygame.draw.rect(self.screen, (75, 75, 75), key_rect)
            pygame.draw.rect(self.screen, (55, 55, 55), key_rect, 1)
            
            # F key labels
            f_font = pygame.font.SysFont("Arial", 6)
            f_text = f_font.render(f"F{i+1}", True, (200, 200, 200))
            text_x = key_rect.centerx - f_text.get_width()//2
            text_y = key_rect.centery - f_text.get_height()//2
            self.screen.blit(f_text, (text_x, text_y))
        
        # Number row (1-0)
        number_keys = "1234567890-="
        num_y = keyboard_y + 18
        for i, key_char in enumerate(number_keys):
            key_x = keyboard_x + 15 + i * (key_width + key_spacing)
            key_rect = pygame.Rect(key_x, num_y, key_width, key_height)
            pygame.draw.rect(self.screen, (70, 70, 70), key_rect)
            pygame.draw.rect(self.screen, (50, 50, 50), key_rect, 1)
            
            # Key labels
            key_font = pygame.font.SysFont("Arial", 7, bold=True)
            key_text = key_font.render(key_char, True, (200, 200, 200))
            text_x = key_rect.centerx - key_text.get_width()//2
            text_y = key_rect.centery - key_text.get_height()//2
            self.screen.blit(key_text, (text_x, text_y))
        
        # QWERTY row
        qwerty_keys = "QWERTYUIOP"
        qwerty_y = keyboard_y + 30
        for i, key_char in enumerate(qwerty_keys):
            key_x = keyboard_x + 25 + i * (key_width + key_spacing)  # Offset for realistic layout
            key_rect = pygame.Rect(key_x, qwerty_y, key_width, key_height)
            pygame.draw.rect(self.screen, (70, 70, 70), key_rect)
            pygame.draw.rect(self.screen, (50, 50, 50), key_rect, 1)
            
            # Key labels
            key_font = pygame.font.SysFont("Arial", 7, bold=True)
            key_text = key_font.render(key_char, True, (200, 200, 200))
            text_x = key_rect.centerx - key_text.get_width()//2
            text_y = key_rect.centery - key_text.get_height()//2
            self.screen.blit(key_text, (text_x, text_y))
        
        # ASDF row
        asdf_keys = "ASDFGHJKL"
        asdf_y = keyboard_y + 42
        for i, key_char in enumerate(asdf_keys):
            key_x = keyboard_x + 30 + i * (key_width + key_spacing)  # More offset
            key_rect = pygame.Rect(key_x, asdf_y - 12, key_width, key_height)
            pygame.draw.rect(self.screen, (70, 70, 70), key_rect)
            pygame.draw.rect(self.screen, (50, 50, 50), key_rect, 1)
            
            # Key labels
            key_font = pygame.font.SysFont("Arial", 7, bold=True)
            key_text = key_font.render(key_char, True, (200, 200, 200))
            text_x = key_rect.centerx - key_text.get_width()//2
            text_y = key_rect.centery - key_text.get_height()//2
            self.screen.blit(key_text, (text_x, text_y))
        
        # Special keys
        # Tab key
        tab_rect = pygame.Rect(keyboard_x + 15, qwerty_y, 20, key_height)
        pygame.draw.rect(self.screen, (65, 65, 65), tab_rect)
        pygame.draw.rect(self.screen, (45, 45, 45), tab_rect, 1)
        tab_font = pygame.font.SysFont("Arial", 6)
        tab_text = tab_font.render("TAB", True, (180, 180, 180))
        self.screen.blit(tab_text, (tab_rect.centerx - tab_text.get_width()//2, 
                                   tab_rect.centery - tab_text.get_height()//2))
        
        # Caps Lock
        caps_rect = pygame.Rect(keyboard_x + 15, asdf_y - 12, 25, key_height)
        pygame.draw.rect(self.screen, (65, 65, 65), caps_rect)
        pygame.draw.rect(self.screen, (45, 45, 45), caps_rect, 1)
        caps_text = tab_font.render("CAPS", True, (180, 180, 180))
        self.screen.blit(caps_text, (caps_rect.centerx - caps_text.get_width()//2, 
                                    caps_rect.centery - caps_text.get_height()//2))
        
        # Space bar - larger and more prominent
        spacebar_width = 120
        spacebar_height = 12
        spacebar_x = keyboard_x + (keyboard_width - spacebar_width) // 2
        spacebar_y = keyboard_y + keyboard_height - 15
        spacebar_rect = pygame.Rect(spacebar_x, spacebar_y, spacebar_width, spacebar_height)
        pygame.draw.rect(self.screen, (75, 75, 75), spacebar_rect)
        pygame.draw.rect(self.screen, (55, 55, 55), spacebar_rect, 2)
        
        # Enter key - distinctive shape
        enter_rect = pygame.Rect(keyboard_x + keyboard_width - 35, asdf_y - 12, 25, key_height)
        pygame.draw.rect(self.screen, (80, 60, 60), enter_rect)  # Slightly reddish
        pygame.draw.rect(self.screen, (60, 40, 40), enter_rect, 1)
        enter_text = tab_font.render("ENTER", True, (200, 180, 180))
        self.screen.blit(enter_text, (enter_rect.centerx - enter_text.get_width()//2, 
                                     enter_rect.centery - enter_text.get_height()//2))
    
    def draw_crt_screen(self, offset_x, offset_y, alpha=255):
        """Draw retro CRT computer screen - positioned in front of large window"""
        screen_width = 400  # Increased from 300
        screen_height = 250 # Increased from 200
        screen_x = self.WINDOW_WIDTH//2 - screen_width//2 + offset_x
        screen_y = self.WINDOW_HEIGHT - 140 + offset_y    # Positioned in front of window
        
        # Monitor stand/base - larger for bigger monitor
        stand_width = 100
        stand_height = 25
        stand_x = screen_x + (screen_width - stand_width) // 2
        stand_y = screen_y + screen_height
        
        # Draw monitor stand
        pygame.draw.rect(self.screen, (40, 35, 30), 
                        pygame.Rect(stand_x, stand_y, stand_width, stand_height))
        pygame.draw.rect(self.screen, (60, 55, 50), 
                        pygame.Rect(stand_x, stand_y, stand_width, stand_height), 2)
        
        # CRT monitor frame - larger
        frame_rect = pygame.Rect(screen_x - 20, screen_y - 20, screen_width + 40, screen_height + 40)
        frame_color = (40, 35, 30)  # Dark brown/black
        pygame.draw.rect(self.screen, frame_color, frame_rect)
        pygame.draw.rect(self.screen, (60, 55, 50), frame_rect, 5)
        
        # Screen surface with alpha
        screen_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        screen_bg = (20, 25, 20)  # Dark green CRT background
        screen_surface.fill((*screen_bg, alpha))
        
        # Store screen rect for click detection
        self.crt_screen_rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
        
        # Draw time input UI on CRT screen
        if self.in_menu and alpha > 0:
            self.draw_crt_time_input(screen_surface, alpha, screen_x, screen_y)
        
        # Apply screen surface to main screen
        self.screen.blit(screen_surface, (screen_x, screen_y))
        
        # CRT scan lines effect
        if alpha > 100:
            for y in range(0, screen_height, 3):
                line_alpha = min(alpha // 3, 80)
                pygame.draw.line(self.screen, (0, 0, 0, line_alpha),
                               (screen_x, screen_y + y),
                               (screen_x + screen_width, screen_y + y), 1)
    
    def draw_crt_time_input(self, surface, alpha, screen_x, screen_y):
        """Draw time input UI on larger CRT screen - removed title to prevent cutoff"""
        text_color = (0, min(255, int(255 * alpha / 255)), 100)  # Green CRT text
        
        # Range info - moved up to replace title position
        range_font = pygame.font.SysFont("Courier", 18, bold=True)  # Larger font since it's now primary
        range_text = range_font.render("(3-60 MINUTES)", True, text_color)
        range_alpha_surface = pygame.Surface(range_text.get_size(), pygame.SRCALPHA)
        range_alpha_surface.blit(range_text, (0, 0))
        range_alpha_surface.set_alpha(alpha)
        surface.blit(range_alpha_surface, (surface.get_width()//2 - range_text.get_width()//2, 50))  # Moved up
        
        # Input box - moved up to use more space
        input_box_width = 150
        input_box_height = 50
        input_box_x = (surface.get_width() - input_box_width) // 2
        input_box_y = 90  # Moved up from 110
        
        # Store input box rect in screen coordinates for click detection
        self.crt_input_box_rect = pygame.Rect(
            screen_x + input_box_x, 
            screen_y + input_box_y, 
            input_box_width, 
            input_box_height
        )
        
        # Draw input box on surface
        surface_input_rect = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
        box_color = (0, min(100, int(100 * alpha / 255)), 50)
        pygame.draw.rect(surface, box_color, surface_input_rect)
        
        if self.input_active:
            border_color = (0, min(255, int(255 * alpha / 255)), 150)
            pygame.draw.rect(surface, border_color, surface_input_rect, 4)
        else:
            pygame.draw.rect(surface, text_color, surface_input_rect, 3)
        
        # Input text - larger font
        display_text = self.duration_input_text
        if self.input_active:
            display_text += "_"  # CRT-style cursor
            
        input_font = pygame.font.SysFont("Courier", 32, bold=True)  # Even larger font
        input_text = input_font.render(display_text, True, text_color)
        input_alpha_surface = pygame.Surface(input_text.get_size(), pygame.SRCALPHA)
        input_alpha_surface.blit(input_text, (0, 0))
        input_alpha_surface.set_alpha(alpha)
        surface.blit(input_alpha_surface, (surface_input_rect.centerx - input_text.get_width()//2, 
                                         surface_input_rect.centery - input_text.get_height()//2))
        
        # Instructions - moved up
        inst_font = pygame.font.SysFont("Courier", 14)
        instructions = ["CLICK BOX AND TYPE NUMBER", "PRESS ENTER TO START"]
        for i, inst in enumerate(instructions):
            inst_text = inst_font.render(inst, True, text_color)
            inst_alpha_surface = pygame.Surface(inst_text.get_size(), pygame.SRCALPHA)
            inst_alpha_surface.blit(inst_text, (0, 0))
            inst_alpha_surface.set_alpha(alpha)
            surface.blit(inst_alpha_surface, (surface.get_width()//2 - inst_text.get_width()//2, 
                                            160 + i * 20))  # Moved up from 180
    
    def handle_events(self):
        """Process game events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            elif event.type == VIDEORESIZE:
                # Handle window resize
                self.handle_window_resize(event.w, event.h)
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.in_menu:
                        # Handle time input interface clicks
                        self.handle_time_input_click(event.pos)
            
            elif event.type == KEYDOWN:
                if self.in_menu and self.input_active:
                    # Handle text input when input is active
                    if event.key == K_RETURN or event.key == K_KP_ENTER:
                        # Start walking when Enter is pressed
                        if self.start_walking():
                            pass  # Game started successfully
                    elif event.key == K_BACKSPACE:
                        self.handle_backspace()
                    elif event.key == K_ESCAPE:
                        self.input_active = False
                    else:
                        # Handle character input
                        if event.unicode.isdigit():
                            self.handle_text_input(event.unicode)
                
                elif event.key == K_SPACE and not self.game_started and not self.in_menu:
                    self.game_started = True
                    self.start_time = pygame.time.get_ticks()
                elif event.key == K_r and self.game_finished:
                    # Reset the game
                    self.in_menu = True
                    self.game_started = False
                    self.game_finished = False
                    self.character_x = -self.character_frames[0].get_width()
                    self.elapsed_time = 0
                    self.is_resting = False
                    self.looking_up = False
                    self.current_phase = 1
                    self.current_activity = "sitting"
                    self.input_active = False
                    self.particles = []
                    # Reset transition state
                    self.transition_phase = "room"
                    self.transition_progress = 0.0
                    self.transition_start_time = 0
                    self.camera_x = 0
                    self.camera_y = 0
                    self.walking_bob = 0
                    self.window_scale = 0.3
                # Window size shortcuts (1-5 keys) - keep for convenience
                elif event.key >= K_1 and event.key <= K_5 and self.in_menu and not self.input_active:
                    size_index = event.key - K_1
                    if size_index < len(self.window_size_options):
                        new_width, new_height = self.window_size_options[size_index]
                        self.handle_window_resize(new_width, new_height)
        
        return True
    
    def update(self):
        """Update game state"""
        # Update room transition if active
        if self.transition_phase != "room" and self.transition_phase != "game":
            current_time = pygame.time.get_ticks()
            if hasattr(self, 'last_transition_time'):
                dt = current_time - self.last_transition_time
            else:
                dt = 16  # ~60fps fallback
            self.last_transition_time = current_time
            self.update_room_transition(dt)
            return
        
        # Normal game update (only when transition is complete)
        if self.game_started and not self.game_finished:
            # Update timer
            current_time = pygame.time.get_ticks()
            self.elapsed_time = (current_time - self.start_time) / 1000  # Convert to seconds
            
            # Phase-based movement logic
            if self.current_phase == 1:  # Phase 1: Walk to bench (first minute)
                # Move character towards bench
                self.character_x += self.walk_speed
                
                # Check if reached bench or first minute is up
                if self.character_x >= self.bench_x or self.elapsed_time >= 60:
                    self.character_x = self.bench_x  # Snap to bench position
                    self.is_resting = True
                    self.rest_start_time = current_time
                    self.current_phase = 2
                    # Calculate rest duration (total time - 2 minutes for walking)
                    self.rest_duration = self.walk_duration - 120
                    print(f"🪑 Phase 1->2: Reached bench at {self.elapsed_time:.1f}s, starting rest for {self.rest_duration:.1f}s")
            
            elif self.current_phase == 2:  # Phase 2: Rest on bench (middle time)
                rest_elapsed = (current_time - self.rest_start_time) / 1000
                time_remaining = self.walk_duration - self.elapsed_time
                
                # Debug info every 10 seconds
                if int(rest_elapsed) % 10 == 0 and int(rest_elapsed) > 0 and abs(rest_elapsed - int(rest_elapsed)) < 0.1:
                    print(f"😴 Phase 2: Resting {rest_elapsed:.1f}s elapsed, {time_remaining:.1f}s remaining")
                
                # Update resting activities
                self.update_resting_activities(current_time)
                
                # Start first activity when resting begins
                if rest_elapsed < 1 and self.current_activity == "sitting":
                    self.start_random_activity(current_time)
                
                # Check if rest time is over (1 minute left in walk)
                if time_remaining <= 60:
                    self.is_resting = False
                    self.current_phase = 3
                    self.current_activity = "sitting"  # Reset activity
                    # Calculate speed for final minute (bench to end)
                    remaining_distance = self.WINDOW_WIDTH - self.bench_x
                    self.walk_speed = remaining_distance / (60 * self.FPS)
                    print(f"🚶 Phase 2->3: Rest over at {self.elapsed_time:.1f}s, final walk begins")
                    print(f"   Distance: {remaining_distance}, Speed: {self.walk_speed:.4f}")
            
            elif self.current_phase == 3:  # Phase 3: Walk to end (last minute)
                # Move character towards end
                self.character_x += self.walk_speed
                
                # Debug info
                if int(self.elapsed_time) % 10 == 0 and abs(self.elapsed_time - int(self.elapsed_time)) < 0.1:
                    remaining_time = self.walk_duration - self.elapsed_time
                    print(f"🏃 Phase 3: Final walk {remaining_time:.1f}s remaining, position: {self.character_x:.1f}")
            
            # Update seasonal objects
            self.update_seasonal_objects()
            
            # Check if character reached the end
            if self.character_x >= self.WINDOW_WIDTH:
                self.game_finished = True
                self.elapsed_time = self.walk_duration  # Ensure timer shows exactly the set duration
    
    def draw_sky_gradient(self):
        """Draw sky with gradient based on time of day"""
        sky_top = self.colors["sky_top"]
        sky_bottom = self.colors["sky_bottom"]
        
        for y in range(0, self.WINDOW_HEIGHT // 2):
            # Calculate color for this line by interpolating between top and bottom colors
            t = y / (self.WINDOW_HEIGHT // 2)
            r = int(sky_top[0] * (1 - t) + sky_bottom[0] * t)
            g = int(sky_top[1] * (1 - t) + sky_bottom[1] * t)
            b = int(sky_top[2] * (1 - t) + sky_bottom[2] * t)
            
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.WINDOW_WIDTH, y))
    
    def draw(self):
        """Main drawing method"""
        # Draw based on current state
        if self.in_menu and self.transition_phase == "room":
            # Draw room scene
            self.draw_room_background()
        elif self.transition_phase in ["standing", "walking", "window"]:
            # Draw transition
            self.draw_room_background()
            # If window is large enough, start showing walking scene inside
            if self.window_scale > 0.6:
                self.draw_walking_scene_in_window()
        else:
            # Draw normal walking scene (full screen)
            self.draw_walking_scene()
        
        # Draw UI overlays
        if self.game_finished:
            self.draw_completion_screen()
        
        pygame.display.flip()
    
    def draw_walking_scene_in_window(self):
        """Draw walking scene constrained to window area during transition"""
        window_rect = self.get_room_window_rect(self.camera_x, self.camera_y)
        
        # Create a surface for the walking scene
        if window_rect.width > 10 and window_rect.height > 10:  # Ensure minimum size
            walk_surface = pygame.Surface((window_rect.width, window_rect.height))
            
            # Scale the walking scene to fit the window
            scale_x = window_rect.width / max(self.WINDOW_WIDTH, 1)  # Avoid division by zero
            scale_y = window_rect.height / max(self.WINDOW_HEIGHT, 1)  # Avoid division by zero
            
            # Draw scaled walking scene elements
            self.draw_scaled_walking_scene(walk_surface, scale_x, scale_y)
            
            # Blit to main screen
            self.screen.blit(walk_surface, window_rect)
            
            # IMPORTANT: Redraw window frame and cross AFTER the walking scene
            # This ensures the cross is always visible on top of the walking scene
            self.draw_window_frame_overlay(window_rect)
    
    def draw_window_frame_overlay(self, window_rect):
        """Draw window frame and cross as overlay - always on top"""
        # Window frame - always draw, adjust thickness based on scale
        frame_thickness = max(4, int(8 / max(self.window_scale, 0.3)))  # Ensure minimum thickness
        frame_color = (100, 80, 60)  # Brown window frame
        pygame.draw.rect(self.screen, frame_color, window_rect, frame_thickness)
        
        # Window cross (divider) - ALWAYS show, make more prominent
        cross_thickness = max(3, int(6 / max(self.window_scale, 0.3)))  # Ensure minimum thickness
        cross_color = (80, 60, 40)  # Slightly darker brown for contrast
        
        # Vertical divider - always draw
        pygame.draw.line(self.screen, cross_color,
                       (window_rect.centerx, window_rect.top + frame_thickness),
                       (window_rect.centerx, window_rect.bottom - frame_thickness), cross_thickness)
        
        # Horizontal divider - always draw
        pygame.draw.line(self.screen, cross_color,
                       (window_rect.left + frame_thickness, window_rect.centery),
                       (window_rect.right - frame_thickness, window_rect.centery), cross_thickness)
        
        # Add extra emphasis to cross at larger scales for better visibility over walking scene
        if self.window_scale > 1.0:
            # Draw additional cross lines for better visibility
            extra_thickness = max(1, cross_thickness // 2)
            shadow_color = (60, 40, 20)  # Even darker for shadow effect
            
            # Vertical emphasis with shadow
            pygame.draw.line(self.screen, shadow_color,
                           (window_rect.centerx - 1, window_rect.top + frame_thickness),
                           (window_rect.centerx - 1, window_rect.bottom - frame_thickness), extra_thickness)
            pygame.draw.line(self.screen, shadow_color,
                           (window_rect.centerx + 1, window_rect.top + frame_thickness),
                           (window_rect.centerx + 1, window_rect.bottom - frame_thickness), extra_thickness)
            
            # Horizontal emphasis with shadow
            pygame.draw.line(self.screen, shadow_color,
                           (window_rect.left + frame_thickness, window_rect.centery - 1),
                           (window_rect.right - frame_thickness, window_rect.centery - 1), extra_thickness)
            pygame.draw.line(self.screen, shadow_color,
                           (window_rect.left + frame_thickness, window_rect.centery + 1),
                           (window_rect.right - frame_thickness, window_rect.centery + 1), extra_thickness)
        
        # For very large windows, add even more emphasis
        if self.window_scale > 2.0:
            # Add bright highlight lines for maximum visibility
            highlight_color = (120, 100, 80)  # Lighter brown for highlight
            highlight_thickness = 1
            
            # Vertical highlight
            pygame.draw.line(self.screen, highlight_color,
                           (window_rect.centerx + cross_thickness//2, window_rect.top + frame_thickness),
                           (window_rect.centerx + cross_thickness//2, window_rect.bottom - frame_thickness), highlight_thickness)
            
            # Horizontal highlight  
            pygame.draw.line(self.screen, highlight_color,
                           (window_rect.left + frame_thickness, window_rect.centery + cross_thickness//2),
                           (window_rect.right - frame_thickness, window_rect.centery + cross_thickness//2), highlight_thickness)
    
    def draw_scaled_walking_scene(self, surface, scale_x, scale_y):
        """Draw walking scene scaled to fit in window"""
        # Simplified version - just draw sky and ground for now
        colors = self.get_colors_for_time()
        
        # Sky gradient (simplified)
        sky_rect = pygame.Rect(0, 0, surface.get_width(), int(surface.get_height() * 0.7))
        surface.fill(colors['sky_top'], sky_rect)
        
        # Ground
        ground_rect = pygame.Rect(0, int(surface.get_height() * 0.7), 
                                surface.get_width(), int(surface.get_height() * 0.3))
        surface.fill(colors['grass'], ground_rect)  # Use 'grass' instead of 'ground'
        
        # If game has started, draw character (scaled)
        if self.game_started and hasattr(self, 'character_x'):
            char_x = int(self.character_x * scale_x)
            char_y = int((self.character_y + 40) * scale_y)  # Adjust for ground level
            
            if 0 <= char_x <= surface.get_width():
                # Draw simple character representation
                char_color = (100, 100, 255) if not self.is_resting else (150, 100, 50)
                pygame.draw.circle(surface, char_color, (char_x, char_y), max(3, int(8 * min(scale_x, scale_y))))
    
    def draw_walking_scene(self):
        """Draw the full walking scene (original method)"""
        # Clear the screen first to prevent ghosting
        self.screen.fill((0, 0, 0))
        
        # Draw sky gradient
        self.draw_sky_gradient()
        
        # Draw celestial object (sun/moon)
        celestial_y = 40
        if self.time_of_day == "Morning":  # Morning - sun rising
            celestial_x = self.WINDOW_WIDTH // 4
        elif self.time_of_day == "Day":  # Day - sun high
            celestial_x = self.WINDOW_WIDTH // 2
        elif self.time_of_day == "Evening":  # Evening - sun setting
            celestial_x = 3 * self.WINDOW_WIDTH // 4
        else:  # Night - moon
            celestial_x = 2 * self.WINDOW_WIDTH // 3
            celestial_y = 30
        
        self.screen.blit(self.celestial_object, (celestial_x - self.celestial_object.get_width()//2, celestial_y))
        
        # Draw clouds (scrolling slowly)
        cloud_offset = int(self.elapsed_time * 5) % (self.WINDOW_WIDTH * 3)
        self.screen.blit(self.clouds, (-cloud_offset, 10))
        
        # Draw sea with gentle movement
        sea_offset = int(self.elapsed_time * 2) % (self.WINDOW_WIDTH * 2)
        self.screen.blit(self.sea, (-sea_offset, self.WINDOW_HEIGHT // 2))
        
        # Draw path at the bottom
        self.screen.blit(self.path, (0, self.WINDOW_HEIGHT - 40))
        
        # Draw bench in the middle of the screen (adjusted for wider bench)
        self.screen.blit(self.bench, (self.bench_x - 90, self.bench_y - 15))  # Center the wider bench
        
        # Draw seasonal objects
        self.draw_seasonal_objects()
        
        # Draw character if game has started
        if self.game_started:
            if self.is_resting:
                # Draw character sitting on bench with current activity
                self.draw_character_sitting(self.bench_x, self.bench_y, self.current_activity)
            else:
                # Determine which animation frame to use
                frame_index = (self.current_frame // self.animation_speed) % len(self.character_frames)
                
                # Add a slight up-down bounce to the walking
                bounce_offset = 0
                if self.game_started and not self.game_finished:
                    bounce_offset = math.sin(self.current_frame / 8) * 2
                
                # Create a temporary surface for the character to ensure proper transparency
                temp_surface = pygame.Surface((self.character_frames[frame_index].get_width(), 
                                              self.character_frames[frame_index].get_height()), 
                                             pygame.SRCALPHA)
                temp_surface.blit(self.character_frames[frame_index], (0, 0))
                
                # Draw the character using the temporary surface
                self.screen.blit(
                    temp_surface, 
                    (int(self.character_x), self.character_y + bounce_offset)
                )
                
                # Update animation frame
                self.current_frame = (self.current_frame + 1) % (self.animation_speed * len(self.character_frames))
        
        # Draw timer with background
        minutes = int(self.elapsed_time) // 60
        seconds = int(self.elapsed_time) % 60
        
        # Format timer text
        if minutes > 0:
            timer_text = f"{minutes}:{seconds:02d}"
        else:
            timer_text = f"{seconds} sec"
            
        timer_surface = self.font_small.render(timer_text, True, (0, 0, 0))
        
        # Draw timer background
        timer_bg_rect = pygame.Rect(self.WINDOW_WIDTH - 110, 5, timer_surface.get_width() + 20, timer_surface.get_height() + 10)
        pygame.draw.rect(self.screen, (255, 255, 255, 180), timer_bg_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), timer_bg_rect, 1)
        
        # Draw timer text
        self.screen.blit(timer_surface, (self.WINDOW_WIDTH - 100, 10))
        
        # Draw total duration with background
        total_minutes = self.walk_duration // 60
        total_seconds = self.walk_duration % 60
        if total_seconds == 0:
            total_text = f"Total: {total_minutes} min"
        else:
            total_text = f"Total: {total_minutes}:{total_seconds:02d}"
        
        total_surface = self.font_small.render(total_text, True, (0, 0, 0))
        
        # Draw total background
        total_bg_rect = pygame.Rect(self.WINDOW_WIDTH - 160, 35, total_surface.get_width() + 20, total_surface.get_height() + 10)
        pygame.draw.rect(self.screen, (255, 255, 255, 180), total_bg_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), total_bg_rect, 1)
        
        # Draw total text
        self.screen.blit(total_surface, (self.WINDOW_WIDTH - 150, 40))
        
        # Draw rest status if resting
        if self.is_resting:
            rest_minutes = int(self.rest_duration - (pygame.time.get_ticks() - self.rest_start_time) / 1000) // 60
            rest_seconds = int(self.rest_duration - (pygame.time.get_ticks() - self.rest_start_time) / 1000) % 60
            
            if rest_minutes > 0:
                rest_text = f"Resting: {rest_minutes}:{rest_seconds:02d} remaining"
            else:
                rest_text = f"Resting: {rest_seconds} sec remaining"
                
            rest_surface = self.font_small.render(rest_text, True, (0, 0, 0))
            
            # Draw rest background
            rest_bg_rect = pygame.Rect(15, 5, rest_surface.get_width() + 10, rest_surface.get_height() + 10)
            pygame.draw.rect(self.screen, (255, 255, 255, 180), rest_bg_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), rest_bg_rect, 1)
            
            # Draw rest text
            self.screen.blit(rest_surface, (20, 10))
        
        # Draw progress bar
        if self.game_started and not self.game_finished:
            progress_percent = self.elapsed_time / self.walk_duration
            progress_bar_width = 200
            progress_bar_height = 10
            progress_bar_x = self.WINDOW_WIDTH - progress_bar_width - 20
            progress_bar_y = 70
            
            # Draw background
            pygame.draw.rect(self.screen, (100, 100, 100), 
                            (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
            
            # Draw progress
            progress_width = int(progress_bar_width * progress_percent)
            pygame.draw.rect(self.screen, (100, 200, 100), 
                            (progress_bar_x, progress_bar_y, progress_width, progress_bar_height))
    
    def draw_completion_screen(self):
        """Draw completion screen"""
        # Create text surface for restart instruction only
        restart_text = self.font_small.render("Press R to restart", True, (0, 0, 0))
        
        # Create background rectangle for restart text
        restart_bg_rect = pygame.Rect(
            self.WINDOW_WIDTH // 2 - restart_text.get_width() // 2 - 10,
            self.WINDOW_HEIGHT // 2 - 5,
            restart_text.get_width() + 20,
            restart_text.get_height() + 10
        )
        
        # Draw background
        pygame.draw.rect(self.screen, (255, 255, 255, 200), restart_bg_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), restart_bg_rect, 1)
        
        # Draw restart text
        self.screen.blit(restart_text, (self.WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 
                                      self.WINDOW_HEIGHT // 2))
        
        # Draw total duration with background
        total_minutes = self.walk_duration // 60
        total_seconds = self.walk_duration % 60
        if total_seconds == 0:
            total_text = f"Total: {total_minutes} min"
        else:
            total_text = f"Total: {total_minutes}:{total_seconds:02d}"
        
        total_surface = self.font_small.render(total_text, True, (0, 0, 0))
        
        # Draw total background
        total_bg_rect = pygame.Rect(self.WINDOW_WIDTH - 160, 35, total_surface.get_width() + 20, total_surface.get_height() + 10)
        pygame.draw.rect(self.screen, (255, 255, 255, 180), total_bg_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), total_bg_rect, 1)
        
        # Draw total text
        self.screen.blit(total_surface, (self.WINDOW_WIDTH - 150, 40))
        
        # Draw rest status if resting
        if self.is_resting:
            rest_minutes = int(self.rest_duration - (pygame.time.get_ticks() - self.rest_start_time) / 1000) // 60
            rest_seconds = int(self.rest_duration - (pygame.time.get_ticks() - self.rest_start_time) / 1000) % 60
            
            if rest_minutes > 0:
                rest_text = f"Resting: {rest_minutes}:{rest_seconds:02d} remaining"
            else:
                rest_text = f"Resting: {rest_seconds} sec remaining"
                
            rest_surface = self.font_small.render(rest_text, True, (0, 0, 0))
            
            # Draw rest background
            rest_bg_rect = pygame.Rect(15, 5, rest_surface.get_width() + 10, rest_surface.get_height() + 10)
            pygame.draw.rect(self.screen, (255, 255, 255, 180), rest_bg_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), rest_bg_rect, 1)
            
            # Draw rest text
            self.screen.blit(rest_surface, (20, 10))
        
        # Draw progress bar
        if self.game_started and not self.game_finished:
            progress_percent = self.elapsed_time / self.walk_duration  # Based on time, not position
            progress_bar_width = 200
            progress_bar_height = 10
            progress_bar_x = self.WINDOW_WIDTH - progress_bar_width - 20
            progress_bar_y = 70
            
            # Draw background
            pygame.draw.rect(self.screen, (100, 100, 100), 
                            (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
            
            # Draw progress
            pygame.draw.rect(self.screen, (100, 200, 100), 
                            (progress_bar_x, progress_bar_y, 
                             int(progress_bar_width * progress_percent), progress_bar_height))
            
            # Draw border
            pygame.draw.rect(self.screen, (50, 50, 50), 
                            (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height), 1)
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)
        
        # Clean up
        pygame.quit()
        sys.exit()

# Run the game if this script is executed
if __name__ == "__main__":
    game = OneDayApp()
    game.run()
