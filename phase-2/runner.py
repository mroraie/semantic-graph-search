import os
import sys
import subprocess

def run_cmd(command, cwd=None):
    print(f"\n> Executing: {command}")
    # Add current directory to PYTHONPATH so phase_2 is visible
    env = os.environ.copy()
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")
    
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd, env=env)
        return True
    except Exception as e:
        print(f"\n[Error] Command failed: {e}")
        return False

def main_menu():
    # Setup paths relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(base_dir, "demo_web")
    python = sys.executable

    stages = [
        ("Install Requirements", f'"{python}" -m pip install numpy requests django networkx matplotlib'),
        ("Database Migration", f'"{python}" manage.py migrate'),
        ("Start Web Server", f'"{python}" manage.py runserver')
    ]

    while True:
        print("\n" + "="*30)
        print("   PHASE 2 SYSTEM RUNNER")
        print("="*30)
        for i, (name, _) in enumerate(stages, 1):
            print(f"{i}. {name}")
        print("4. Run All Stages (Full Setup)")
        print("5. Exit")
        
        try:
            choice = input("\nSelect an option (1-5): ").strip()
        except KeyboardInterrupt:
            break

        if choice == '1':
            run_cmd(stages[0][1])
        elif choice == '2':
            run_cmd(stages[1][1], cwd=web_dir)
        elif choice == '3':
            print("\n[Reminder] Ensure LM Studio is running on port 1234 if using LLM mode.")
            run_cmd(stages[2][1], cwd=web_dir)
        elif choice == '4':
            print("\nStarting Full Automated Setup...")
            # 1. Install
            if not run_cmd(stages[0][1]): continue
            # 2. Migrate
            if not run_cmd(stages[1][1], cwd=web_dir): continue
            # 3. Server
            print("\n[Reminder] Ensure LM Studio is running on port 1234 if using LLM mode.")
            run_cmd(stages[2][1], cwd=web_dir)
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
