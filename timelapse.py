# Author: Rodrigo Graca
import argparse
import cv2
import sys
import enum
import glob
import logging
import os
import platform
import time
from datetime import datetime
from threading import Thread

from cv2 import VideoCapture, VideoWriter, imshow, imwrite, waitKey, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, resize


class CaptureMode(enum.Enum):
    PERIOD = 1
    CONT = 2

class Res:
    x480 = (640, 480)
    x720 = (1280, 720)
    x1080 = (1920, 1080)


class Timelapse(Thread):
    def __init__(self, camID=None, camRes=None, headless=False, genVideo=False, capInterval=5, capPeriod=60, capMode=CaptureMode.PERIOD):
        if capInterval < 1:
            logging.error("Capture interval cannot be less than 1 second")
            return

        super(Timelapse, self).__init__()
        self.camID = int(camID) if camID and camID >= 0 else self.clientPickCam()

        logging.basicConfig(level=logging.DEBUG)
        logging.info(f"Camera {self.camID + 1} selected")

        self.capDir = f"{os.getcwd()}/captures"
        self.camera = None
        self.capInterval = capInterval
        self.capPeriod = capPeriod
        self.capMode = capMode

        self.camRes = camRes
        self.displayRes = None

        self.headless = headless
        self.genVideo = genVideo

        if not os.path.exists(f"{self.capDir}"):
            os.mkdir(f"{self.capDir}")
            logging.info("No captures dir, creating...")

        self.running = False

    def run(self) -> None:
        self.running = True
        while self.running:
            try:
                self.startCapture(self.capMode)

            except KeyboardInterrupt:
                if self.genVideo or input("Make captures into video? [y/n]: ").lower().strip()[0] == 'y':
                    self.makeVideoFromCap(
                        res=(int(self.camera.get(CAP_PROP_FRAME_WIDTH)),
                             int(self.camera.get(CAP_PROP_FRAME_HEIGHT)))
                    )
                self.running = False
        self.close()

    # Simply show a window with a live camera view
    def preview(self, res=None):
        self.initCam(res=res)
        logging.info(f"{self.camRes[0]}x{self.camRes[1]}")

        logging.info("Showing camera preview")
        while True:
            success, img = self.camera.read()
            if success:
                imshow("Preview", img)

            if waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    def initCam(self, res=None):
        if not self.camera:
            if platform.system() == "Windows":
                self.camera = VideoCapture(self.camID, cv2.CAP_DSHOW)
            else:
                self.camera = VideoCapture(self.camID)
        logging.info(f"Camera {self.camID + 1} initialized")

        if res or self.camRes:
            if self.camRes is None:
                self.camRes = res

            self.camera.set(CAP_PROP_FRAME_WIDTH, self.camRes[0])
            self.camera.set(CAP_PROP_FRAME_HEIGHT, self.camRes[1])
            logging.info("Set camera resolution")
        else:
            if self.camRes is None:
                self.camRes = (int(self.camera.get(CAP_PROP_FRAME_WIDTH)), int(self.camera.get(CAP_PROP_FRAME_HEIGHT)))
            logging.info("Grabbed camera resolution")

    def startCapture(self, capMode):
        self.initCam()

        # Continuous capture mode (until Ctrl+C or q)
        if capMode is CaptureMode.CONT:
            capturing = True
            frameDelta = time.time()

            while capturing:
                success, img = self.camera.read()

                if success:
                    if not self.headless:
                        imshow("Timelapse View", resize(img, self.displayRes))

                    # If the interval passes, capture the frame and save to disk
                    if time.time() - frameDelta >= self.capInterval:
                        frameDelta = time.time()

                        logging.info(f"Captured Image from {self.camID + 1}")
                        now = datetime.now()
                        imwrite(f"{self.capDir}/{now.strftime('%Y-%m-%d_%H-%M-%S')}.png", img)
                else:
                    logging.warning(f"Could not grab frame from camera {self.camID + 1}")

                if waitKey(1) & 0xFF == ord('q'):
                    raise KeyboardInterrupt

        # Capture for period of time in seconds
        elif capMode is CaptureMode.PERIOD:
            startTime = time.time()
            frameDelta = time.time()

            while time.time() - startTime < self.capPeriod:
                success, img = self.camera.read()

                if success:
                    if not self.headless:
                        imshow("Timelapse View", img)

                    # If the interval passes, capture the frame and save to disk
                    if time.time() - frameDelta >= self.capInterval:
                        frameDelta = time.time()

                        logging.info(f"Captured Image from {self.camID + 1}")
                        now = datetime.now()
                        imwrite(f"{self.capDir}/{now.strftime('%Y-%m-%d_%H-%M-%S')}.png", img)
                else:
                    logging.warning(f"Could not grab frame from camera {self.camID + 1}")

                if waitKey(1) & 0xFF == ord('q'):
                    raise KeyboardInterrupt
            if self.genVideo:
                self.makeVideoFromCap(
                    res=(int(self.camera.get(CAP_PROP_FRAME_WIDTH)), int(self.camera.get(CAP_PROP_FRAME_HEIGHT)))
                )
            self.running = False

    def clientPickCam(self):
        # Get list of devices
        index = 0
        cams = []
        while True:
            cap = VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                cams.append(index)

            cap.release()
            index += 1

        if len(cams) == 1:
            return cams[0]

        while True:
            for cam in cams:
                print(f"[{cam + 1}]")
            camSelected = int(input("Select a camera from above: ")) - 1

            if camSelected in cams:
                return cams[camSelected]
            print(f"Camera {camSelected + 1} is an invalid selection\n")

    def makeVideoFromCap(self, filename='video.avi', fps=30, res=(1280, 720)):
        out = VideoWriter(
            filename,
            cv2.VideoWriter_fourcc(*'XVID'),
            fps,
            res
        )
        logging.info(f"Writing at {res[0]}x{res[1]}")

        for filename in glob.glob(f"{self.capDir}/*.png"):
            img = cv2.imread(filename)
            out.write(resize(img, res))

        out.release()

    def clearCapDir(self):
        for file in os.scandir(f"{os.getcwd()}/{self.capDir}"):
            os.remove(file)

    def close(self):
        cv2.destroyAllWindows()
        self.camera.release()

