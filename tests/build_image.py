"""Build a test image, retrying only explicit registry rate-limit failures."""
import subprocess
import sys
import time


def build_image(image, context, delays=(10, 30)):
    command = ['docker', 'build', '-t', image, str(context)]
    for attempt in range(len(delays) + 1):
        try:
            output = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
            print(output, end='', flush=True)
            return
        except subprocess.CalledProcessError as error:
            output = error.output or ''
            print(output, file=sys.stderr, flush=True)
            rate_limited = any(marker in output.lower()
                               for marker in ('429 too many requests', 'toomanyrequests'))
            if not rate_limited or attempt == len(delays):
                raise
            delay = delays[attempt]
            print(f'Registry rate limit; retrying build in {delay}s '
                  f'(attempt {attempt + 2}/{len(delays) + 1}).',
                  file=sys.stderr, flush=True)
            time.sleep(delay)
