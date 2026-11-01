# UniNav — Campus Navigation
About the App: UniNav is a campus navigation application built around locations at Habib University. Users can select their current location and a destination to view coordinate-based directions on an interactive campus map.

The project combines Python programming, a KD-tree data structure, and graphical interface design.

GUI Screenshot
<img width="1638" height="1416" alt="image" src="https://github.com/user-attachments/assets/de1d7198-34c7-4982-8686-1a705e1edc18" />


Features

- Interactive campus map with labelled, colour-coded locations.
- Search suggestions while typing building names.
- Clickable map locations to fill the destination and starting point.
- A highlighted route between the selected locations.
- Horizontal and vertical directions with an estimated straight-line distance in coordinate units.
- Hover tooltips showing building names and categories.
- Input validation for missing or unrecognised locations.

The map uses illustrative coordinates. Routes are drawn horizontally and then vertically; they do not account for actual campus paths, obstacles, or accessibility.

Technologies

- **Python:** Application logic.
- **Tkinter:** Graphical interface and interactive map.
- **KD-tree:** Storage of two-dimensional building coordinates.
- **Math module:** Distance calculations.

The KD-tree implementation also includes nearest-neighbour search. The current GUI selects buildings through name matching and map clicks.


1. Install Python 3 with Tkinter support.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Run:

```bash
python3 uninav_gui.py
```

Once the window opens, enter a destination and your current location, then click **Get Directions**. You can also select locations by clicking their dots on the map.

No additional third-party Python packages are required.
