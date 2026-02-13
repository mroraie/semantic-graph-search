from django.shortcuts import render

from phase_2.src.semantic_graph import SemanticGraph
from phase_2.src.similarity import LMStudioSimilarity
from phase_2.src.analysis import AlgorithmComplexityAnalyzer, GraphMetrics

from django.http import JsonResponse
import requests
import time
import tracemalloc

SCENARIOS = {
    # --- سناریوهای ساده (۴ عدد) ---
    "fruits_easy": {
        "name": "میوه‌ها (ساده)",
        "concepts": "سیب, پرتقال, موز, انبه, انگور, میوه",
        "start": "سیب",
        "goal": "میوه",
        "desc": "روابط سلسله‌مراتبی مستقیم."
    },
    "transport_easy": {
        "name": "حمل و نقل (ساده)",
        "concepts": "ماشین, دوچرخه, اتوبوس, قطار, وسیله نقلیه",
        "start": "ماشین",
        "goal": "وسیله نقلیه",
        "desc": "مسیر مستقیم حمل و نقل."
    },
    "colors_easy": {
        "name": "رنگ‌ها (ساده)",
        "concepts": "قرمز, آبی, سبز, زرد, رنگ, طیف",
        "start": "قرمز",
        "goal": "رنگ",
        "desc": "ارتباط دسته‌ای پایه."
    },
    "family_easy": {
        "name": "خانواده (ساده)",
        "concepts": "پدر, مادر, فرزند, برادر, خواهر, خانواده",
        "start": "فرزند",
        "goal": "خانواده",
        "desc": "سلسله‌مراتب خانوادگی."
    },
    # --- سناریوهای متوسط (۴ عدد) ---
    "ai_medium": {
        "name": "هوش مصنوعی (متوسط)",
        "concepts": "هوش مصنوعی, یادگیری ماشین, یادگیری عمیق, شبکه های عصبی, داده, الگوریتم, پردازنده گرافیکی, آموزش",
        "start": "هوش مصنوعی",
        "goal": "پردازنده گرافیکی",
        "desc": "حوزه تکنولوژی با وابستگی‌های چندگانه."
    },
    "web_medium": {
        "name": "توسعه وب (متوسط)",
        "concepts": "فرانت اند, بک اند, پایگاه داده, رابط برنامه نویسی, ریکت, نود جی اس, مرورگر, سرور",
        "start": "فرانت اند",
        "goal": "سرور",
        "desc": "مسیر توسعه وب کامل."
    },
    "eco_medium": {
        "name": "محیط زیست (متوسط)",
        "concepts": "درخت, جنگل, اکسیژن, فتوسنتز, خورشید, حیات, اتمسفر, گرمایش جهانی",
        "start": "خورشید",
        "goal": "گرمایش جهانی",
        "desc": "روابط علمی زیست‌محیطی."
    },
    "disconnected_edge": {
        "name": "گره ایزوله (Edge Case)",
        "concepts": "تهران, اصفهان, شیراز, تبریز, کهکشان آندرومدا",
        "start": "تهران",
        "goal": "کهکشان آندرومدا",
        "desc": "تست حالتی که هیچ مسیری وجود ندارد."
    },
    # --- سناریوهای سخت (۲ عدد) ---
    "cross_domain_hard": {
        "name": "ترکیبی پیچیده (سخت)",
        "concepts": "بازی, گرافیک, موتور فیزیک, هوش مصنوعی, شبکه های عصبی, ریاضیات, منطق, سخت افزار, سیلیکون, معدن",
        "start": "بازی",
        "goal": "معدن",
        "desc": "ارتباط بین حوزه‌های کاملاً متفاوت."
    },
    "dense_worst_case": {
        "name": "گراف متراکم (Worst-Case)",
        "concepts": "کلمه۱, کلمه۲, کلمه۳, کلمه۴, کلمه۵, کلمه۶, کلمه۷, کلمه۸, کلمه۹, کلمه۱۰",
        "start": "کلمه۱",
        "goal": "کلمه۱۰",
        "desc": "تعداد یال‌های زیاد برای فشار به الگوریتم."
    }
}

def llm_status(request):
    """Checks if LM Studio is alive."""
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        return JsonResponse({"ok": response.status_code == 200})
    except:
        return JsonResponse({"ok": False})

import time

