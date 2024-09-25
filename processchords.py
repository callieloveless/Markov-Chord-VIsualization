from mingus.core import chords, notes
from music21 import * 

# this class will be used when web scraping chord progressions

def convert_chord_to_roman_numeral(chord_list):
    roman_numerals = []
    for c in chord_list:
        notes_in_chord = chords.from_shorthand(c)
        new_chord =  chord.Chord(notes_in_chord)
        rf = roman.romanNumeralFromChord(new_chord, kb)
        roman_alone = rf.romanNumeralAlone
        roman_numerals.append(roman_alone)
    return roman_numerals

def convert_roman_numeral_to_chord(roman_numeral):
    rn = roman.RomanNumeral(roman_numeral)
    c = rn.pitches
    c = [str(n) for n in c]
    return c