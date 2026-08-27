#!/usr/bin/env python3
####################################################################################################
#
#   *************************************
#   |   FIT Time Shifter                |
#   *************************************
#
#   FIT file manipulator that edits the activity recording time by a specified offset in seconds [s]
#   Takes an input file, which will not be touched, and produces an output file with the modified time
#   Negative values will make the activity start earlier
#   Positive values will make the activity start later
#   The strategy used is to apply the offset to all "timestamp" fields in the FIT messages
#
#
#   REQUIREMENTS    ------------------------------
#
#   * Garmin Python FIT SDK
#       Install it by running:
#       pip install garmin-fit-sdk
#
#
#   USAGE    -------------------------------------
#
#   * Standard mode (with GUI)
#       Symply double-click the script; it will ask the input file location, the time shift offset,
#       and the output file name
#       OR
#       Drop the input FIT file onto the script; it will ask the time shift offset and the output
#       file name
#
#   * Pure command-line mode (no GUI, useful for batches)
#       Run it with the following parameters:
#       FITTimeShifter.py <infile> <outfile> <offset>
#       where:
#       <infile>    Input file name
#       <outfile>   Output file name
#       <offset>    Time shifting offset in seconds [s]
#
#
####################################################################################################


import math     # For isnan()
import sys      # For sys.argv
import os       # For os.path
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog
from garmin_fit_sdk import Decoder, Encoder, Stream, Profile


##### CONSTANTS
APPNAME = "FIT Time Shifter"
APPVERSION = 1

EXIT_NOINPUTFILE = 1
EXIT_NOOUTPUTFILE = 2
EXIT_BAD_TIMESHIFT = 3
EXIT_USERCANCEL = 4
EXIT_DECODE_ERROR = -1
EXIT_UNKNOWN_MESSAGENR_STRING_ERROR = -2

PARAMIDX_INFILE = 1
PARAMIDX_OUTFILE = 2
PARAMIDX_TIMESHIFT = 3


##### GLOBAL VARIABLES
MODE_PURE_CMDLINE = False   # When enabled, sets "Pure Command-line Mode".
                            # In Pure Command-Line Mode, no GUI window will be opened


##### USAGE
out_fpath = None
timeshift_s = None
if len(sys.argv) >= PARAMIDX_TIMESHIFT+1:
    MODE_PURE_CMDLINE = True
    out_fpath = sys.argv[PARAMIDX_OUTFILE]
    try:
        timeshift_s = int(sys.argv[PARAMIDX_TIMESHIFT])
    except ValueError:
        print("Bad timeshift parameter '%s'. Please enter an integer number, unit: seconds [s]. Positive will make the activity start later, negative will make the activity start earlier" % sys.argv[3])
        exit(EXIT_BAD_TIMESHIFT)


##### INPUT FILE SELECTION
if len(sys.argv) >= PARAMIDX_INFILE+1:
    in_fpath = sys.argv[PARAMIDX_INFILE]
else:
    in_fpath = tkinter.filedialog.askopenfilename(
        title = "%s v%d - Select input FIT file" % (APPNAME, APPVERSION),
        filetypes = ( ("FIT files", ".fit"), )
        )
if len(in_fpath) == 0:
    # No file to open: quit
    exit(EXIT_NOINPUTFILE)


##### TIMESHIFT AMOUNT SELECTION
if timeshift_s == None:
    timeshift_userdata = tkinter.simpledialog.askinteger("%s v%d" % (APPNAME, APPVERSION), "Enter timeshift amount, in seconds [s].\nPositive values will make the activity start later\nNegative values will make the activity start earlier")
    if timeshift_userdata == None:
        # No timeshift amount: quit
        exit(EXIT_USERCANCEL)
    timeshift_s = int(timeshift_userdata)
print("[INFO] Requested timeshift: %d seconds" % timeshift_s)


##### DECODE DATA, modifying it on the fly using a mesg_listener callback
stream = Stream.from_file(in_fpath)
decoder = Decoder(stream)

