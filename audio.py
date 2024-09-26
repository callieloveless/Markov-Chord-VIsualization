import pygame
import threading
from mingus.core import chords, notes
import re
import soundfile as sf
import numpy as np
import os

SHARP_TO_FLAT = {
    'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb', 'B#': 'C',
    'Db': 'Db', 'Eb': 'Eb', 'Gb': 'Gb', 'Ab': 'Ab', 'Bb': 'Bb', 'C': 'C',

    'C##': 'D', 'D##': 'E', 'F##': 'G', 'G##': 'A', 'A##': 'B', 'B##': 'C',
    'Dbb': 'C', 'Ebb': 'D', 'Fbb': 'E', 'Gbb': 'F', 'Abb': 'G', 'Bbb': 'A'
}

def convert_sharps_to_flats(note):
    """Convert a note with sharps or flats to its enharmonic flat equivalent, preserving the octave."""
    match = re.match(r'([A-G][#]{1,2}|[A-G][b]{1,2})(\d+)', note)
    if match:
        base_note = match.group(1)
        octave = match.group(2)
        # Convert the base note from sharp to flat if necessary
        flat_note = SHARP_TO_FLAT.get(base_note, base_note)
        return f"{flat_note}{octave}"
    return note

def get_note_to_file_mapping():
    return lambda note_name: f"{note_name}.mp3"

def append_octave_to_notes(chord_list, octave):
    new_list = []
    new_list.append(str(chord_list[0]) + str(octave))
    for i in range(1, len(chord_list)):
        if notes.note_to_int(chord_list[i-1]) > notes.note_to_int(chord_list[i]):
            octave += 1
        new_list.append(str(chord_list[i]) + str(octave))
    return new_list

def overlay_chords(chord_list, chord_name):
    note_to_file = get_note_to_file_mapping()
    overlay_data = None
    samplerate = None

    for note in chord_list:
        note_name = convert_sharps_to_flats(note)
        mp3_file_path = f"piano-mp3/{note_to_file(note_name)}"

        try:
            data, sr = sf.read(mp3_file_path)
            if overlay_data is None:
                overlay_data = data
                samplerate = sr
            else:
                # Ensure both audio files have the same sample rate
                if sr != samplerate:
                    raise ValueError("Sample rates do not match!")

                # Pad the shorter audio if needed
                min_length = min(len(overlay_data), len(data))
                
                # Sum the audio data
                overlay_data = overlay_data[:min_length] + data[:min_length]

        except Exception as e:
            print(f"Error loading {mp3_file_path}: {e}")

    if overlay_data is not None:
        # Normalize the output data to prevent distortion
        overlay_data = overlay_data / np.max(np.abs(overlay_data))  # Normalize to [-1, 1]

        # Save the overlay audio to a new file named after the chord
        output_file = f"{chord_name}.mp3"
        sf.write(output_file, overlay_data, samplerate)
        print(f"Overlay saved as {output_file}")

def play_chord(chord_symbol):
    chord_list = chords.from_shorthand(chord_symbol)
    new_list = append_octave_to_notes(chord_list, 4)  # Assuming octave 4 for this example
    overlay_chords(new_list, chord_symbol)  # Pass the chord symbol as the filename

if __name__ == '__main__':
    play_chord("D/G")
