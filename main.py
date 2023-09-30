from src.cmdline import execute
from src.logger import log


def main():
    try:
        execute()
        log.catch_exit()
    except KeyboardInterrupt:
        log.catch_exit()
    except Exception as e:
        if isinstance(e, AssertionError):
            log.error("[x] Some tests are failing")
        else:
            log.error(e)

        log.fail_exit()


if __name__ == "__main__":
    main()
