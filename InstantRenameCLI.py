import os
import re
import glob
import shutil
import argparse

shareregex = re.compile(
    r"^(.*) ([0-9]+)\.([0-9]+)\.([0-9]+) - ([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)(\.DVR)?\.mp4$")

logList = []

def getFiles(inputpath: str) -> list:
    """Gathers all files from subfolders and makes sure they match the Nvidia Share format."""
    # Gather all relevant files
    files = glob.glob(os.path.join(inputpath, "*/*.mp4"))
    # Filter out oddly named folders
    files = filter(lambda f: os.path.isfile(f), files)
    # Filter out files based on regex
    files = filter(shareregex.match, files)
    return files


def getFileInfo(filename: str, options: dict) -> dict:
    """Turns filename into a useful information dict.

    filename (str): Full path to the file.
    options (dict): provides the following
    #validate (bool): Open the file to make sure it's encoded with "GeForce SHARE" and set the "valid" key accordingly.
    #spacechar (str): Replace spaces in game/app name with this symbol.
    #dvrtext (str)
    """
    groups = shareregex.match(os.path.basename(filename)).groups()
    info = {
        "valid": False,
        "app": groups[0].replace(" ", options["spacechar"]),
        "year": groups[1],
        "shortyear": groups[1][-2:],
        "month": groups[2],
        "day": groups[3],
        "hour": groups[4],
        "minute": groups[5],
        "second": groups[6],
        "index": groups[7],
        "dvr": options["dvrval"] if groups[8] else "",
        "isdvr": bool(groups[8]),
        "original": os.path.basename(filename),
    }
    # Generate ISO8601-like dates
    info["date"] = f"{info['year']}-{info['month']}-{info['day']}"
    info["time"] = f"{info['hour']}-{info['minute']}-{info['second']}"
    # Validate that the file is encoded by "GeForce SHARE"
    if options["validate"]:
        with open(filename, 'rb') as file:
            file.seek(-47, os.SEEK_END)  # Note minus sign
            if (file.read() == b'EncodedBy\x00\x00\x00\x01\x00\x00\x00"\x00\x08G\x00e\x00F\x00o\x00r\x00c\x00e\x00 \x00S\x00H\x00A\x00R\x00E\x00\x00\x00'):
                info["valid"] = True
    return info


def moveFile(filename: str, targetname: str, simulate: bool) -> bool:
    """Move files, but only simulate if desired. Returns True on error."""
    if os.path.exists(targetname):
        log(f"Can't move {filename} to {targetname}: target file already exists")
        return True
    log(f"{'[Simulated] ' if simulate else ''}Moved {filename} -> {targetname}")
    if not simulate:
        try:
            shutil.move(filename,targetname)
        except Exception as e:
            log(f"Can't move {filename} to {targetname}: {e}")
            return True
    return False


def log(text):
    global logList
    print(text)
    logList.append(text)

def formatName(formatstr, info):
    name = formatstr.format(
            app=info["app"], game=info["app"],
            date=info["date"],
            time=info["time"],
            y=info["year"], year=info["year"],
            sy=info["shortyear"], shortyear=info["shortyear"],
            m=info["month"], month=info["month"], mo=info["month"],
            d=info["day"], day=info["day"],
            h=info["hour"], hour=info["hour"],
            min=info["minute"], minute=info["minute"],
            s=info["second"], second=info["second"],
            i=info["index"], index=info["index"],
            original=info["original"],orig=info["original"],
            dvr=info["dvr"])
    return name

def process(options):
    global logList
    logList = []
    files = getFiles(options["inputpath"])
    for file in files:
        info = getFileInfo(file, options)
        if options["validate"] != info["valid"]:
            log(f'Skipping {info["original"]} because it failed to validate (use --skip-validate to move anyways)')
            continue
        outname = formatName(options["format"], info)
        outpath = options["targetpath"]
        if options["dvrpath"] and info["isdvr"]:
            outpath = options["dvrpath"]
        if options["nodvrpath"] and not info["isdvr"]:
            outpath = options["nodvrpath"]
        if (moveFile(file,os.path.join(outpath,outname),options["simulate"])):
            log(f"Exiting due to critical error")
            return logList
    log("Simulated successfully!" if options["simulate"] else "Completed successfully!")
    return logList

def app():
    defaultformat = "{date}.{time}.{app}.mp4"
    defaultdvrval = "DVR"
    parser = argparse.ArgumentParser(description='A simple tool to move and rename Nvidia Share (Shadowplay) recordings to a more sensible format.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('inputpath', type=str,
                        help='Folder that contains the folders of the original Nvidia Share recordings.')
    parser.add_argument('targetpath', type=str,
                        help='Folder where recordings will be moved to.')
    parser.add_argument('--format', type=str, metavar="FORMAT", default=defaultformat,
                        help='''New filename format (default: "''' + defaultformat + '''")\n\nFormatting options:
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
                {dvr} - Only present if recording is DVR, set text with --dvrval\n\n''')
    parser.add_argument('--dvrval', metavar="DVR", default="DVR", type=str,
                        help=f'Set the value for the {{dvr}} formatting option (default: "{defaultdvrval}").')
    parser.add_argument('--dvrpath', metavar="PATH", type=str,
                        help='Move DVR clips here instead of targetpath.')
    parser.add_argument('--nodvrpath', metavar="PATH", type=str,
                        help='Move non-DVR clips here instead of targetpath.')
    parser.add_argument('--spacechar', metavar="x", default=" ", type=str,
                        help='Replace spaces in app/game name with this character.')
    parser.add_argument('--simulate', action='store_true',
                        help="Simulate the process and don't actually move the files.")
    parser.add_argument('--skip-validate', dest="validate", action='store_false',
                        help="Skip validating that the files are actually Nvidia Share files.")
    #parser.add_argument('--skip-rename', dest="rename", action='store_false',
    #                    help="Skip renaming files, just move.")
    #parser.add_argument('--skip-move', dest="move", action='store_false',
    #                    help="Skip moving files, just rename.")
    args = parser.parse_args()
    process(vars(args))

if __name__ == '__main__':
    app()
