from mp3tagger.data.constants import AUTO_LOAD_LAST_VIEW, NEUTRAL, bg_color, fg_color, filter_font
from mp3tagger.data.sections import NEUTRAL, bg_color, fg_color, filter_font, sections_data
from mp3tagger.scripts.automate import automate, os
from mp3tagger.scripts.bpm import get_bpm_filter
from mp3tagger.scripts.builders import NEUTRAL, Any, Dict, IntVar, bg_color, build_section, clean_filter, fg_color, filter_font, get_filter_from_section, logger, sections_data, tk
from mp3tagger.classes.slider import END, WORD, Canvas, IntVar, List, Scrollbar, Slider, Text, logger


import json
import os
import subprocess
import threading
import tkinter as tk
from datetime import datetime
from tkinter import END, WORD, Canvas, IntVar, Label, Scrollbar, Text, filedialog, messagebox, simpledialog
from typing import Any, Dict, List, Optional


class MP3TaggerApp:
    def __init__(self, root: tk.Tk) -> None:
        """
        Initializes the MP3TaggerApp with the main Tkinter root window.
        """
        self.root: tk.Tk = root
        self.root.title("MP3 Tagger")
        self.root.configure(bg=bg_color, highlightcolor=fg_color)
        self.root.state('zoomed')
        self.views_dir: str = os.path.join(os.path.dirname(__file__), "data\\views")

        # Add current_view_name attribute
        self.current_view_name: str = "No view loaded"
        
        self.sections: List[Dict[str, Any]] = []
        self.textbox: Text
        self.slider: Slider
        self.IncludeBpm: IntVar
        self.HoldAbsent: IntVar
        self.DeselectAbsent: IntVar
        self.current_view_label: Optional[Label] = None

        logger.debug("Initializing MP3TaggerApp.")
        self.setup_gui()
        self.setup_view_label()
        
        # Try to load the most recent view
        self.load_most_recent_view()
        
        # If no view was loaded, set default filter string
        if not self.textbox.get("1.0", END).strip():
            self.set_filter_string()

        self.mp3tag_path: Optional[str] = os.environ.get("MP3TAG_PATH")
        logger.debug(f"MP3TAG_PATH retrieved: {self.mp3tag_path}")
        self.launch_mp3tag()


    def setup_view_label(self) -> None:
        """
        Sets up the label that displays the current view name.
        """
        # Create a frame for the view label with padding
        view_frame = tk.Frame(
            self.frame,
            bg=bg_color,
            padx=5,
            pady=5
        )
        view_frame.grid(
            row=0,  # At the top
            column=len(self.sections) + 1,  # Next to the controls
            sticky="ne",
            padx=10,
            pady=5
        )

        # Create the label with the current view name
        self.current_view_label = tk.Label(
            view_frame,
            text=f"Current View: {self.current_view_name}",
            bg=bg_color,
            fg=fg_color,
            font=("Courier", 10),
            justify=tk.LEFT,
            anchor="w"
        )
        self.current_view_label.pack(expand=True, fill=tk.X)

    def update_view_label(self, view_name: str) -> None:
        """
        Updates the current view label with a new view name.
        
        Args:
            view_name (str): Name of the current view
        """
        self.current_view_name = view_name
        if self.current_view_label:
            self.current_view_label.config(
                text=f"Current View: {self.current_view_name}"
            )


    def load_most_recent_view(self) -> None:
        """
        Attempts to load the most recently saved view from the views directory.
        """
        try:
            if not os.path.exists(self.views_dir):
                logger.info("No views directory found.")
                return

            # Get list of all view files
            view_files = [f for f in os.listdir(self.views_dir) if f.endswith('.json')]
            
            if not view_files:
                logger.info("No saved views found.")
                return

            # Sort files by modification time (most recent first)
            most_recent = max(
                view_files,
                key=lambda f: os.path.getmtime(os.path.join(self.views_dir, f))
            )
            
            # Get view name without timestamp
            view_name = os.path.splitext(most_recent)[0]
            view_name = view_name.rsplit('_', 2)[0]  # Remove timestamp
            
            filepath = os.path.join(self.views_dir, most_recent)
            logger.info(f"Loading most recent view: {view_name}")

            # Update the view name display
            self.update_view_label(view_name)

            # Load the view data
            with open(filepath, "r") as f:
                view_data = json.load(f)

            # Set BPM Slider
            bpm_values = view_data.get("BPMSlider", [80, 100])
            self.slider.setValues(bpm_values)
            logger.debug(f"BPM Slider set to: {bpm_values}")

            # Set Checkboxes
            self.IncludeBpm.set(view_data.get("IncludeBpm", NEUTRAL))
            self.HoldAbsent.set(view_data.get("HoldAbsent", NEUTRAL))
            self.DeselectAbsent.set(view_data.get("DeselectAbsent", NEUTRAL))
            logger.debug("Checkboxes set to loaded values.")

            # Update each section
            for loaded_section in view_data.get("sections", []):
                label_text = loaded_section.get("label")
                for section in self.sections:
                    current_label = section["label"].cget("text")
                    if current_label == label_text:
                        # Set no_blanks checkbox
                        section["no_blanks"].set(loaded_section.get("no_blanks", NEUTRAL))
                        logger.debug(f"'no_blanks' set for section '{label_text}'.")

                        # Set each scale
                        for scale_widget, (param, value) in zip(section["scales"], loaded_section.get("scales", [])):
                            scale_label = scale_widget.cget("label").strip()
                            if scale_label == param:
                                scale_widget.set(value)
                                logger.debug(f"Scale '{param}' set to {value} in section '{label_text}'.")
                        break

            # Update the filter string after loading the view
            self.set_filter_string()
            logger.info(f"Successfully loaded most recent view: {most_recent}")
            
            # Show a temporary message to user
            self.show_temporary_message(f"Loaded view: {most_recent}")
            
        except Exception as e:
            logger.error(f"Failed to load most recent view: {e}")
            messagebox.showerror("Load View", f"Failed to load most recent view.\nError: {e}")

    def show_temporary_message(self, message: str, duration: int = 3000) -> None:
        """
        Shows a temporary message at the bottom of the window.
        
        Args:
            message (str): Message to display
            duration (int): How long to show message in milliseconds
        """
        # Create a label for the message
        msg_label = Label(
            self.root,
            text=message,
            bg='#2d2d2d',
            fg='#8c8c8c',
            pady=10
        )
        msg_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Schedule the label to be destroyed
        self.root.after(duration, msg_label.destroy)
    def setup_gui(self) -> None:
        """
        Sets up the main GUI components, including the scrollable frame, sections, and controls.
        """
        logger.debug("Setting up GUI components.")
        # Create a scrollable frame
        canvas: Canvas = Canvas(self.root, bg=bg_color, highlightthickness=0)
        h_scrollbar: Scrollbar = Scrollbar(self.root, orient='horizontal', command=canvas.xview)
        canvas.configure(xscrollcommand=h_scrollbar.set)

        self.frame: tk.Frame = tk.Frame(canvas, bg=bg_color)
        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.create_window((0, 0), window=self.frame, anchor='nw')
        self.frame.bind("<Configure>", lambda event: self.on_frame_configure(canvas))

        self.build_sections()
        self.build_controls()

    def on_frame_configure(self, canvas: Canvas) -> None:
        """
        Updates the scroll region of the canvas whenever the frame is resized.

        Args:
            canvas (Canvas): The canvas containing the frame.
        """
        logger.debug("Configuring frame scroll region.")
        canvas.configure(scrollregion=canvas.bbox("all"))

    def build_sections(self) -> None:
        """
        Builds each section of the GUI based on the sections_data.
        """
        logger.debug("Building sections.")
        row: int = 0
        column: int = 0

        for section_data in sections_data:
            section_data["no_blanks"] = IntVar(name=f"NoBlanks{section_data['label']}")
            logger.debug(f"Adding no_blanks IntVar for section: {section_data['label']}")

            section: Dict[str, Any] = build_section(
                self.frame,
                section_data,
                row=row,
                column=column,
                toggle_command=self.set_filter_string_from_toggle,
                command=self.set_filter_string,
            )
            self.sections.append(section)
            logger.debug(f"Section '{section_data['label']}' added to GUI.")
            column += 1

    def build_controls(self) -> None:
        """
        Builds additional controls such as BPM slider, checkboxes, filter button, textbox,
        and the new Save/Load View buttons.
        """
        logger.debug("Building controls.")
        row: int = 0
        column: int = len(self.sections)  # Continue columns after sections

        # BPM Label
        bpm_label: tk.Label = tk.Label(self.frame, text="BPM Range", bg=bg_color, fg=fg_color)
        bpm_label.grid(row=row, column=column, padx=5, pady=5)
        logger.debug("BPM Label added.")

        # BPM Slider
        row += 1
        self.slider = Slider(
            self.frame,
            width=600,
            height=50,
            min_val=55,
            max_val=140,
            init_lis=[80, 100],
            show_value=True,
        )
        self.slider.grid(row=row, column=column, padx=5, pady=5)
        logger.debug("BPM Slider added.")

        # BPM Checkbox
        row += 1
        self.IncludeBpm = IntVar(value=NEUTRAL)
        bpm_checkbox: tk.Checkbutton = tk.Checkbutton(
            self.frame,
            text="Include BPM",
            variable=self.IncludeBpm,
            bg=bg_color,
            fg=fg_color,
            selectcolor="#333333",
            command=self.set_filter_string,
        )
        bpm_checkbox.grid(row=row, column=column, padx=5, pady=5)
        bpm_checkbox.select()
        logger.debug("Include BPM Checkbox added and selected.")

        # Hold Absent Checkbox
        row += 1
        self.HoldAbsent = IntVar(value=NEUTRAL)
        hold_checkbox: tk.Checkbutton = tk.Checkbutton(
            self.frame,
            text="Exclude files on hold",
            variable=self.HoldAbsent,
            bg=bg_color,
            fg=fg_color,
            selectcolor="#333333",
            command=self.set_filter_string,
        )
        hold_checkbox.grid(row=row, column=column, padx=5, pady=5)
        hold_checkbox.select()
        logger.debug("Hold Absent Checkbox added and selected.")

        # Deselect Absent Checkbox
        row += 1
        self.DeselectAbsent = IntVar(value=NEUTRAL)
        deselect_checkbox: tk.Checkbutton = tk.Checkbutton(
            self.frame,
            text="Exclude deselect",
            variable=self.DeselectAbsent,
            bg=bg_color,
            fg=fg_color,
            selectcolor="#333333",
            command=self.set_filter_string,
        )
        deselect_checkbox.grid(row=row, column=column, padx=5, pady=5)
        deselect_checkbox.select()
        logger.debug("Deselect Absent Checkbox added and selected.")

        # Filter Button
        row += 2
        filter_button: tk.Button = tk.Button(
            self.frame,
            text="FILTER",
            command=self.copy_to_mp3tag,
            bg=bg_color,
            fg=fg_color
        )
        filter_button.grid(row=row, column=column, padx=5, pady=5)
        logger.debug("Filter Button added.")

        # Filter Textbox
        self.textbox = tk.Text(
            self.frame,
            wrap=WORD,
            padx=10,
            bg=bg_color,
            fg=fg_color,
            font=filter_font
        )
        row += 1
        self.textbox.grid(
            row=row,
            column=column,
            rowspan=5,
            pady=17,
            padx=5,
            sticky="nsew",
        )
        self.textbox.delete("1.0", END)
        logger.debug("Filter Textbox added and cleared.")

        # ---- Buttons for Save and Load View ----
        # Save View Button
        row = 1  # Adjust row to place buttons below existing controls
        column += 1  # Adjust column to place buttons to the right of existing controls
        save_view_button: tk.Button = tk.Button(
            self.frame,
            text="Save View",
            command=self.save_view,
            bg=bg_color,
            fg=fg_color
        )
        save_view_button.grid(row=row, column=column, padx=5, pady=5)
        logger.debug("Save View Button added.")

        # Load View Button
        row += 1
        load_view_button: tk.Button = tk.Button(
            self.frame,
            text="Load View",
            command=self.load_view,
            bg=bg_color,
            fg=fg_color
        )
        load_view_button.grid(row=row, column=column, padx=5, pady=5)
        logger.debug("Load View Button added.")
        # ---------------------------------------------

    def save_view(self) -> None:
        """
        Saves the current view configuration to a JSON file.
        """
        logger.debug("Initiating Save View process.")

        # Prompt user for a view name, defaulting to current datetime
        default_name = datetime.now().strftime("%Y-%m-%d %H:%M")
        view_name = simpledialog.askstring("Save View", "Enter a name for the view:", initialvalue=default_name)
        
        if not view_name:
            logger.info("Save View cancelled by user.")
            return

        # Update the view name display
        self.update_view_label(view_name)

        if not view_name:
            logger.info("Save View cancelled by user.")
            return  # User cancelled the dialog

        # Sanitize view_name to create a valid filename
        safe_view_name = "".join([c if c.isalnum() or c in " _-" else "_" for c in view_name])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_view_name}_{timestamp}.json"


        os.makedirs(self.views_dir, exist_ok=True)
        filepath = os.path.join(self.views_dir, filename)

        # Gather current state
        view_data = {
            "sections": [],
            "IncludeBpm": self.IncludeBpm.get(),
            "HoldAbsent": self.HoldAbsent.get(),
            "DeselectAbsent": self.DeselectAbsent.get(),
            "BPMSlider": self.slider.getValues(),
        }

        for section in self.sections:
            section_data = {
                "label": section["label"].cget("text"),
                "no_blanks": section["no_blanks"].get(),
                "scales": []
            }
            for scale in section["scales"]:
                param = scale.cget("label").strip()
                value = scale.get()
                section_data["scales"].append((param, value))
            view_data["sections"].append(section_data)

        # Save to JSON
        try:
            with open(filepath, "w") as f:
                json.dump(view_data, f, indent=4)
            logger.info(f"View '{view_name}' saved successfully as '{filename}'.")
            messagebox.showinfo("Save View", f"View '{view_name}' saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save view '{view_name}': {e}")
            messagebox.showerror("Save View", f"Failed to save view '{view_name}'.\nError: {e}")

    def load_view(self) -> None:
        """
        Loads a saved view configuration from a JSON file.
        """
        logger.debug("Initiating Load View process.")

        if not os.path.exists(self.views_dir):
            logger.warning("No 'views' directory found.")
            messagebox.showwarning("Load View", "No saved views found.")
            return

        filepath = filedialog.askopenfilename(
            title="Select a View to Load",
            initialdir=self.views_dir,
            filetypes=[("JSON Files", "*.json")],
        )

        if not filepath:
            logger.info("Load View cancelled by user.")
            return

        try:
            # Get view name from filename
            view_name = os.path.splitext(os.path.basename(filepath))[0]
            # Remove timestamp from view name (assuming format "viewname_YYYYMMDD_HHMMSS")
            view_name = view_name.rsplit('_', 2)[0]
            
            # Rest of your existing load_view code...
            with open(filepath, "r") as f:
                view_data = json.load(f)
                
            # Update the view name display
            self.update_view_label(view_name)

            logger.info(f"View loaded from '{filepath}'.")
        except Exception as e:
            logger.error(f"Failed to load view from '{filepath}': {e}")
            messagebox.showerror("Load View", f"Failed to load view.\nError: {e}")
            return

        # Apply loaded data to the GUI
        try:
            # Set BPM Slider
            bpm_values = view_data.get("BPMSlider", [80, 100])
            self.slider.setValues(bpm_values)
            logger.debug(f"BPM Slider set to: {bpm_values}")

            # Set Checkboxes
            self.IncludeBpm.set(view_data.get("IncludeBpm", NEUTRAL))
            self.HoldAbsent.set(view_data.get("HoldAbsent", NEUTRAL))
            self.DeselectAbsent.set(view_data.get("DeselectAbsent", NEUTRAL))
            logger.debug("Checkboxes set to loaded values.")

            # Update each section
            for loaded_section in view_data.get("sections", []):
                label_text = loaded_section.get("label")
                for section in self.sections:
                    current_label = section["label"].cget("text")
                    if current_label == label_text:
                        # Set no_blanks checkbox
                        section["no_blanks"].set(loaded_section.get("no_blanks", NEUTRAL))
                        logger.debug(f"'no_blanks' set for section '{label_text}'.")

                        # Set each scale
                        for scale_widget, (param, value) in zip(section["scales"], loaded_section.get("scales", [])):
                            scale_label = scale_widget.cget("label").strip()
                            if scale_label == param:
                                scale_widget.set(value)
                                logger.debug(f"Scale '{param}' set to {value} in section '{label_text}'.")
                        break  # Move to the next loaded section

            # Update the filter string after loading the view
            self.set_filter_string()
            logger.info("GUI updated with loaded view.")
            messagebox.showinfo("Load View", "View loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to apply loaded view: {e}")
            messagebox.showerror("Load View", f"Failed to apply loaded view.\nError: {e}")

    def copy_to_mp3tag(self) -> None:
        """
        Copies the filter string to MP3Tag by invoking an external automation function.
        """
        logger.debug("Copying filter string to MP3Tag.")
        my_filter: str = self.textbox.get("1.0", "end-1c").replace("\n", " AND ")
        logger.debug(f"Original filter string from textbox: {my_filter}")

        if self.HoldAbsent.get() == NEUTRAL:
            my_filter += " AND HOLD ABSENT"
            logger.debug("Added 'HOLD ABSENT' to filter.")

        if self.DeselectAbsent.get() == NEUTRAL:
            my_filter += " AND DESELECT ABSENT"
            logger.debug("Added 'DESELECT ABSENT' to filter.")

        logger.info(f"Final filter string to automate: {my_filter}")
        threading.Thread(target=automate, args=(my_filter,), daemon=True).start()
        logger.debug("Automation thread started.")

    def set_filter_string(self, *args) -> None:
        """
        Updates the filter string based on user input and current section states.
        Now handles additional arguments passed by Tkinter callbacks.
        """
        logger.debug("Updating filter string.")
        filters = []

        if self.IncludeBpm.get() == NEUTRAL:
            bpm_values: List[int] = self.slider.getValues()
            bpm_filter = get_bpm_filter(bpm_values)
            if bpm_filter:
                filters.append(bpm_filter)
            logger.debug(f"Including BPM filter: {bpm_filter}")

        for section in self.sections:
            section_filter = get_filter_from_section("", section, control_toggle_pressed=False)
            if section_filter:
                filters.append(section_filter)
            logger.debug(f"Filter after section '{section['label'].cget('text')}': {section_filter}")

        # Combine all non-empty filters with AND
        my_filter = " AND ".join(filter for filter in filters if filter)
        my_filter = clean_filter(my_filter)

        logger.debug(f"Final filter string: {my_filter}")

        self.textbox.delete("1.0", "end-1c")
        self.textbox.insert(END, my_filter.replace(" AND ", "\n"))
        logger.info("Filter string updated and inserted into textbox.")

    def set_filter_string_from_toggle(self, value, toggled_section_name: Optional[str] = None) -> None:
        """
        Updates the filter string when a toggle is pressed, highlighting the toggled section.

        Args:
            value: The new value from the toggle (passed automatically by Tkinter)
            toggled_section_name (Optional[str]): The name of the toggled section.
        """
        logger.debug(f"Toggle pressed for section: {toggled_section_name} with value: {value}")

        my_filter: str = ""

        if self.IncludeBpm.get() == NEUTRAL:
            bpm_values: List[int] = self.slider.getValues()
            my_filter = get_bpm_filter(bpm_values)
            logger.debug(f"Including BPM filter: {my_filter}")

        for section in self.sections:
            is_toggled: bool = section["label"].cget("text") == toggled_section_name
            my_filter = get_filter_from_section(
                my_filter, section, control_toggle_pressed=is_toggled
            )
            logger.debug(f"Filter after toggling section '{section['label'].cget('text')}': {my_filter}")

        my_filter = clean_filter(my_filter).replace(" AND ", "\n")
        logger.debug(f"Final filter string after toggle: {my_filter}")

        self.textbox.delete("1.0", "end-1c")
        self.textbox.insert(END, my_filter)
        logger.info("Filter string updated from toggle and inserted into textbox.")

    def launch_mp3tag(self) -> None:
        """
        Launches the MP3Tag application using the provided path.
        """
        logger.debug("Launching MP3Tag application.")
        try:
            if not self.mp3tag_path:
                raise ValueError("MP3TAG_PATH environment variable is not set.")
            logger.debug(f"MP3TAG_PATH: {self.mp3tag_path}")

            subprocess.Popen([self.mp3tag_path])
            logger.info(f"MP3Tag launched from path: {self.mp3tag_path}")

            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error launching MP3Tag: {e}")
            print(f"Error: {e}")
            print("Please set the MP3TAG_PATH environment variable to the path of your mp3tag executable.")
            print("Example (Windows): set MP3TAG_PATH='C:\\Path\\To\\mp3tag.exe'")
            print(f"Currently, it is set to: {self.mp3tag_path}")