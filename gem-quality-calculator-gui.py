import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List, Dict, Set
from collections import defaultdict

class GemQualityCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PoE Gem Quality Calculator")
        self.root.geometry("1000x400")
        
        # Configure dark theme colors
        self.accent_blue = "#4b6eaf"
        self.dark_bg = "#2b2b2b"
        self.darker_bg = "#1e1e1e"
        self.input_bg = "#3c3f41"
        self.button_bg = "#4a4a4a"  # Darker grey button background
        self.button_hover_bg = "#5a5a5a"  # Button hover color
        
        # Round window corners (Windows only)
        try:
            from ctypes import windll
            hwnd = windll.user32.GetParent(root.winfo_id())
            style = windll.user32.GetWindowLongW(hwnd, -20)
            style = style & ~0x00C00000 | 0x00080000
            windll.user32.SetWindowLongW(hwnd, -20, style)
        except:
            pass  # Skip if not on Windows or if it fails
        
        self.style = ttk.Style()
        self.style.configure(".", 
            background=self.dark_bg,
            foreground="#ffffff",
            fieldbackground=self.input_bg,
            troughcolor=self.darker_bg,
            selectbackground=self.accent_blue,
            selectforeground="#ffffff"
        )
        self.style.configure("TFrame", background=self.dark_bg)
        self.style.configure("TLabel", background=self.dark_bg, foreground="#ffffff", font=("Arial", 12))
        self.style.configure("TButton", 
            background=self.button_bg,
            foreground="#000000",
            padding=8,  # Increased padding
            font=("Arial", 10)  # Changed font size
        )
        self.style.map('TButton',
            background=[('active', self.button_hover_bg), ('pressed', self.button_hover_bg)],
            foreground=[('active', '#0d22bd'), ('pressed', '#0d22bd')]
        )
        self.style.configure("Title.TLabel", 
            font=('Arial', 16, 'bold'),  # Increased title font size
            background=self.dark_bg,
            foreground=self.accent_blue,
            padding=10
        )
        
        # Configure root window
        self.root.configure(bg=self.dark_bg)
        
        # Create main container
        self.main_container = ttk.Frame(root, padding="20")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights for responsiveness
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Create frames
        self.input_frame = ttk.Frame(self.main_container, padding="10")
        self.input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.output_frame = ttk.Frame(self.main_container, padding="10")
        self.output_frame.grid(row=0, column=1, sticky="nsew")
        
        self.gem_counts = {}
        self.create_input_panel()
        self.create_output_panel()
        
    def create_input_panel(self):
        # Title for input section
        ttk.Label(self.input_frame, text="Gem Inventory by Quality", style="Title.TLabel").grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Create a grid layout for gem quality inputs (5 columns)
        cols = 5
        for i in range(20):
            quality = i + 1
            row = (i // cols) + 1
            col = (i % cols) * 2
            
            # Quality label
            ttk.Label(self.input_frame, 
                     text=f"{quality}%:",  # Removed the word "Quality"
                     padding=(5, 2)).grid(row=row, column=col, padx=5, pady=5, sticky="e")
            
            # Spinbox with custom styling
            count_var = tk.StringVar(value="0")
            spinbox = ttk.Spinbox(
                self.input_frame,
                from_=0,
                to=99,
                width=3,
                textvariable=count_var
            )
            spinbox.grid(row=row, column=col + 1, padx=5, pady=5, sticky="w")
            
            # Configure spinbox colors
            spinbox.configure(style="Custom.TSpinbox")
            spinbox.configure(background=self.input_bg, foreground="#000000")
            
            self.gem_counts[quality] = count_var
            
        # Button frame
        button_frame = ttk.Frame(self.input_frame)
        button_frame.grid(row=21, column=0, columnspan=8, pady=20)
        
        # Add buttons with improved styling
        ttk.Button(button_frame, 
                  text="Find Combinations",
                  command=self.calculate,
                  style="TButton").grid(row=0, column=0, padx=5)
                  
        ttk.Button(button_frame,
                  text="Clear All",
                  command=self.clear_all,
                  style="TButton").grid(row=0, column=1, padx=5)
        
    def create_output_panel(self):
        # Title for output section
        ttk.Label(self.output_frame, text="Results", style="Title.TLabel").grid(row=0, column=0, pady=(0, 10))
        
        # Create text frame for results with custom styling
        self.output_text = tk.Text(
            self.output_frame,
            wrap=tk.WORD,  # Enable word wrapping
            width=50,
            height=30,
            bg=self.darker_bg,
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground=self.accent_blue,
            selectforeground="#ffffff",
            font=("Consolas", 10),
            padx=10,
            pady=10,
            relief="flat",  # Remove border
            highlightthickness=0  # Remove highlight border
        )
        self.output_text.grid(row=1, column=0, sticky="nsew")
        
        # Create scrollbar that only appears when needed
        scrollbar = ttk.Scrollbar(self.output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=self.scroll_command(scrollbar))
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.output_frame.grid_rowconfigure(1, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)

    def scroll_command(self, scrollbar):
        def set_scroll(*args):
            # Only show scrollbar if content exceeds visible area
            if float(args[1]) < 1:
                scrollbar.grid()
            else:
                scrollbar.grid_remove()
            scrollbar.set(*args)
        return set_scroll

    def clear_all(self):
        for var in self.gem_counts.values():
            var.set("0")
        self.output_text.delete(1.0, tk.END)
        
    def find_all_combinations(self, inventory: Dict[int, int], target: int = 40) -> List[Dict[int, int]]:
        def combine_results(current_sum: int, remaining_items: List[tuple], current_combo: Dict[int, int], 
                          all_results: List[Dict[int, int]], seen_sums: Set[int]):
            if current_sum == target:
                all_results.append(current_combo.copy())
                return
            
            if current_sum > target or not remaining_items:
                return
                
            quality, max_count = remaining_items[0]
            next_items = remaining_items[1:]
            
            for count in range(max_count + 1):
                new_sum = current_sum + (quality * count)
                if new_sum > target or new_sum in seen_sums:
                    continue
                    
                seen_sums.add(new_sum)
                if count > 0:
                    current_combo[quality] = count
                combine_results(new_sum, next_items, current_combo, all_results, seen_sums)
                if count > 0:
                    del current_combo[quality]
                    
        items = [(q, c) for q, c in inventory.items() if c > 0]
        results = []
        combine_results(0, items, {}, results, set())
        return results
        
    def calculate(self):
        inventory = {}
        for quality, var in self.gem_counts.items():
            count = int(var.get())
            if count > 0:
                inventory[quality] = count
                
        if not inventory:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Please add some gems to your inventory first.")
            return
            
        combinations = self.find_all_combinations(inventory)
        
        self.output_text.delete(1.0, tk.END)
        if combinations:
            # Insert title with custom tag
            self.output_text.tag_configure("title", foreground=self.accent_blue, font=("Arial", 12, "bold"))
            self.output_text.insert(tk.END, f"Found {len(combinations)} combination(s) that sum to exactly 40 quality:\n\n", "title")
            
            for i, combo in enumerate(combinations, 1):
                self.output_text.insert(tk.END, f"Combination {i}:\n")
                for quality, count in sorted(combo.items()):
                    self.output_text.insert(tk.END, f"  {count}x {quality}% quality gems\n")
                self.output_text.insert(tk.END, "\n")
        else:
            self.output_text.insert(tk.END, "No combinations found that add up to exactly 40 quality.")

def main():
    root = tk.Tk()
    app = GemQualityCalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