# From here down is for stand-alone CLI
def createParser():
    tl_parser = argparse.ArgumentParser(
        prog="Zen's Timelapse",
        description="Create timelapsed videos"
    )

    # TODO: Add flags/args: [stitch fps] [capture modes] [custom capture dir] [clear cap dir]
    tl_parser.add_argument(
        "--id",
        "--camID",
        metavar="id",
        default=0,
        type=int,
        help="Which camera (usually 1 or 2) you'd like to use"
    )
    tl_parser.add_argument(
        "-i",
        "--capInt",
        "--capInterval",
        metavar="interval",
        default=5,
        type=int,
        help="Seconds between taking each photo"
    )
    tl_parser.add_argument(
        "-p",
        "--capPeriod",
        metavar="period",
        default=60,
        type=int,
        help="Specifies length of the timelapse in seconds"
    )
    tl_parser.add_argument(
        "--headless",
        default=False,
        action="store_true",
        help="If specified, will not display live view"
    )
    tl_parser.add_argument(
        "--preview",
        default=False,
        action="store_true",
        help="Display preview of camera to setup before starting timelapse"
    )
    tl_parser.add_argument(
        "-s",
        "--stitch",
        default=False,
        action="store_true",
        help="Stitch all photos in captures directory into video"
    )

    return tl_parser


if __name__ == '__main__':
    parser = createParser()
    args = parser.parse_args()

    timelapse = Timelapse(
        camID=args.id - 1,
        camRes=Res.x720,
        capInterval=args.capInt,
        capPeriod=args.capPeriod,
        headless=args.headless,
        genVideo=args.stitch
    )

    if args.preview:
        timelapse.preview()
    timelapse.start()

    try:
        timelapse.join()
    except KeyboardInterrupt:
        sys.exit(0)
