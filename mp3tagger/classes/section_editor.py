import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional


class SectionEditor:
    def __init__(self, parent: tk.Tk, sections_data: List[Dict[str, Any]], save_callback) -> None:
        """
        Creates a new window for editing sections data.

        Args:
            parent: Parent window
            sections_data: List of section dictionaries to edit
            save_callback: Function to call when saving sections
        """
        self.parent = parent
        self.original_data = sections_data.copy()
        self.save_callback = save_callback

        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title("Section Data Editor")
        self.window.geometry("800x600")

        # Configure dark theme colors
        self.bg_color = '#333333'
        self.fg_color = 'white'
        self.button_bg = '#444444'
        self.entry_bg = '#2d2d2d'

        self.window.configure(bg=self.bg_color)

        # Configure ttk styles
        self.style = ttk.Style()
        self.style.configure('Dark.TFrame', background=self.bg_color)
        self.style.configure(
            'Dark.TLabelframe', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('Dark.TLabelframe.Label',
                             background=self.bg_color, foreground=self.fg_color)
        self.style.configure(
            'Dark.TButton', background=self.button_bg, foreground=self.fg_color)
        self.style.configure(
            'Dark.TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure(
            'Dark.TEntry', fieldbackground=self.entry_bg, foreground=self.fg_color)

        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()

        # Create main frame with scrollbar
        self.main_frame = ttk.Frame(self.window, style='Dark.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add scrollbar and canvas
        self.canvas = tk.Canvas(
            self.main_frame, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style='Dark.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack scrollbar components
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Add mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Button frame at the top
        self.button_frame = ttk.Frame(
            self.scrollable_frame, style='Dark.TFrame')
        self.button_frame.pack(fill=tk.X, pady=(0, 10))

        # Add buttons using themed buttons
        self._create_button("Add Section", self.add_section).pack(
            side=tk.LEFT, padx=5)
        self._create_button("Save Changes", self.save_changes).pack(
            side=tk.LEFT, padx=5)
        self._create_button("Cancel", self.window.destroy).pack(
            side=tk.LEFT, padx=5)

        # Section frames will be stored here
        self.section_frames: List[Dict] = []

        # Load initial data
        self.load_sections(sections_data)

    def _create_button(self, text: str, command) -> tk.Button:
        """Create a consistently styled button"""
        return tk.Button(
            self.button_frame,
            text=text,
            command=command,
            bg=self.button_bg,
            fg=self.fg_color,
            relief=tk.RAISED,
            borderwidth=1
        )

    def _create_entry(self, parent, textvariable) -> tk.Entry:
        """Create a consistently styled entry"""
        return tk.Entry(
            parent,
            textvariable=textvariable,
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color
        )

    def _create_label(self, parent, text) -> tk.Label:
        """Create a consistently styled label"""
        return tk.Label(
            parent,
            text=text,
            bg=self.bg_color,
            fg=self.fg_color
        )

    def _create_combobox(self, parent, textvariable, values) -> ttk.Combobox:
        """Create a consistently styled combobox"""
        combo = ttk.Combobox(
            parent,
            textvariable=textvariable,
            values=values,
            state="readonly",
            width=10
        )
        combo.configure(background=self.entry_bg, foreground=self.fg_color)
        return combo

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_sections(self, sections_data: List[Dict[str, Any]]) -> None:
        """Load sections data into the editor"""
        for frame in self.section_frames:
            frame['frame'].destroy()
        self.section_frames.clear()

        for section in sections_data:
            self.add_section(section)

    def add_section(self, section_data: Optional[Dict[str, Any]] = None) -> None:
        """Add a new section frame"""
        if section_data is None:
            section_data = {
                "group_control": 0,
                "label": "New Section",
                "scales": [("New Scale", 0)]
            }

        # Create frame for this section
        section_frame = ttk.Frame(self.scrollable_frame, style='Dark.TFrame')
        section_frame.pack(fill=tk.X, padx=5, pady=5)

        # Add border and padding
        section_border = ttk.Frame(section_frame, style='Dark.TFrame')
        section_border.pack(fill=tk.X, padx=1, pady=1)

        # Section header
        header_frame = ttk.Frame(section_border, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        # Label entry
        self._create_label(header_frame, "Section Label:").pack(
            side=tk.LEFT, padx=(0, 5))

        label_var = tk.StringVar(value=section_data["label"])
        self._create_entry(header_frame, label_var).pack(side=tk.LEFT, padx=5)

        # Buttons
        self._create_button("Delete Section",
                            lambda: self.delete_section(section_frame)).pack(side=tk.RIGHT, padx=5)
        self._create_button("Add Scale",
                            lambda f=section_border: self.add_scale(f)).pack(side=tk.RIGHT, padx=5)

        # Frame for scales
        scales_frame = ttk.Frame(section_border, style='Dark.TFrame')
        scales_frame.pack(fill=tk.X, padx=5, pady=5)

        # Add initial scales
        for scale_name, scale_value in section_data["scales"]:
            self.add_scale(scales_frame, scale_name, scale_value)

        # Store section data
        self.section_frames.append({
            'frame': section_frame,
            'label_var': label_var,
            'scales_frame': scales_frame
        })

    def add_scale(self, parent_frame, scale_name: str = "New Scale", scale_value: int = 0) -> None:
        """Add a new scale row to a section"""
        scale_frame = ttk.Frame(parent_frame, style='Dark.TFrame')
        scale_frame.pack(fill=tk.X, pady=2)

        # Scale name entry
        name_var = tk.StringVar(value=scale_name)
        self._create_entry(scale_frame, name_var).pack(side=tk.LEFT, padx=5)

        # Scale value dropdown
        value_var = tk.StringVar()
        combo = self._create_combobox(
            scale_frame,
            value_var,
            ["OFF", "NEUTRAL", "ON"]
        )
        combo.pack(side=tk.LEFT, padx=5)

        # Set initial value
        value_map = {-1: "OFF", 0: "NEUTRAL", 1: "ON"}
        combo.set(value_map.get(scale_value, "NEUTRAL"))

        # Delete button
        self._create_button("Delete",
                            lambda: scale_frame.destroy()).pack(side=tk.LEFT, padx=5)

    def delete_section(self, section_frame: tk.Frame) -> None:
        """Delete a section frame"""
        section_frame.destroy()
        self.section_frames = [
            s for s in self.section_frames if s['frame'] != section_frame]

    def get_current_data(self) -> List[Dict[str, Any]]:
        """Get the current sections data from the UI"""
        sections_data = []
        value_map = {"OFF": -1, "NEUTRAL": 0, "ON": 1}

        for section in self.section_frames:
            scales = []
            for scale_frame in section['scales_frame'].winfo_children():
                widgets = [w for w in scale_frame.winfo_children()
                           if isinstance(w, (tk.Entry, ttk.Combobox))]
                if len(widgets) >= 2:
                    name_entry, value_combo = widgets[:2]
                    text_value = value_combo.get()
                    int_value = value_map.get(text_value, 0)
                    scales.append((name_entry.get(), int_value))

            sections_data.append({
                "group_control": 0,
                "label": section['label_var'].get(),
                "scales": scales
            })

        return sections_data

    def save_changes(self) -> None:
        """Save the current state and close the window"""
        try:
            new_data = self.get_current_data()
            self.save_callback(new_data)
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")
