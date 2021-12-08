# Author: Rodrigo Graca
import sys, argparse

from timelapse import Timelapse

def createParser():
    parser = argparse.ArgumentParser(
        prog="Zen's Timelapse",
        description="Create timelapsed videos"
    )

    parser.add_argument(
        "--id",
        "--camID",
        metavar="camera id",
        default=0,
        type=int,
        help="Which camera (usually 0 or 1) you'd like to use"
    )
    parser.add_argument(
        "-i",
        "--capInt",
        "--capInterval",
        metavar="interval",
        default=5,
        type=int,
        help="Seconds between taking each photo"
    )
    parser.add_argument(
        "-p",
        "--capPeriod",
        metavar="period",
        default=60,
        type=int,
        help="Specifies length of the timelapse in seconds"
    )

    parser.add_argument(
        "--headless",
        default=False,
        action="store_true",
        help="If specified, will not display live view"
    )

    return parser

def main():
    parser = createParser()
    args = parser.parse_args()

    timelapse = Timelapse(
        camID=args.id,
        camRes=(1920, 1080),
        capInterval=args.capInt,
        capPeriod=args.capPeriod,
        headless=args.headless,
        genVideo=False
    )
    timelapse.start()

    try:
        timelapse.join()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
