import time

def pomodoro_timer(work_minutes=25, break_minutes=5):
    """
    Runs a Pomodoro timer cycle.
    
    Args:
        work_minutes (int): Duration of the focused work session.
        break_minutes (int): Duration of the short break.
    """
    print("**************************************")
    print("🚀 Starting Pomodoro Timer!")
    print("**************************************")
    
    # Calculate the number of cycles the user wants (optional)
    # For this example, we will run 4 cycles and then stop.
    total_cycles = 4 
    cycle_count = 0

    while cycle_count < total_cycles:
        cycle_count += 1
        
        # --- Work Session ---
        print(f"\n--- Cycle {cycle_count}: Focus Time ---")
        print(f"⏱️ Work for {work_minutes} minutes. Start the timer now!")
        
        # Countdown for the work session
        time.sleep(work_minutes * 60)
        
        print("✅ Work session finished!")
        
        # --- Break Session ---
        if cycle_count < total_cycles:
            print(f"🧘 Break time! Relax for {break_minutes} minutes.")
            time.sleep(break_minutes * 60)
            print("🎉 Break finished! Time to get back to work.")
        
    print("\n**************************************")
    print("🥳 All Pomodoro cycles completed! Great job!")
    print("**************************************")

# --- Main Program Execution ---

if __name__ == "__main__":
    # Define the parameters (default: 25 min work, 5 min break)
    WORK_TIME = 25  # in minutes
    BREAK_TIME = 5  # in minutes
    
    try:
        pomodoro_timer(WORK_TIME, BREAK_TIME)
    except KeyboardInterrupt:
        print("\n🛑 Timer stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")