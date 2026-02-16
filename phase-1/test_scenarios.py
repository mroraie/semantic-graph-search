import json

# تعریف دامنه‌ای دستی (Manual Domain Mapping)
DOMAIN_KNOWLEDGE = {
    "CPU": {"processor": 0.9, "hardware": 0.7, "silicon": 0.5},
    "processor": {"CPU": 0.9, "hardware": 0.8, "logic gate": 0.4},
    "hardware": {"CPU": 0.7, "processor": 0.8, "RAM": 0.6, "monitor": 0.4},
    "RAM": {"memory": 0.9, "hardware": 0.7},
    "memory": {"RAM": 0.9, "storage": 0.7},
    "storage": {"SSD": 0.9, "HDD": 0.8, "memory": 0.7},
    "SSD": {"storage": 0.9, "hardware": 0.6},
    "monitor": {"display": 0.9, "hardware": 0.5},
    "display": {"monitor": 0.9, "pixels": 0.7},
    "GPU": {"graphics": 0.9, "hardware": 0.7, "processor": 0.6}
}

def get_manual_similarity(concept1, concept2):
    """
    تابع شباهت دستی بر اساس دامنه تعریف شده
    """
    if concept1 == concept2:
        return 1.0
    
    # چک کردن هر دو جهت در دیکشنری
    sim1 = DOMAIN_KNOWLEDGE.get(concept1, {}).get(concept2, 0.0)
    sim2 = DOMAIN_KNOWLEDGE.get(concept2, {}).get(concept1, 0.0)
    
    return max(sim1, sim2)

class SimpleSemanticGraph:
    def __init__(self, threshold=0.5):
        self.nodes = set()
        self.edges = {}
        self.threshold = threshold

    def build_from_concepts(self, concepts):
        self.nodes = set(concepts)
        for c1 in concepts:
            for c2 in concepts:
                if c1 != c2:
                    sim = get_manual_similarity(c1, c2)
                    if sim >= self.threshold:
                        if c1 not in self.edges: self.edges[c1] = []
                        self.edges[c1].append((c2, sim))

    def has_path(self, start, goal, visited=None):
        if visited is None: visited = set()
        if start == goal: return True
        visited.add(start)
        
        for neighbor, _ in self.edges.get(start, []):
            if neighbor not in visited:
                if self.has_path(neighbor, goal, visited):
                    return True
        return False

def run_tests():
    test_cases = [
        {"name": "Direct Relation", "concepts": ["CPU", "processor"], "start": "CPU", "goal": "processor", "expected": True},
        {"name": "Chain Relation", "concepts": ["CPU", "processor", "hardware"], "start": "CPU", "goal": "hardware", "expected": True},
        {"name": "Long Chain", "concepts": ["CPU", "hardware", "RAM", "memory"], "start": "CPU", "goal": "memory", "expected": True},
        {"name": "Disconnected Concepts", "concepts": ["CPU", "monitor"], "start": "CPU", "goal": "monitor", "expected": False}, # threshold dependency
        {"name": "Storage Hierarchy", "concepts": ["SSD", "storage", "memory", "RAM"], "start": "SSD", "goal": "RAM", "expected": True},
        {"name": "No Path (Isolated)", "concepts": ["CPU", "processor", "garden"], "start": "CPU", "goal": "garden", "expected": False},
        {"name": "Full Hardware Loop", "concepts": ["CPU", "processor", "hardware", "RAM", "monitor"], "start": "monitor", "goal": "CPU", "expected": True},
        {"name": "Graphics Path", "concepts": ["GPU", "graphics", "display", "monitor"], "start": "GPU", "goal": "monitor", "expected": True},
        {"name": "Self Loop", "concepts": ["CPU"], "start": "CPU", "goal": "CPU", "expected": True},
        {"name": "Threshold Filter", "concepts": ["processor", "logic gate"], "start": "processor", "goal": "logic gate", "expected": False}, # 0.4 < 0.5
    ]

    print(f"{'Test Name':<25} | {'Result':<10} | {'Expected'}")
    print("-" * 50)
    
    passed = 0
    for case in test_cases:
        graph = SimpleSemanticGraph(threshold=0.5)
        graph.build_from_concepts(case["concepts"])
        result = graph.has_path(case["start"], case["goal"])
        
        status = "✅ PASS" if result == case["expected"] else "❌ FAIL"
        if result == case["expected"]: passed += 1
        
        print(f"{case['name']:<25} | {str(result):<10} | {case['expected']} {status}")

    print("-" * 50)
    print(f"Total Passed: {passed}/10")

def test_graph_logic():
    test_cases = [
        {"name": "Direct Relation", "concepts": ["CPU", "processor"], "start": "CPU", "goal": "processor", "expected": True},
        {"name": "Chain Relation", "concepts": ["CPU", "processor", "hardware"], "start": "CPU", "goal": "hardware", "expected": True},
        {"name": "Long Chain", "concepts": ["CPU", "hardware", "RAM", "memory"], "start": "CPU", "goal": "memory", "expected": True},
        {"name": "Disconnected Concepts", "concepts": ["CPU", "monitor"], "start": "CPU", "goal": "monitor", "expected": False},
        {"name": "Storage Hierarchy", "concepts": ["SSD", "storage", "memory", "RAM"], "start": "SSD", "goal": "RAM", "expected": True},
        {"name": "No Path (Isolated)", "concepts": ["CPU", "processor", "garden"], "start": "CPU", "goal": "garden", "expected": False},
        {"name": "Full Hardware Loop", "concepts": ["CPU", "processor", "hardware", "RAM", "monitor"], "start": "monitor", "goal": "CPU", "expected": True},
        {"name": "Graphics Path", "concepts": ["GPU", "graphics", "display", "monitor"], "start": "GPU", "goal": "monitor", "expected": True},
        {"name": "Self Loop", "concepts": ["CPU"], "start": "CPU", "goal": "CPU", "expected": True},
        {"name": "Threshold Filter", "concepts": ["processor", "logic gate"], "start": "processor", "goal": "logic gate", "expected": False},
    ]

    for case in test_cases:
        graph = SimpleSemanticGraph(threshold=0.5)
        graph.build_from_concepts(case["concepts"])
        result = graph.has_path(case["start"], case["goal"])
        assert result == case["expected"], f"Failed test {case['name']}"

if __name__ == "__main__":
    run_tests()

