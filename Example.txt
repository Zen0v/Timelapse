# Example commands to run Timelapse class from CLI

# Use [python3 timelapse.py -h] to display command info

# Defaults
Camera ID: 1                        Which camera should be used, normally on laptops cam #1 is the built-in
Capture interval: 5 seconds         How often should a photo be taken
Capture Period: 60 seconds          How long the program should run and take captures
Headless: False                     If enabled, will perform normally, but no visual display
Preview: False                      Shows a small cam view to align your shot
Stitch: False                       Stitches all frames in capture dir together into video

# Capture a picture every 30 seconds and stop capture after 3600 seconds (1 hour)
python3 timelapse.py -i 30 -p 3600 --preview

# Use the second camera to capture timelapse
python3 timelapse.py --id 2
