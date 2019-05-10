import cv2
import numpy as np


def tracker(frames, bboxes):
    # Create MultiTracker object
    print(len(frames), len(bboxes))
    multiTracker = cv2.MultiTracker_create()

    # Initialize MultiTracker
    for bbox in bboxes:
        multiTracker.add(cv2.TrackerCSRT_create(), frames[0], bbox)

    video = [[] for _ in bboxes]

    # Process video and track objects
    for frame in frames:
        # get updated location of objects in subsequent frames
        success, boxes = multiTracker.update(frame)

        # draw tracked objects
        for i, newbox in enumerate(boxes):
            crop_frame = frame[int(newbox[1]):int(
                newbox[1] + newbox[3]), int(newbox[0]):int(newbox[0] + newbox[2])]
            crop_frame = cv2.resize(crop_frame, (224, 224),
                                    interpolation=cv2.INTER_AREA)
            video[i].append(crop_frame)

    return np.array(video)
