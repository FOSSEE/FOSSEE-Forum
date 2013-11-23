def get_video_info(path):
    """Uses ffmpeg to determine information about a video. This has not been broadly
    tested and your milage may vary"""
 
    from decimal import Decimal
    import subprocess
    import re
 
    process = subprocess.Popen(['/usr/bin/ffmpeg', '-i', path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    duration_m = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?)", stdout, re.DOTALL).groupdict()
    info_m = re.search(r": Video: (?P<codec>.*?), (?P<profile>.*?), (?P<width>.*?)x(?P<height>.*?), ", stdout, re.DOTALL).groupdict()

    hours = Decimal(duration_m['hours'])
    minutes = Decimal(duration_m['minutes'])
    seconds = Decimal(duration_m['seconds'])

    total = 0
    total += 60 * 60 * hours
    total += 60 * minutes
    total += seconds

    info_m['duration'] = total
    info_m['width'] = int(info_m['width'])
    info_m['height'] = int(info_m['height'])
    return info_m
