import tkinter as tk
from typing import List, Tuple

# Sample Flash Card Data
FLORENCE_DATA = [
    ("What is the capital of France?", "Paris"),
    ("Who wrote 'Hamlet'?", "William Shakespeare"),
    ("What is the CSS property to remove list bullets?", "list-style-type: none;"), 
]

def create_card_ui(container, data_list):
    """Creates a Tkinter GUI for flashcards"""
    
    # Track the current card index using a dictionary wrapper for simple state management
    state = {"current_index": 0, "showing_answer": False}

    # Create a frame to hold the card elements and display it
    card_container = tk.Frame(container)
    card_container.pack(pady=20)

    # Label to show the text
    label = tk.Label(card_container, font=('Arial', 16), text="Click 'Start' to Begin", wraplength=400)
    label.grid(row=0, column=0, pady=20)

    def engine_loop():
        """Handles updating the text on screen dynamically based on state"""
        idx = state["current_index"]
        
        # Check if we have run out of cards
        if idx >= len(data_list):
            label.config(text="🎉 All cards completed!")
            action_btn.config(text="Restart", command=reset_deck)
            return

        current_card = data_list[idx]

        if not state["showing_answer"]:
            # Display Question state
            label.config(text=f"Question:\n\n{current_card[0]}")
            action_btn.config(text="Show Answer")
            state["showing_answer"] = True
        else:
            # Display Answer state
            label.config(text=f"Answer:\n\n{current_card[1]}")
            action_btn.config(text="Next Card")
            state["showing_answer"] = False
            state["current_index"] += 1

    def reset_deck():
        """Resets application track index to zero"""
        state["current_index"] = 0
        state["showing_answer"] = False
        engine_loop()

    # The single execution action button
    action_btn = tk.Button(container, text="Start", width=12, height=2, command=engine_loop)
    action_btn.pack(pady=10)

def main():
    app_var = "App Var"  # Placeholder for dynamic state management

    root = tk.Tk()
    root.title("Flashcard App")
    root.geometry("450x300")

    # Fixed: Changed tkinter.Frame to tk.Frame
    container = tk.Frame(root)
    container.pack(fill="both", expand=True)

    # Fixed: Synced the function names together 
    create_card_ui(container, FLORENCE_DATA)

    root.mainloop()

if __name__ == "__main__": 
    main()
