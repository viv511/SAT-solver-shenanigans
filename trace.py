import cv2
import numpy as np
import sys

HEIGHT_SCALE = 5
LENGTH = 75
SCALE = 100
FPS = 1000

# only take every FRAME_JUMP-th line to speed up the video and make it more watchable LOL
FRAME_JUMP = 10 

# both in the "traces" folder
INPUT_TRACE_FILE = "traces/o11-l75.txt"
OUTPUT_VIDEO_FILE = INPUT_TRACE_FILE.replace(".txt", ".mp4")

def displayChar(c):
    if(c == '█'):
        # white
        return np.full((SCALE, SCALE, 3), 255, dtype=np.uint8)
    elif(c == '░'):
        # black
        return np.full((SCALE, SCALE, 3), 0, dtype=np.uint8)
    elif(c == '-'):
        # grey
        return np.full((SCALE, SCALE, 3), 128, dtype=np.uint8)
    else:
        # unknown/invalid/unassigned char
        print("warning! unknown char in trace:", c)
        exit(1)

def lineToFrame(line):
    frame = np.zeros((SCALE * HEIGHT_SCALE, (LENGTH + 1) * SCALE, 3), dtype=np.uint8)

    for i, c in enumerate(line.strip()):
            block = displayChar(c)
            startX = i * SCALE
            endX = (i + 1) * SCALE

            # corresponding block at pos i
            for j in range(HEIGHT_SCALE):
                startY = j * SCALE
                endY = (j + 1) * SCALE

                frame[startY:endY, startX:endX] = block
    
    return frame

def visualizeTrace():
    width = (LENGTH + 1) * SCALE
    height = SCALE * HEIGHT_SCALE

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(OUTPUT_VIDEO_FILE, fourcc, FPS, (width, height))

    count = 0

    with open(INPUT_TRACE_FILE, "r") as f:
        for i, line in enumerate(f):
            if(i % FRAME_JUMP != 0):
                continue

            if(i % 1000 == 0):
                print(f"Processing line {i}...")
            line = line.strip()

            if len(line) != (LENGTH + 1):
                print(f"warning! line {i} has length {len(line)} instead of {(LENGTH + 1)}")
                continue

            frame = lineToFrame(line)
            writer.write(frame)
            count += 1

    writer.release()

    print(f"done! output video saved to {OUTPUT_VIDEO_FILE} :)")

if __name__ == "__main__":
    visualizeTrace()