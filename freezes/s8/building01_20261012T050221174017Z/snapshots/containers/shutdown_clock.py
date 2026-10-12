#!/usr/bin/env python3
"""EOF-only administrative clock advance to wake native ROS Rate.sleep."""
import time
from pathlib import Path
import yaml
import rospy
from rosgraph_msgs.msg import Clock

rospy.init_node('administrative_eof_clock', anonymous=True, disable_signals=True)
publisher = rospy.Publisher('/clock', Clock, queue_size=1)
time.sleep(.5)  # Wall time: never block on the stopped replay clock.
bag_end = float(yaml.safe_load(Path('/output/bag_info.yaml').read_text())['end'])
# /clock is not latched: this subscriber starts after EOF and may receive
# no messages. The index end is an upper bound on the exhausted bag clock.
stamp = max(bag_end, rospy.Time.now().to_sec())
if stamp < 1_000_000_000:
    raise RuntimeError('replay clock not received; refusing reset or backwards clock')
print('EOF-only administrative clock; no sensor input or performance samples', stamp, flush=True)
while True:
    stamp += .01
    publisher.publish(Clock(clock=rospy.Time.from_sec(stamp)))
    time.sleep(.01)