# * "messages" is a dict of messages, which keys are message number and values are a list of messages.
#   So all the FIT messages are organized in separated lists, identified by their "message number", in FIT nomenclature (which actually tells what the message "type" is it)
#   Each list contains the messages as a dict containing the message data: keys are the field name and values the field value
# * "errors" is a list of errors happened during the decoding of the FIT file
messages, errors = decoder.read(
    convert_datetimes_to_dates = False     # Set to allow easy editing of the timestamps by applying an offset in seconds
    )


##### SHOW DATA INFO
if len(errors) != 0:
    errmsg = "ERRORS in the input FIT file, aborting processing.\n" + \
        "===== ERROR LIST =====\n" + \
        str(errors) + "\n" + \
        "----------\n"
    print(errmsg)
    if not MODE_PURE_CMDLINE:
        tkinter.messagebox.showerror("%s - %d" % (APPNAME, APPVERSION), errmsg)
    exit(EXIT_DECODE_ERROR)

print("===== INFO =====")
print(messages.keys())
print("----------\n\n")
#print("===== MESSAGES =====")
#print(messages)
#print("----------\n\n")


##### PROCESS & ENCODE DATA
# Process all FIT messages and pass them to the encoder
encobj = Encoder()
for mesg_str, msglist in messages.items():    # Iterate over all messages, categorized by message number
    # Retrieve the message number and check its validity
    if mesg_str.endswith("_mesgs"):
        mesg_strid = mesg_str[:-len("_mesgs")]
        mesg_num = Profile["mesg_num"][mesg_strid.upper()]
    else:
        # Try converting the string to int, to use it as a direct message number
        try:
            n = int(mesg_str)
        except ValueError:
            errmsg = "ERROR processing the decoded message dict.\nUnexpected message string ID: %s\nAborting processing" % mesg_str
            print(errmsg)
            if not MODE_PURE_CMDLINE:
                tkinter.messagebox.showerror("%s - %d" % (APPNAME, APPVERSION), errmsg)
            exit(EXIT_UNKNOWN_MESSAGENR_STRING_ERROR)
        else:
            if not n in Profile["messages"]:
                print("[INFO] Skipping messages with number %d because it's not listed in the Profile messages" % n)
                continue
            mesg_num = str(n)

    for mesg in msglist:
        # Examine the message data, throwing away bad data
        wmsg = {}
        for k, v in mesg.items():
            if k == "timestamp":    # This is a timestamp field: edit it by adding the requested offset
                wmsg[k] = v + timeshift_s
                continue

            if isinstance(v, float) and math.isnan(v):  # This is a field with a "NaN" value, which will cause an error in the encoder: skip it
                print("[INFO] Skipping field '%s' of message number %d (%s) because it has an invalid value (NaN)" % (k, n, mesg_str))
                continue

            # Save all the other fields unchanged
            wmsg[k] = v

        # Send the processed message to the decoder
        try:
            encobj.on_mesg(mesg_num, wmsg)
        except Exception as e:
            errmsg = "[ENCODER ERROR] %s --- while processing message %s:%s" % (e, mesg_num, mesg)
            print(errmsg)
            if not MODE_PURE_CMDLINE:
                res = tkinter.messagebox.askokcancel("%s - %d" % (APPNAME, APPVERSION), errmsg)
                if not res:
                    exit(EXIT_USERCANCEL)

# Get encoded FIT bytes
fit_bin_data = encobj.close()
# Write the bytes to a file
if out_fpath == None:
    workdir, in_fname = os.path.split(in_fpath)
    out_fname = os.path.splitext(in_fname)[0] + "_timeshifted.fit"
    out_fpath = tkinter.filedialog.asksaveasfilename(
        title = "%s v%d - Select output FIT file" % (APPNAME, APPVERSION),
        initialdir = workdir,
        initialfile = out_fname,
        filetypes = ( ("FIT files", ".fit"), )
        )
if len(out_fpath) == 0:
    # No file to write: quit
    exit(EXIT_NOOUTPUTFILE)
with open(out_fpath, 'wb') as f:
    f.write(fit_bin_data)

if not MODE_PURE_CMDLINE:
    tkinter.messagebox.showinfo("%s - %d" % (APPNAME, APPVERSION), "Timeshifting by %d seconds completed" % timeshift_s)




