# Author: Rodrigo Graca
import sys

from timelapse import Timelapse, createParser

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
