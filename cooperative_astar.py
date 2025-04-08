import heapq

def astar_search(grid, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor in get_neighbors(grid, current):
            terrain_cost = get_terrain_cost(grid, neighbor)
            tentative_g_score = g_score[current] + terrain_cost
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

# 曼哈頓距離作為啟發式函數
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# 取得相鄰節點
def get_neighbors(grid, node):
    x, y = node
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] != "wall":
            neighbors.append((nx, ny))
    return neighbors

# 計算不同地形的通行成本
def get_terrain_cost(grid, pos):
    terrain_weights = {"empty": 1, "mud": 2, "water": 3, "wall": float("inf")}
    return terrain_weights.get(grid[pos[0]][pos[1]], 1)

# 重建最短路徑
def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    return path[::-1]

def cooperative_astar(grid, npc_positions, clustered_npcs, player_position, blocker_target):
    planned_paths = {}
    occupied_positions = set(npc_positions)
    target_positions = {
        "chaser": player_position,
        "helper": player_position,
        "blocker": blocker_target
    }
    for group_name, npc_group in clustered_npcs.items():
        for npc in npc_group:
            if npc in target_positions[group_name]:
                planned_paths[npc] = npc
                continue

            path = astar_search(grid, npc, target_positions[group_name]) 
            if not path:
                planned_paths[npc] = npc
                continue
  
            if group_name == "helper" and len(path) < 3:
                next_pos = npc
            elif group_name == "blocker" and len(path) >= 2:
                next_pos = path[1]
            else:
                next_pos = path[0]
            
            if next_pos not in occupied_positions:
                planned_paths[npc] = next_pos
                occupied_positions.add(next_pos)
            else:
                planned_paths[npc] = npc
    return planned_paths
