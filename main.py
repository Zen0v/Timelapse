# Author: Rodrigo Graca
import sys

from timelapse import Timelapse, createParser, Res

def main():
    parser = createParser()
    args = parser.parse_args()

    timelapse = Timelapse(
        camID=args.id,
        camRes=Res.x720,
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

def test():
    timelapse = Timelapse(
        camID=0,
        camRes=Res.x720,
        capInterval=5,
        capPeriod=30,
        headless=True,
        genVideo=True
    )
    timelapse.preview()
    timelapse.start()

    try:
        timelapse.join()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
