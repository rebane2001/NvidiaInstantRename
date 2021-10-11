# NvidiaInstantRename
A simple tool to move and rename [Nvidia Share](https://www.nvidia.com/en-us/geforce/geforce-experience/shadowplay/) (Shadowplay) recordings to a more sensible format.

# [Tutorial/Showcase video](https://www.youtube.com/watch?v=E2uyvlV9OGs)

![GUI](img/gui.png?raw=true)

![Comparison](img/comparison.png?raw=true)

https://www.youtube.com/watch?v=E2uyvlV9OGs

## Using the GUI
If you are not a programmer and wish to simply use the GUI, go to the [Releases](https://github.com/rebane2001/NvidiaInstantRename/releases) page and download the exe of the latest version - then run it. Note that Windows SmartScreen might block it due to it not being popular and signed.

# Using the CLI

```
usage: InstantRenameCLI.py [-h] [--format FORMAT] [--dvrval DVR] [--dvrpath PATH] [--nodvrpath PATH] [--spacechar x] [--simulate] [--skip-validate]
                           inputpath targetpath

A simple tool to move and rename Nvidia Share (Shadowplay) recordings to a more sensible format.

positional arguments:
  inputpath         Folder that contains the folders of the original Nvidia Share recordings.
  targetpath        Folder where recordings will be moved to.

optional arguments:
  -h, --help        show this help message and exit
  --format FORMAT   New filename format (default: "{date}.{time}.{app}.mp4")

                    Formatting options:
                                    {app} - Application/Game name
                                   {date} - Date, formatted with dashes
                                   {time} - Time, formatted with dashes
                         {sy}/{shortyear} - Year, last two digits
                               {y}/{year} - Year
                              {m}/{month} - Month
                                {d}/{day} - Day
                               {h}/{hour} - Hour (24h)
                           {min}/{minute} - Minute
                             {s}/{second} - Second
                              {i}/{index} - Index number set by Nvidia Share after the date and time
                        {orig}/{original} - Original filename (without path)
                                    {dvr} - Only present if recording is DVR, set text with --dvrval

  --dvrval DVR      Set the value for the {dvr} formatting option (default: "DVR").
  --dvrpath PATH    Move DVR clips here instead of targetpath.
  --nodvrpath PATH  Move non-DVR clips here instead of targetpath.
  --spacechar x     Replace spaces in app/game name with this character.
  --simulate        Simulate the process and don't actually move the files.
  --skip-validate   Skip validating that the files are actually Nvidia Share files.
```

## Compiling the GUI
Run `pyinstaller --onefile .\InstantRenameGUI.pyw`, the exe will be in `/dist`.

> Legal disclaimer: The name of the project is just a play on "Nvidia Instant Replay" and is not in any way officially made or endorsed by Nvidia. Also while it shouldn't happen, I take no responsibility if this program somehow deletes or corrupts your files.
