import os
import sys
import subprocess
import argparse

# تنظیم مسیر پروژه برای اطمینان از کارکرد ایمپورت‌ها
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

# لیست اسکریپت‌های تحلیل عملکرد
SCRIPTS = [
    "benchmark_scaling.py",
    "generate_algorithm_comparison_chart.py",
    "generate_big_o_comparison_chart.py",
    "generate_perf_chart.py",
    "generate_time_growth_chart.py"
]

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

def run_script(script_name):
    script_path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"Error: Script {script_name} not found at {script_path}")
        return

    print(f"\n--- Running {script_name} ---")
    
    # تنظیم محیط اجرا برای اطمینان از پیدا شدن پکیج phase_2
    env = os.environ.copy()
    project_root = os.path.dirname(os.path.dirname(SCRIPT_DIR))
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = project_root + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = project_root

    try:
        result = subprocess.run([sys.executable, script_path, "--output", OUTPUT_DIR], check=True, env=env)
        print(f"Successfully finished {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Performance Analysis Runner")
    parser.add_argument("--script", type=str, help="Run a specific script (e.g., benchmark_scaling.py)")
    parser.add_argument("--list", action="store_true", help="List all available scripts")
    
    args = parser.parse_args()

    ensure_output_dir()

    if args.list:
        print("Available scripts:")
        for s in SCRIPTS:
            print(f"  - {s}")
        return

    if args.script:
        if args.script in SCRIPTS:
            run_script(args.script)
        else:
            # جستجوی تقریبی اگر پسوند .py وارد نشده باشد
            found = False
            for s in SCRIPTS:
                if args.script in s:
                    run_script(s)
                    found = True
                    break
            if not found:
                print(f"Error: Script '{args.script}' not recognized.")
    else:
        print("No specific script specified. Running ALL scripts...")
        for s in SCRIPTS:
            run_script(s)

if __name__ == "__main__":
    main()

