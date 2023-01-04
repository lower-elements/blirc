# Blirc - a Self-Voicing IRC Client

Blirc is a self-voicing IRC client, designed to be used by blind / visually impaired IRC users.

## Installation

If you'd like to run this from source (Currently the only way):

```shell
git clone https://github.com/lower-elements/blirc
cd blirc
pip install .
python -m blirc
```

At this time, no config initialisation has-been implemented yet. If you don't copy the configuration file to your user-directory, the app might respond with unexpected behaviour.

* On Windows, copy config.ini.example in to your standard App Data folder, E.G c:\users\Alice\app data\local\lower-elements\blirc
* On Mac OS, copy it to your Application Support folder, E.G /Users/Alice/Library/Application Support/blirc
* On most other Unix-based operating systems, copy it to ~/.config/blirc

Rename config.ini.example to config.ini after copying it to it's destination, then edit it and change / add whatever settings you need.

## Keybinds

Here's a complete list of the keybinds you need to use the program. These will be customisable in the future.

|Shortcut|Description|
|--------|-----------|
|<kbd>/</kbd>|Send a message.|
|<kbd>m</kbd>|Say the message currently focused in the buffer.|
|<kbd>N</kbd>|Say the name of the currently selected network.|
|<kbd>B</kbd>|Say the name of the currently selected buffer.|
|<kbd>-</kbd> and <kbd>=</kbd>|Switch networks.|
|<kbd>SHIFT+-</kbd> and <kbd>SHIFT+=</kbd>|Switch to the first and last network, respectively.|
|<kbd>[</kbd> and <kbd>]</kbd>|Switch buffers.|
|<kbd>SHIFT+[</kbd> and <kbd>SHIFT+]</kbd>|Switch to the first and last buffer, respectively.|
|<kbd>,</kbd> and <kbd>.</kbd>|Go up and down the list of messages in the current buffer.|
|<kbd>SHIFT+,</kbd> and <kbd>SHIFT+.</kbd>|Switch to the first and last message, respectively.|
|<kbd>CTRL+1-9</kbd>|Switch to the nth network.|
|<kbd>CTRL+0</kbd>|Switch to the last network.|
|<kbd>1-9</kbd>|Switch to the nth buffer in the current network.|
|<kbd>0</kbd>|Switch to the last buffer in the current network.|

## License

    Blirc: Your favourite blindy IRC client
    Copyright (C) 2022-2023  Michael Connor Buchan <mikey@blindcomputing.org>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
