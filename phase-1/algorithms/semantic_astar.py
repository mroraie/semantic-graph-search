import heapq
from typing import List, Dict, Any, Callable, Optional, Tuple

def semantic_astar_search(
    graph: Dict[str, List[Tuple[str, float]]],
    start_node: str,
    goal_node: str,
    semantic_similarity: Callable[[str, str], float],
    heuristic: Callable[[str, str], float],
    epsilon: float = 1e-6
) -> Optional[List[str]]:
    """
    Semantic A* Search implementation.
    
    Args:
        graph: Adjacency list representation of the graph.
        start_node: Starting node identifier.
        goal_node: Target node identifier.
        semantic_similarity: Function to calculate similarity between nodes.
        heuristic: Heuristic function estimating cost to goal.
        epsilon: Small value to avoid division by zero.
    """
    open_list = [(0.0, start_node)]
    came_from = {}
    g_score = {start_node: 0.0}
    
    while open_list:
        current_f, current_node = heapq.heappop(open_list)
        
        if current_node == goal_node:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            path.append(start_node)
            return path[::-1]
            
        if current_node not in graph:
            continue
            
        for neighbor, edge_weight in graph[current_node]:
            # استفاده از شباهت معنایی برای تعدیل وزن یال
            similarity = semantic_similarity(neighbor, goal_node)
            semantic_weight = 1.0 / (similarity + epsilon)
            
            tentative_g_score = g_score[current_node] + (edge_weight * semantic_weight)
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal_node)
                heapq.heappush(open_list, (f_score, neighbor))
    
    return None

