# Mount & Blade Music Manager

Mount and Blade was an interesting feudal combat simulator with incredible modding capabilities. You also could add your favourite musics to any of the games (modules) using the Mount and Blade engine. The situations when you want to listen the music was also tunable. So you could have different musics for fighting on then field and other ones for sieges, also other for visiting towns, etc.

## Features

The program currently able to do the following:
* It parses the module's `music.txt` and reads the music folder.
* The two are compared and multiple ways are offered to correct errors (browsing an existing copy of a missing file or removing it's entry from the txt).
* New tracks can be added and their context (main menu, battle etc.) can be set.
* Tracks can be removed. They are excluded form the config only so no physical deletion occurs.
* User interface is English and Hungarian.
* UI strings and music types are stored in XML so UI can be easily translated and further mods can be easily added and maintained. (Feel free to create pull request to add updates.)

## Requirements

Requires Python 3 with tkinter installed (not excluded during installation). No additional packages are required besides the core python.

Clone the repo (or download it as a zip and extract) and you are ready to launch it.

## How to use

Run it from it's folder with

```python mbmmui.pyw```

command or double click on `mbmmui.pyw` file in a file manager.

If python's home folder is not included in the PATH variable, you need to run it with full path of python binary (for example `c:/python30/python.exe mbmmui.pyw` in case of a default installation of the earliest python 3 under Windows).

Don't expect some flashy UI, it is only TkInter. No eye candies.

### Module menu

In the `Module` menu you can select a mod folder to load a mod.

You can commit the changes made on the `music.txt` in the `Module` menu too.

### Application menu

In the `Application` menu you can change the UI language.

### Track list

If you have loaded a mod, you got little skull and crossbones button on the the top left corner. You can invert the exclusion checkboxes by clicking it. Exclusion is explained later.

By clicking the `Filename` or the `Category` button you can reorder the track list.

New records can be added by clicking on the `+` button on the middle.

In each row four things can be found:
* A checkbox for marking the row to be excluded when you save. You can remove a track by marking it for exclusion before you commit your changes.
* The filename.
* A button labeled `...` for browsing a new file. If you pick a new file from outside the mod's and the game's music directory, the file will be copied into one of them instantly.
* A drop down list for setting the context (ie. battle) when the track should be played.

![Screenshot](/.img/mbmm.png?raw=true)

## How to expand

Currently only _Warband_ and _Caribbean!_ can be managed by MBMM but you can easily add the missing games or your favorite mods, by adding them to `types-??.xml` where ?? stands for the ISO 639-1 code of language you use.

Additional <types> tags can be added for each mod. For the Mount and Blade vanilla it should be

```<types game="Mount and Blade"></types>```

Always try to find some unique string for the game attribute because if the value are found in the path of the module then it is identified automatically. If it is not found in the path then the program checks the selected mod's music.txt against all the different mods stored in the XML and finds the best fit.

![Types example](/.img/types.PNG?raw=true)

## Disclaimer

I uploaded it github as nostalgia. Back then when I wrote it, I did not care about PEP8, flake8 checks, unit testing or clean code. I would write it by following the standards and using TTD, if I would start the development now. Anyway it does the job. Have fun with it. :)
