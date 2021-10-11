import PySimpleGUI as sg
import InstantRenameCLI

theme = {
    "BACKGROUND": "#262B2F",
    "TEXT": "#FFFFFF",
    "INPUT": "#212326",
    "TEXT_INPUT": "#FFFFFF",
    "SCROLL": "#76B900",
    "BUTTON": (
        "#FFFFFF",
        "#76B900"
    ),
    "PROGRESS": (
        "#000000",
        "#000000"
    ),
    "BORDER": 1,
    "SLIDER_DEPTH": 0,
    "PROGRESS_DEPTH": 0
}
sg.theme_add_new('NvidiaTheme', theme)
sg.theme('NvidiaTheme')

layout = [
    [sg.Text("NvidiaInstantRename - A simple tool to move and rename Nvidia Share (Shadowplay) recordings to a more sensible format.")],
    [
    sg.TabGroup([[
            sg.Tab('General', [
                [sg.Text("Source folder      "), sg.In(key="source"), sg.FolderBrowse(enable_events=True)],
                [sg.Text("Destination folder"), sg.In(key="dest"), sg.FolderBrowse(enable_events=True)],
                [sg.Text("Filename format  "), sg.In("{date}.{time}.{app}{dvr}.mp4", key="format", enable_events=True)],
                [sg.Text("placeholder", key="formatexample"),],
                
                [sg.Checkbox("Validate (prevent moving non-shadowplay files)", default = True, key="validate")],
            ]),
            sg.Tab('Advanced', [
                [sg.Text("DVR indicator ({dvr} in formatting)"), sg.In(".DVR", key="dvrval")],
                [sg.Text("Replace space character with (in app name)"), sg.In("_", key="spacechar", size=(1,0))],
                [sg.Text("DVR-only destination folder"), sg.In("", key="dvrpath")],
                [sg.Text("non-DVR destination folder"), sg.In("", key="nodvrpath")],
            ]),
            sg.Tab('Help', [
                [sg.Text('''Formatting options:
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
    {dvr} - Only present if recording is DVR, set text with "DVR indicator" in Advanced''')],
            ])
        ]], key="groups", enable_events=True
        )
    
    ],
    [sg.Button("Quit", font='Any 12 bold'), sg.Button("Preview", font='Any 12 bold'), sg.Button("Move/Rename", font='Any 12 bold')],
    [sg.Listbox(
            values=["Output will appear here..."], enable_events=True, size=(100, 20), expand_x=True, expand_y=True, key="logs"
        )]
]

def showExample(window,values):
    info = {
        "app": "Video Game Name".replace(" ", values["spacechar"]),
        "date": "2021-11-30",
        "time": "17-31-43",
        "year": "2021",
        "shortyear": "21",
        "month": "11",
        "day": "30",
        "hour": "17",
        "minute": "31",
        "second": "43",
        "index": "123",
        "dvr": values["dvrval"],
        "original": "Video Game Name 2021.11.30 - 17.31.43.123.DVR.mp4",
    }
    try:
        window["formatexample"].update(f"Example: {InstantRenameCLI.formatName(values['format'],info)}")
    except:
        window["formatexample"].update("Error generating example")

# Create the window
window = sg.Window("NvidiaInstantRename", layout, resizable=True, finalize=True) # use_custom_titlebar=True

try:
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\NVIDIA Corporation\\Global\\ShadowPlay\\NVSPCAPS")
    value = winreg.QueryValueEx(key, "DefaultPathW")
    window["source"].update(value[0].decode(encoding='utf-16',errors='strict')[:-1])
except Exception as e:
    print(f"Failed to automatically find source folder: {e}")

event, values = window.read(timeout=0)
showExample(window,values)
# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "Quit" or event == sg.WIN_CLOSED:
        break
    if event == "Preview" or event == "Move/Rename":
        if len(values["dest"]) == 0:
            window["logs"].update(["Error: Destination not specified"])
            continue
        if len(values["format"]) == 0:
            window["logs"].update(["Error: Format not specified"])
            continue
        window["logs"].update(["Moving..."])
        try:
            logs = InstantRenameCLI.process(
                {
                    'inputpath': values["source"],
                    'targetpath': values["dest"],
                    'format': values["format"],
                    'dvrval': values["dvrval"],
                    'dvrpath': values["dvrpath"] if len(values["dvrpath"]) > 0 else None,
                    'nodvrpath': values["nodvrpath"] if len(values["nodvrpath"]) > 0 else None,
                    'spacechar': values["spacechar"],
                    'simulate': event == "Preview",
                    'validate': values["validate"]
                })
            window["logs"].update(logs)
        except Exception as e:
            window["logs"].update([f"Error: {e}"])
    if event == "format" or event == "groups":
        showExample(window,values)
window.close()