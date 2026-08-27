# **FIT Time Shifter**

A lightweight Python utility for adjusting timestamps inside **Garmin FIT activity files**.

It applies a user-specified time offset (positive or negative) to all `timestamp` fields in the FIT messages, producing a corrected FIT file.

The offset is in **seconds**, unlike you can find on many online FIT time shifter tools, and it completely works locally: nothing leaves your computer.

The file may be then be used with other utilities: my main usage has been to load it in Insta360 Studio to show a dashboard with speed, position, and other during my activity, which I tracked with my Garmin watch and recorded with my Insta360 action cam.
You may also upload the file to Garmin Connect or other fitness platforms.


---

## **✨ Why this project is useful**

- Corrects activities recorded with wrong device time (e.g., after traveling across time zones).
- Allows batch processing via command-line mode.
- Provides a simple GUI for casual users (via `tkinter`).
- Uses the official **Garmin Python FIT SDK** for reliable decoding/encoding.
- Automatically skips invalid fields (e.g., `NaN`) to prevent encoder crashes.
- Produces clean, valid FIT files ready to use or upload.


---

## **🚀 Getting Started**

### **Prerequisites**

Install the Garmin FIT SDK for Python:

```bash
pip install garmin-fit-sdk
```

This script uses:
- `garmin-fit-sdk` for FIT decoding/encoding  
- `tkinter` for GUI dialogs  
- Standard Python libraries (`sys`, `os`, `math`)


---

## **📦 Installation**

Clone or download this repository, then simply run:

```bash
python3 FITTimeShifter.py
```

No additional setup required.


---

## **🖥️ Usage**

### **GUI Mode (default)**

Just double-click the script.  
You will be prompted to:

1. Select the input `.fit` file  
2. Enter the wanted time shift (in seconds)  
3. Choose the output file name  

You can also drag-and-drop a FIT file onto the script.

### **Command-Line Mode**

Useful for automation or batch processing:

```bash
python3 FITTimeShifter.py <infile> <outfile> <offset>
```

Where:

- `<infile>` — input FIT file  
- `<outfile>` — output FIT file  
- `<offset>` — time shift in seconds  
  - Positive → activity starts later  
  - Negative → activity starts earlier  

Example (starts the activity 1 hour earlier):

```bash
python3 FITTimeShifter.py activity.fit activity_shifted.fit -3600
```


---

## **👥 Contributions**

Contributions are welcome!
I do not have specific guidelines, please simply send me a PR and I'll evaluate it


---

## **🏷️ Badges**

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-1.0-orange)


---
Note: this README has been AI-generated, and sligthly edited manually
