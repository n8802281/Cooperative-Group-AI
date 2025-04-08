import numpy as np
import random
from collections import deque

from npc_clustering import cluster_npc_groups
from pygame_running_and_display import GRID_SIZE, MOVES, MODIFY_KEYS, handle_events, update_screen, show_game_over_screen, quit_game
from cooperative_astar import cooperative_astar

MAXIUM_TURNS = 150
MAX_REGROUP_TURN = 10
ENEMY_NUMBER = 20

class GameEnvironment:
    def __init__(self):
        self.player_pos, self.npc_positions = self.generate_positions()
        self.npc_clusters = cluster_npc_groups(self.player_pos, self.npc_positions)
        self.grid = self.generate_map()

        self.player_history = deque(maxlen=10)
        self.player_tendency = self.update_player_tendency()
        
        self.player_delay = 0 
        self.enemy_delay = [0] * ENEMY_NUMBER

        self.point = 0
        self.RemainingTurn = MAXIUM_TURNS
        self.modify_cooldown = 0
        self.clear_cooldown = 0

    def reset_game(self):
        self.player_pos, self.npc_positions = self.generate_positions()
        self.npc_clusters = cluster_npc_groups(self.player_pos, self.npc_positions)
        self.grid = self.generate_map()
        
        self.player_history.clear()
        self.player_tendency = self.update_player_tendency()

        self.player_delay = 0
        self.enemy_delay = [0] * ENEMY_NUMBER
        
        self.point = 0
        self.RemainingTurn = MAXIUM_TURNS
        self.modify_cooldown = 0
        self.clear_cooldown = 0
        
    def generate_positions(self):
        while True:
            player_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            npc_positions = set()
            while len(npc_positions) < ENEMY_NUMBER:
                npc_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
                if npc_pos != player_pos :
                    npc_positions.add(npc_pos)
            return player_pos, list(npc_positions)
            
    def generate_map(self):
        while True:
            grid = np.random.choice(
                ["empty", "mud", "water", "wall"],
                size=(GRID_SIZE, GRID_SIZE),
                p=[0.7, 0.15, 0.1, 0.05]
            )
            grid[self.player_pos] = "empty"
            for npc_pos in self.npc_positions:
                grid[npc_pos] = "empty"
            if self.is_map_valid(grid, self.player_pos, self.npc_positions):
                return grid
                
    def is_map_valid(self,grid, starting_pos, npc_positions):
        queue = deque([starting_pos])
        visited = set([starting_pos])
        while queue:
            x, y = queue.popleft()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[nx, ny] != "wall" and (nx, ny) not in visited:
                    queue.append((nx, ny))
                    visited.add((nx, ny))
        return all(npc in visited for npc in npc_positions) 

    def record_player_position(self):
        self.player_history.append(self.player_pos)
        
    def update_player_tendency(self):
        if len(self.player_history) > 1:
            start_pos = self.player_history[0]
            end_pos = self.player_history[-1]
            move_vector = ((end_pos[0] - start_pos[0]) / len(self.player_history),
                           (end_pos[1] - start_pos[1]) / len(self.player_history))
            return move_vector
        return (1,0)
        
    def update_enemy_position(self):
        self.player_tendency = self.update_player_tendency()
        blocker_target = self.get_blocker_target()
        planned_paths = cooperative_astar(self.grid, self.npc_positions, self.npc_clusters, self.player_pos, blocker_target)
        for npc, new_position in planned_paths.items():
            if npc not in self.npc_positions:
                continue
                
            i = self.npc_positions.index(npc)
            if self.enemy_delay[i] > 0:
                self.enemy_delay[i] -= 1
                continue
            
            for group_name in self.npc_clusters:
                if npc in self.npc_clusters[group_name]:
                    self.npc_clusters[group_name].remove(npc)
                    self.npc_clusters[group_name].append(new_position)
            self.npc_positions[i] = new_position
            
            if abs(new_position[0] - self.player_pos[0]) + abs(new_position[1] - self.player_pos[1]) <= 1:
                self.respawn_enemy(npc)
                self.point -= 100
                
            current_tile = self.grid[new_position[0], new_position[1]]
            if current_tile == "mud":
                self.enemy_delay[i] = 1
            elif current_tile == "water":
                self.enemy_delay[i] = 2
        
    def get_blocker_target(self):
        tendency = self.update_player_tendency()
        predicted_x = round(self.player_pos[0] + 7 * tendency[0])
        predicted_y = round(self.player_pos[1] + 7 * tendency[1])
        return (max(0, min(GRID_SIZE - 1, predicted_x)), max(0, min(GRID_SIZE - 1, predicted_y)))

    def respawn_enemy(self, npc):
        if npc not in self.npc_positions:
            return
        npc_index = self.npc_positions.index(npc)
        
        while True:
            new_x, new_y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            new_position = (new_x, new_y)

            if (self.grid[new_x, new_y] != "wall" and new_position not in self.npc_positions and
                abs(new_x - self.player_pos[0]) + abs(new_y - self.player_pos[1]) > 5): 
                self.npc_positions[npc_index] = new_position

                if self.is_map_valid(self.grid, self.player_pos, self.npc_positions):
                    if self.grid[new_x, new_y] == "mud":
                        self.enemy_delay[npc_index] = 1
                    elif self.grid[new_x, new_y] == "water":
                        self.enemy_delay[npc_index] = 2
                    else:
                        self.enemy_delay[npc_index] = 0
                    self.npc_clusters = cluster_npc_groups(self.player_pos, self.npc_positions)
                    break
                else:
                    self.npc_positions[npc_index] = npc
                    
    def move_player(self, direction):
        self.record_player_position()
        self.player_tendency = self.update_player_tendency()
        if self.player_delay > 0:
            self.player_delay -= 1
            return
        dx, dy = MOVES[direction]
        new_x, new_y = self.player_pos[0] + dx, self.player_pos[1] + dy
        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and self.grid[new_x, new_y] != "wall":
            self.player_pos = (new_x, new_y)
        current_tile = self.grid[new_x][new_y]
        if current_tile == "mud":
            self.player_delay = 1
        elif current_tile == "water":
            self.player_delay = 2     
    
    def enemy_skill(self):
        blocker_target = self.get_blocker_target()
        
        for npc in self.npc_positions:
            if npc in self.npc_clusters["helper"]:
                self.helper_skill(npc, self.player_tendency)
            elif npc in self.npc_clusters["blocker"]:
                self.blocker_skill(npc, blocker_target, self.player_tendency)
    
    def helper_skill(self, npc, player_tendency):
        x, y = npc
        best_target = None
        best_distance = float("inf")
        casted_mud = False
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                if abs(dx) + abs(dy) > 5 or abs(dx) + abs(dy) < 4:
                  continue
                target_x, target_y = self.player_pos[0] + dx, self.player_pos[1] + dy
                if 0 <= target_x < GRID_SIZE and 0 <= target_y < GRID_SIZE:
                    
                    helper_dist = abs(target_x-x) + abs(target_y-y)
                    dot_product = dx * player_tendency[0] + dy * player_tendency[1]
                    
                    if (dot_product >= 0 and helper_dist <= 5 and
                        self.grid[target_x, target_y] == "empty" and
                        (target_x, target_y) not in self.npc_positions and
                        abs(dx) + abs(dy) < best_distance):
                        best_target = (target_x, target_y)
                        best_distance = abs(dx) + abs(dy)
        
        if best_target:
            self.helper_set_mud(best_target)
            self.enemy_delay[self.npc_positions.index(npc)] = 1
            casted_mud = True

        if casted_mud == False:
          best_target = None
          best_distance = float("inf")
          for dx in range(-5, 6):
            for dy in range(-5, 6):
                if abs(dx) + abs(dy) > 5:
                  continue
                target_x, target_y = self.player_pos[0] + dx, self.player_pos[1] + dy
                if 0 <= target_x < GRID_SIZE and 0 <= target_y < GRID_SIZE:
                    
                    helper_dist = abs(target_x-x) + abs(target_y-y)
                    dot_product =dx * player_tendency[0] + dy * player_tendency[1]
                    
                    if (dot_product < 0 and helper_dist <= 5 and
                        self.grid[target_x, target_y] in ["mud", "water"] and
                        (target_x, target_y) not in self.npc_positions and
                        abs(dx) + abs(dy) < best_distance):
                        best_target = (target_x, target_y)
                        best_distance = abs(dx) + abs(dy)
          if best_target:
            self.helper_clear_terrain(best_target) 
            
    def helper_set_mud(self, position):
        self.grid[position] = "mud"
    
    def helper_clear_terrain(self, position):
        if self.grid[position] == "water":
            self.grid[position] = "mud"
        elif self.grid[position] == "mud":
            self.grid[position] = "empty"
          
    def blocker_skill(self, npc, blocker_target, player_tendency):
        x, y = npc
        best_target = None
        best_score = -float("inf")
        
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                if abs(dx) + abs(dy) > 5:
                  continue
                target_x, target_y = blocker_target[0] + dx, blocker_target[1] + dy
                blocker_dist = abs(target_x-x) + abs(target_y-y)
                if (0 <= target_x < GRID_SIZE and 0 <= target_y < GRID_SIZE and 
                    self.grid[target_x, target_y] != "wall" and
                    blocker_dist<=5):
                    
                    score = -abs(target_x - blocker_target[0]) - abs(target_y - blocker_target[1])
                    if self.grid[target_x, target_y] == "empty":
                        score += 3
                    if score > best_score:
                        best_target = (target_x, target_y)
                        best_score = score
        
        if best_target and best_target != self.player_pos:
            self.grid[best_target] = "wall"
            if not self.is_map_valid(self.grid, self.player_pos, self.npc_positions):
                self.grid[best_target] = "empty" 
            self.enemy_delay[self.npc_positions.index(npc)] = 1

    def create_mud_field(self, direction):
        if self.modify_cooldown > 0:
            return
        
        dx, dy = MODIFY_KEYS[direction]
        start_x, start_y = self.player_pos[0] + dx, self.player_pos[1] + dy
        
        for depth in range(3): 
            for width in range(-2, 3): 
                target_x = start_x + width if dx == 0 else start_x + depth * dx
                target_y = start_y + width if dy == 0 else start_y + depth * dy
                
                if 0 <= target_x < GRID_SIZE and 0 <= target_y < GRID_SIZE:
                    if self.grid[target_x, target_y] == "empty":
                        self.grid[target_x, target_y] = "mud"
                        if (target_x, target_y) in self.npc_positions:
                            npc_index = self.npc_positions.index((target_x, target_y))
                            self.enemy_delay[npc_index] += 1
        self.modify_cooldown = 5
        
    def clear_nearby_area(self):
        if self.clear_cooldown > 0:
            return
        affected_positions = []
        
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                target_x, target_y = self.player_pos[0] + dx, self.player_pos[1] + dy
                if 0 <= target_x < GRID_SIZE and 0 <= target_y < GRID_SIZE:
                    affected_positions.append((target_x, target_y))
        
        for pos in affected_positions:
            if 0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE:
                if pos in self.npc_positions:
                    self.point += 50
                    self.respawn_enemy(pos)
                self.grid[pos[0], pos[1]] = "empty"
        
        self.clear_cooldown = 5
    
    def run(self):
        running = True
        turn_count = 0
        while running:
            running, last_move, modify_skill, last_modify_move, clear_skill = handle_events()
            if not running:
                break
            if last_move:
                self.move_player(last_move)
            if modify_skill:
                self.create_mud_field(last_modify_move)
            if clear_skill:
                self.clear_nearby_area()

            self.update_enemy_position()
            self.enemy_skill()

            if turn_count >= MAX_REGROUP_TURN:
                self.npc_clusters = cluster_npc_groups(self.player_pos, self.npc_positions)
                turn_count = 0

            self.point += 1
            turn_count += 1
            self.modify_cooldown = max(0, self.modify_cooldown - 1)
            self.clear_cooldown = max(0, self.clear_cooldown - 1)
            self.RemainingTurn = max(0, self.RemainingTurn - 1)
            
            if self.RemainingTurn == 0:
                if show_game_over_screen(self.point):
                    self.reset_game()
                    continue
                else:
                    break
            update_screen(self.grid, self.player_pos, self.npc_positions, self.npc_clusters, self.enemy_delay, self.modify_cooldown, self.clear_cooldown, self.point, self.RemainingTurn)
        quit_game()

if __name__ == "__main__":
    game = GameEnvironment()
    game.run()
