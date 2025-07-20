import librosa
import soundfile as sf
import os
import sys
from tkinter import Tk, filedialog, messagebox, ttk, StringVar, Menu
import logging
import numpy as np
import json # For saving/loading settings

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class AudioChunkerApp:
    def __init__(self, master):
        self.master = master
        master.title("Audio Chunk Tool for AI Voice Cloning (Enhanced)")
        master.geometry("650x500") # Slightly larger window
        master.resizable(False, False) # Prevent resizing

        # --- Style ---
        style = ttk.Style(master)
        style.theme_use('clam') # or 'alt', 'default', 'classic'

        # --- Variables ---
        self.file_path_var = StringVar()
        self.output_dir_var = StringVar()
        self.chunk_duration_var = StringVar(value="10")
        self.output_format_var = StringVar(value="wav")
        self.base_name_var = StringVar(value="chunk")
        self.status_var = StringVar(value="Ready")

        self.config_file = "audio_chunker_config.json"
        self._load_config() # Load saved settings

        self._create_widgets()
        self._create_menu()

    def _load_config(self):
        """Loads configuration from a JSON file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.file_path_var.set(config.get('last_input_file', ''))
                    self.output_dir_var.set(config.get('last_output_dir', ''))
                    self.chunk_duration_var.set(config.get('chunk_duration', '10'))
                    self.output_format_var.set(config.get('output_format', 'wav'))
                    self.base_name_var.set(config.get('base_name', 'chunk'))
            except Exception as e:
                logging.error(f"Error loading configuration: {e}")
                messagebox.showerror("Config Error", f"Could not load settings: {e}")

    def _save_config(self):
        """Saves current settings to a JSON file."""
        config = {
            'last_input_file': self.file_path_var.get(),
            'last_output_dir': self.output_dir_var.get(),
            'chunk_duration': self.chunk_duration_var.get(),
            'output_format': self.output_format_var.get(),
            'base_name': self.base_name_var.get()
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")

    def _create_menu(self):
        """Creates the application menu bar."""
        menu_bar = Menu(self.master)
        self.master.config(menu=menu_bar)

        # File Menu
        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Audio File...", command=self.select_file)
        file_menu.add_command(label="Set Output Directory...", command=self.select_output_dir)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

        # Actions Menu
        actions_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Actions", menu=actions_menu)
        actions_menu.add_command(label="Start Splitting", command=self.start_splitting)
        actions_menu.add_command(label="Open Output Folder", command=self.open_output_directory)

        # Help Menu
        help_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about_info)

    def _create_widgets(self):
        """Creates and places all GUI widgets."""
        # --- Input File Frame ---
        input_frame = ttk.LabelFrame(self.master, text="Input Audio File")
        input_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="File Path:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.file_entry = ttk.Entry(input_frame, textvariable=self.file_path_var, width=60, state='readonly')
        self.file_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_file_button = ttk.Button(input_frame, text="Browse", command=self.select_file)
        self.browse_file_button.grid(row=0, column=2, padx=5, pady=5)

        # --- Output Directory Frame ---
        output_frame = ttk.LabelFrame(self.master, text="Output Settings")
        output_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        output_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.output_dir_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=60, state='readonly')
        self.output_dir_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_output_button = ttk.Button(output_frame, text="Browse", command=self.select_output_dir)
        self.browse_output_button.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(output_frame, text="Chunk Duration (seconds):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.duration_spinbox = ttk.Spinbox(output_frame, from_=1, to=120, textvariable=self.chunk_duration_var, width=5)
        self.duration_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(output_frame, text="Output Format:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.format_combobox = ttk.Combobox(output_frame, textvariable=self.output_format_var,
                                            values=["wav", "flac", "ogg", "aiff"], width=7, state='readonly')
        self.format_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.format_combobox.set("wav") # Ensure default is set for display

        ttk.Label(output_frame, text="Base File Name:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.base_name_entry = ttk.Entry(output_frame, textvariable=self.base_name_var, width=20)
        self.base_name_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # --- Action Buttons ---
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Splitting", command=self.start_splitting)
        self.start_button.pack(side="left", padx=10)

        self.open_output_button = ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_directory)
        self.open_output_button.pack(side="left", padx=10)
        self.open_output_button.config(state='disabled') # Disable until splitting is done

        # --- Status Bar ---
        self.status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=ttk.SUNKEN, anchor="w")
        self.status_bar.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        # Configure column to expand
        self.master.grid_columnconfigure(0, weight=1)

    def _update_status(self, message):
        """Updates the status bar message."""
        self.status_var.set(message)
        self.master.update_idletasks() # Ensure GUI updates immediately

    def _set_controls_state(self, state):
        """Sets the state of interactive controls (normal/disabled)."""
        self.browse_file_button.config(state=state)
        self.browse_output_button.config(state=state)
        self.duration_spinbox.config(state=state)
        self.format_combobox.config(state=state)
        self.base_name_entry.config(state=state)
        self.start_button.config(state=state)
        # open_output_button's state is handled separately after successful split

    def select_file(self):
        """Opens a dialog to select an audio file."""
        initial_dir = os.path.dirname(self.file_path_var.get()) if self.file_path_var.get() else os.path.expanduser("~")
        file_path = filedialog.askopenfilename(
            title="Select an Audio File",
            initialdir=initial_dir,
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            # Suggest output directory if none is set, using input file's directory
            if not self.output_dir_var.get():
                self.output_dir_var.set(os.path.dirname(file_path))

    def select_output_dir(self):
        """Opens a dialog to select the output directory."""
        initial_dir = self.output_dir_var.get() if self.output_dir_var.get() else os.path.expanduser("~")
        output_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=initial_dir
        )
        if output_dir:
            self.output_dir_var.set(output_dir)

    def open_output_directory(self):
        """Opens the output directory in the file explorer."""
        output_path = os.path.join(self.output_dir_var.get(), "audio_chunks")
        if not os.path.isdir(output_path):
            messagebox.showinfo("Info", "Output directory not yet created or found.")
            return

        if sys.platform == "win32":
            os.startfile(output_path)
        elif sys.platform == "darwin": # macOS
            os.system(f"open \"{output_path}\"")
        else: # Linux and other POSIX systems
            os.system(f"xdg-open \"{output_path}\"")

    def show_about_info(self):
        """Displays application information."""
        messagebox.showinfo(
            "About",
            "Audio Chunk Tool\nBy Dr. Eric O. Flores\nVersion 2.2_GAIS (Enhanced)\nPython 3 / Tkinter\n"
            "Copyrights (2024), Public domain under CC0: No rights reserved."
        )

    def start_splitting(self):
        """Initiates the audio splitting process."""
        file_path = self.file_path_var.get()
        output_dir = self.output_dir_var.get()
        try:
            chunk_duration_seconds = int(self.chunk_duration_var.get())
            if chunk_duration_seconds <= 0:
                messagebox.showerror("Invalid Input", "Chunk duration must be a positive integer.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Chunk duration must be a number.")
            return

        output_format = self.output_format_var.get()
        base_name = self.base_name_var.get()

        if not all([file_path, output_dir, chunk_duration_seconds, output_format, base_name]):
            messagebox.showerror("Error", "Please ensure an audio file, output directory, and all settings are provided.")
            return
        if not os.path.exists(file_path):
            messagebox.showerror("File Error", "The selected audio file does not exist.")
            return
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                messagebox.showinfo("Directory Created", f"Output directory '{output_dir}' was created.")
            except Exception as e:
                messagebox.showerror("Directory Error", f"Could not create output directory: {e}")
                logging.error(f"Error creating output directory '{output_dir}': {e}")
                return

        self._set_controls_state('disabled')
        self.open_output_button.config(state='disabled') # Disable this until success
        self._update_status("Loading audio file...")

        try:
            # Load the audio file, letting librosa determine the sample rate and force mono
            y, sr = librosa.load(file_path, sr=None, mono=True)

            duration = librosa.get_duration(y=y, sr=sr)
            self._update_status(f"File loaded: {os.path.basename(file_path)} (SR: {sr}, Duration: {duration:.2f}s)")
            print(f"Loaded file: {file_path}")
            print(f"Sample Rate: {sr}")
            print(f"Duration: {duration:.2f} seconds")

            # Create specific output subdirectory for chunks
            final_output_dir = os.path.join(output_dir, "audio_chunks")
            os.makedirs(final_output_dir, exist_ok=True)

            total_chunks = int(duration // chunk_duration_seconds) + (1 if duration % chunk_duration_seconds != 0 else 0)

            confirm_msg = (f"Audio will be split into approximately {total_chunks} chunks of {chunk_duration_seconds} seconds.\n"
                           f"Output will be saved in: {final_output_dir}\n"
                           f"Proceed?")
            if not messagebox.askyesno("Confirmation", confirm_msg):
                self._update_status("Operation Cancelled.")
                messagebox.showinfo("Info", "Operation Cancelled.")
                self._set_controls_state('normal')
                return

            original_file_name = os.path.splitext(os.path.basename(file_path))[0]
            self._update_status("Splitting audio...")

            chunks_saved = self._split_audio_into_chunks(y, sr, chunk_duration_seconds, final_output_dir,
                                                        base_name, output_format, original_file_name=original_file_name)

            self._update_status(f"Successfully split into {chunks_saved} chunks!")
            messagebox.showinfo("Success", f"Audio split into {chunks_saved} chunks in:\n{final_output_dir}")
            self.open_output_button.config(state='normal') # Enable after success
            self._save_config() # Save current settings
        except librosa.LibrosaError as e:
            error_msg = f"Error loading audio file: {e}"
            messagebox.showerror("Audio Load Error", error_msg)
            logging.error(error_msg)
            self._update_status("Error loading audio file.")
        except sf.SoundFileError as e:
            error_msg = f"Error writing audio chunk: {e}"
            messagebox.showerror("File Write Error", error_msg)
            logging.error(error_msg)
            self._update_status("Error writing audio chunks.")
        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}"
            messagebox.showerror("General Error", error_msg)
            logging.error(error_msg, exc_info=True) # Log full traceback
            self._update_status("An unexpected error occurred.")
        finally:
            self._set_controls_state('normal')
            # If start button was already enabled, ensure it remains so.
            # If it was disabled due to an error, it should now be re-enabled.


    def _split_audio_into_chunks(self, audio_data, sample_rate, chunk_duration_seconds, output_dir, base_name, output_format, mono=True, original_file_name=None):
        """Splits audio data into chunks and saves them as separate files."""
        duration = librosa.get_duration(y=audio_data, sr=sample_rate)
        total_chunks = int(duration // chunk_duration_seconds) + (1 if duration % chunk_duration_seconds != 0 else 0)

        print(f"Generating {total_chunks} chunks...")
        self._update_status(f"Processing 0/{total_chunks} chunks...")

        chunks_saved_count = 0
        for i in range(total_chunks):
            start_sample = i * chunk_duration_seconds * sample_rate
            end_sample = min((i + 1) * chunk_duration_seconds * sample_rate, len(audio_data))
            chunk = audio_data[int(start_sample):int(end_sample)]

            # Ensure chunk is float32 for soundfile compatibility
            chunk = chunk.astype(np.float32)

            # Create custom filename
            file_prefix = original_file_name if original_file_name else base_name
            # Sanitize file_prefix to remove invalid characters
            file_prefix = "".join(c for c in file_prefix if c.isalnum() or c in (' ', '_', '-')).strip()
            if not file_prefix: # Fallback if sanitized name is empty
                file_prefix = "chunk"

            output_file_path = os.path.join(output_dir, f"{file_prefix}_{str(i + 1).zfill(len(str(total_chunks)))}.{output_format}")

            try:
                sf.write(output_file_path, chunk, sample_rate, format=output_format)
                print(f"Saved: {output_file_path}")
                chunks_saved_count += 1
                self._update_status(f"Processing {i+1}/{total_chunks} chunks...")
            except sf.SoundFileError as e:
                logging.error(f"Error writing to {output_file_path}: {e}")
                print(f"Error writing to {output_file_path}: {e}")
                self._update_status(f"Error saving chunk {i+1}. See logs.")
            except Exception as e:
                logging.error(f"An unexpected error occurred while writing {output_file_path}: {e}")
                print(f"An unexpected error occurred while writing {output_file_path}: {e}")
                self._update_status(f"Error saving chunk {i+1}. See logs.")

        return chunks_saved_count

if __name__ == "__main__":
    root = Tk()
    app = AudioChunkerApp(root)
    root.mainloop()
