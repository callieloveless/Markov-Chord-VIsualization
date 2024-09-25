import pygame
import threading
from mingus.core import chords, notes
import re

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

def play_chord(chord_symbol):
    chord_list = chords.from_shorthand(chord_symbol)
    new_list = append_octave_to_notes(chord_list, 4)  # Assuming octave 4 for this example

    pygame.mixer.init()
    note_to_file = get_note_to_file_mapping()

    channels = [pygame.mixer.Channel(i) for i in range(8)]  # Create 8 channels

    def play_note_mp3(note_name, channel):
        note_name = convert_sharps_to_flats(note_name)
        print(note_name)
        mp3_file_path = f"piano-mp3\\{note_to_file(note_name)}"

        try:
            sound = pygame.mixer.Sound(mp3_file_path)
            channel.play(sound)
        except pygame.error as e:
            print(f"Error loading {mp3_file_path}: {e}")

    for i, note in enumerate(new_list):
        if i < len(channels):
            play_note_mp3(note, channels[i])
        else:
            print("Not enough channels to play all notes.")

    while any(channel.get_busy() for channel in channels):
        pygame.time.wait(100)

    pygame.quit()

if __name__ == '__main__':
    play_chord("Dsus4b9/G")
