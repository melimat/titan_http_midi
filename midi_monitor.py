import mido

with mido.open_input("nanoKONTROL2 1 SLIDER/KNOB 0") as inport:
    for msg in inport:
        print(msg)