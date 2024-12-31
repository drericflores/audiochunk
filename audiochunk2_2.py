# Audio Tool 
# Takes audio files and create 10 second chunks.
# Programmed by Dr. Eric O. FLores
# Version 2.2_GAIS
#
import librosa
import librosa.display
import soundfile as sf
import os
from tkinter import Tk, filedialog, messagebox, ttk, StringVar, Menu
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def split_audio_into_chunks(audio_data, sample_rate, chunk_duration_seconds, output_dir, base_name, output_format, mono=True, original_file_name=None):
    """Splits audio data into chunks and saves them as separate files."""
    duration = librosa.get_duration(y=audio_data, sr=sample_rate)
    total_chunks = int(duration // chunk_duration_seconds) + (1 if duration % chunk_duration_seconds != 0 else 0)

    print(f"Generating {total_chunks} chunks...")

    for i in range(total_chunks):
        start_sample = i * chunk_duration_seconds * sample_rate
        end_sample = min((i + 1) * chunk_duration_seconds * sample_rate, len(audio_data))
        chunk = audio_data[int(start_sample):int(end_sample)]
        if mono:
            chunk = chunk.astype(np.float32)
        else:
            chunk = chunk.astype(np.float32)

        # Create custom filename
        file_prefix = original_file_name if original_file_name else base_name
        output_file_path = os.path.join(output_dir, f"{file_prefix}_{str(i + 1).zfill(3)}.{output_format}")

        try:
            sf.write(output_file_path, chunk, sample_rate, format=output_format)
            print(f"Saved: {output_file_path}")
        except sf.SoundFileError as e:
            logging.error(f"Error writing to {output_file_path}: {e}")
            print(f"Error writing to {output_file_path}: {e}")

    return total_chunks


def analyze_audio_and_split():
    root = Tk()
    root.title("Audio Chunk Tool for AI Voice Cloning")
    root.geometry("600x400")  # Adjust window size

    # --- Style ---
    style = ttk.Style(root)
    style.theme_use('clam')  # or 'alt', 'default', 'classic'

    # --- Menu ---
    menu_bar = Menu(root)
    root.config(menu=menu_bar)

    # File Menu
    file_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    def load_file_menu():
        select_file()
    file_menu.add_command(label="Load a file", command=load_file_menu)
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=root.quit)

    #Settings Menu
    settings_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Settings", menu=settings_menu)

    def set_output_dir_menu():
        select_output_dir()
    settings_menu.add_command(label="Set Output Directory", command=set_output_dir_menu)


    def set_chunk_duration_menu():
         duration_spinbox.focus_set()
    settings_menu.add_command(label="Set Chunk Duration", command=set_chunk_duration_menu)

    def set_output_format_menu():
         format_combobox.focus_set()
    settings_menu.add_command(label="Set Output Format", command = set_output_format_menu)
    settings_menu.add_separator()
    def start_split_menu():
         start_splitting()
    settings_menu.add_command(label="Start Split", command = start_split_menu)

    # Help Menu
    help_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Help", menu=help_menu)

    def about_menu():
         messagebox.showinfo("About", "Audio Chunk\nBy Dr. Eric O. Flores\nVersion 2.2\nPython 3 / tkinter\nCopyrights (2024), Public domain under CC0: No rights reserved. ")
    help_menu.add_command(label="About", command=about_menu)

    # --- File Selection ---
    file_label = ttk.Label(root, text="Select Audio File:")
    file_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    file_path_var = StringVar()
    file_entry = ttk.Entry(root, textvariable=file_path_var, width=50)
    file_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    def select_file():
        file_path = filedialog.askopenfilename(
            title="Select an Audio File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a")]
        )
        file_path_var.set(file_path)

    file_button = ttk.Button(root, text="Browse", command=select_file)
    file_button.grid(row=0, column=2, padx=10, pady=10, sticky="w")

    # --- Output Directory Selection ---
    output_dir_label = ttk.Label(root, text="Select Output Directory:")
    output_dir_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    output_dir_var = StringVar()
    output_dir_entry = ttk.Entry(root, textvariable=output_dir_var, width=50)
    output_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    def select_output_dir():
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        output_dir_var.set(output_dir)

    output_dir_button = ttk.Button(root, text="Browse", command=select_output_dir)
    output_dir_button.grid(row=1, column=2, padx=10, pady=10, sticky="w")

    # --- Chunk Duration ---
    duration_label = ttk.Label(root, text="Chunk Duration (seconds):")
    duration_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    chunk_duration_var = StringVar(value="10")  # Default
    duration_spinbox = ttk.Spinbox(root, from_=1, to=60, textvariable=chunk_duration_var, width=5)
    duration_spinbox.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    # --- Output Format ---
    format_label = ttk.Label(root, text="Output Format:")
    format_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    output_format_var = StringVar(value="wav")  # Default
    format_combobox = ttk.Combobox(root, textvariable=output_format_var, values=["wav", "flac", "ogg", "aiff"], width=5)
    format_combobox.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    # --- Base Name ---
    base_name_label = ttk.Label(root, text="Base File Name:")
    base_name_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

    base_name_var = StringVar(value="chunk")  # Default
    base_name_entry = ttk.Entry(root, textvariable=base_name_var, width=20)
    base_name_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    def start_splitting():
        file_path = file_path_var.get()
        output_dir = output_dir_var.get()
        chunk_duration_seconds = int(chunk_duration_var.get())
        output_format = output_format_var.get()
        base_name = base_name_var.get()
        if not all([file_path, output_dir, chunk_duration_seconds, output_format, base_name]):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            # Load the audio file, letting librosa determine the sample rate
            y, sr = librosa.load(file_path, sr=None, mono=True)  # Loads in mono and allows librosa to determine sample rate.

            # Analyze the audio
            duration = librosa.get_duration(y=y, sr=sr)
            print(f"Loaded file: {file_path}")
            print(f"Sample Rate: {sr}")
            print(f"Duration: {duration:.2f} seconds")
            # Generate output directory if needed
            output_dir = os.path.join(output_dir, "audio_chunks")
            os.makedirs(output_dir, exist_ok=True)
            # Confirm before proceeding
            total_chunks = int(duration // chunk_duration_seconds) + (1 if duration % chunk_duration_seconds != 0 else 0)
            if messagebox.askyesno("Confirmation", f"Audio will be split into approximately {total_chunks} chunks. Proceed?"):

                original_file_name = os.path.splitext(os.path.basename(file_path))[0]
                total_chunks = split_audio_into_chunks(y, sr, chunk_duration_seconds, output_dir, base_name,
                                                      output_format, mono=True, original_file_name=original_file_name)
                messagebox.showinfo("Success", f"Audio split into {total_chunks} chunks in {output_dir}")
            else:
                messagebox.showinfo("Info", "Operation Cancelled.")
                return
        except librosa.LibrosaError as e:
            messagebox.showerror("Error", f"Error loading audio file: {e}")
            logging.error(f"Error loading audio file: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            logging.error(f"An unexpected error occurred: {e}")

    # --- Start Button ---
    start_button = ttk.Button(root, text="Start Splitting", command=start_splitting)
    start_button.grid(row=5, column=0, columnspan=3, pady=20)

    root.grid_columnconfigure(1, weight=1)  # Makes Entry field expand
    root.mainloop()


if __name__ == "__main__":
    analyze_audio_and_split()