def index(request):
    """
    Main demo page with test scenarios support and performance monitoring.
    """
    # Get theoretical complexity data
    complexity_data = AlgorithmComplexityAnalyzer.get_all_analyses()
    
    context = {
        "concepts_input": "",
        "start": "",
        "goal": "",
        "use_llm": False,
        "threshold": 0.65,
        "top_k": 3,
        "path": None,
        "error": None,
        "scenarios": SCENARIOS,
        "algorithm": "dijkstra",
        "performance": None,
        "complexity_data": complexity_data,
        "graph_metrics": None
    }

    if request.method == "POST":
        tracemalloc.start()
        scenario_key = request.POST.get("scenario")
        
        # 1. Parse Inputs & Validation
        try:
            threshold = float(request.POST.get("threshold", 0.65))
            top_k = int(request.POST.get("top_k", 3))
            algorithm = request.POST.get("algorithm", "dijkstra")
            sim_mode = request.POST.get("sim_mode", "rule") # rule, llm, matrix
            
            # Algorithm specific params
            max_depth = request.POST.get("max_depth")
            max_depth = int(max_depth) if max_depth else None
            min_similarity_param = request.POST.get("min_similarity_param")
            min_similarity_param = float(min_similarity_param) if min_similarity_param else threshold
        except ValueError as e:
            return render(request, "graphdemo/index.html", {**context, "error": f"خطا در پارامترهای عددی: {str(e)}"})

        if scenario_key in SCENARIOS:
            s = SCENARIOS[scenario_key]
            concepts_input = s["concepts"]
            start = s["start"]
            goal = s["goal"]
            use_llm = (sim_mode == "llm")
        else:
            concepts_input = request.POST.get("concepts", "")
            start = request.POST.get("start", "").strip()
            goal = request.POST.get("goal", "").strip()
            use_llm = (request.POST.get("sim_mode") == "llm")

        concepts = [c.strip() for c in concepts_input.split(",") if c.strip()]
        
        # Validation: check mandatory inputs
        if not concepts or len(concepts) < 2:
            context.update({"error": "حداقل دو مفهوم وارد کنید.", "concepts_input": concepts_input})
            return render(request, "graphdemo/index.html", context)
        if not start or not goal:
            context.update({"error": "مبدأ و مقصد نمی‌توانند خالی باشند.", "concepts_input": concepts_input})
            return render(request, "graphdemo/index.html", context)
        if start not in concepts or goal not in concepts:
            context.update({"error": "مبدأ و مقصد باید در لیست مفاهیم باشند.", "concepts_input": concepts_input, "start": start, "goal": goal})
            return render(request, "graphdemo/index.html", context)

        context.update({
            "concepts_input": concepts_input,
            "start": start,
            "goal": goal,
            "sim_mode": sim_mode,
            "threshold": threshold,
            "top_k": top_k,
            "algorithm": algorithm,
            "max_depth": max_depth,
            "min_similarity_param": min_similarity_param
        })

        try:
            # 2. Graph Construction
            start_graph = time.perf_counter()
            graph = SemanticGraph(similarity_threshold=threshold)
            
            # Similarity Function/Matrix logic
            if sim_mode == "matrix":
                # Implementation for matrix input if provided (simplified for demo)
                pass 
            
            def get_sim(a, b):
                if sim_mode == "llm":
                    llm_sim = LMStudioSimilarity()
                    return llm_sim.compute_similarity(a, b)
                else:
                    common = set(a.lower()) & set(b.lower())
                    return len(common) / max(len(set(a.lower())), 1)

            for i, concept in enumerate(concepts):
                similarities = []
                for j, other in enumerate(concepts):
                    if i == j: continue
                    sim = get_sim(concept, other)
                    if sim >= threshold:
                        similarities.append((other, sim))
                
                similarities.sort(key=lambda x: x[1], reverse=True)
                for target, sim in similarities[:top_k]:
                    graph.add_bidirectional_edge(concept, target, sim)
            
            end_graph = time.perf_counter()
            graph_time = (end_graph - start_graph) * 1000

            # 3. Execution & Performance
            context["graph_metrics"] = GraphMetrics.analyze_graph_structure(graph)
            cost, path = None, None
            nodes_visited = 0
            start_algo = time.perf_counter()

            if algorithm == "dijkstra":
                cost, path = graph.dijkstra(start, goal, min_similarity=min_similarity_param)
                nodes_visited = len(path) if path else 0
            elif algorithm == "a_star":
                # Default heuristic: 0 (Manhattan/Euclidean not applicable to words without vectors)
                cost, path = graph.a_star(start, goal, min_similarity=min_similarity_param)
                nodes_visited = len(path) if path else 0
            elif algorithm == "bfs":
                path = graph.bfs(start, max_depth=max_depth, min_similarity=min_similarity_param)
                # BFS in semantic_graph returns all reachable if goal not found, 
                # so we need to filter/re-check if goal is reached
                if goal in path:
                    # find actual path (simplified here, in real app we'd use the search results)
                    idx = path.index(goal)
                    path = path[:idx+1]
                    cost = 1.0
                else:
                    path = None
                nodes_visited = len(path) if path else 0
            elif algorithm == "floyd_warshall":
                dist, next_hop = graph.floyd_warshall(min_similarity=min_similarity_param)
                path = graph.reconstruct_path(start, goal, next_hop)
                cost = dist.get((start, goal), 0) if path else None
                nodes_visited = len(graph.nodes)

            end_algo = time.perf_counter()
            algo_time = (end_algo - start_algo) * 1000
            
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            stats = graph.get_statistics()
            context["performance"] = {
                "graph_construction_ms": f"{graph_time:.2f}",
                "algorithm_execution_ms": f"{algo_time:.2f}",
                "total_ms": f"{(time.perf_counter() - start_total)*1000:.2f}",
                "num_nodes": stats["num_nodes"],
                "num_edges": stats["num_edges"],
                "nodes_visited": nodes_visited,
                "memory_kb": f"{peak_mem / 1024:.2f}"
            }

            except Exception as e:
                tracemalloc.stop()
                context["error"] = f"Error: {str(e)}"
                return render(request, "graphdemo/index.html", context)

            if path:
                context["path"] = path
                context["cost"] = f"{cost:.4f}" if cost is not None else "N/A"
            else:
                context["error"] = "No semantic path found between these concepts."

    return render(request, "graphdemo/index.html", context)

    return render(request, "graphdemo/index.html", context)


