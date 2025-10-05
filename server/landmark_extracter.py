import cv2
import mediapipe as mp
import numpy as np
import torch

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

holistic = mp_holistic.Holistic(
    static_image_mode=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=2
)

def detect_landmarks(image):
    landmarks = {
        'left_hand': None,
        'right_hand': None,
        'pose': None,
        # 'face': None
    }

    results = holistic.process(image)

    if results.left_hand_landmarks:
        landmarks['left_hand'] = results.left_hand_landmarks

    if results.right_hand_landmarks:
        landmarks['right_hand'] = results.right_hand_landmarks

    if results.pose_landmarks:
        landmarks['pose'] = results.pose_landmarks

    # if results.face_landmarks:
    #     landmarks['face'] = results.face_landmarks

    return landmarks

def process_frame(frame):
    frame = cv2.resize(frame, (640, 480))
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = detect_landmarks(frame_rgb)

    if result['left_hand']:
      mp_drawing.draw_landmarks(frame, result['left_hand'], mp_holistic.HAND_CONNECTIONS)

    if result['right_hand']:
      mp_drawing.draw_landmarks(frame, result['right_hand'], mp_holistic.HAND_CONNECTIONS)

    if result['pose']:
      mp_drawing.draw_landmarks(frame, result['pose'], mp_holistic.POSE_CONNECTIONS)

    # if result['face']:
    #   mp_drawing.draw_landmarks(frame, result['face'], mp_holistic.FACEMESH_TESSELATION)

    return frame

def normalize_landmarks(landmarks):
  left_shoulder, right_shoulder = landmarks[2][11], landmarks[2][12]

  # shoulder center
  root = (left_shoulder + right_shoulder) / 2.0

  scale = torch.linalg.norm(left_shoulder - right_shoulder).to(dtype=torch.float64)

  # avoid division by 0
  if scale < 1e-6:
    scale = 1.0

  landmarks[0] = (landmarks[0] - root) / scale
  landmarks[1] = (landmarks[1] - root) / scale
  landmarks[2] = (landmarks[2] - root) / scale
  # landmarks[3] = (landmarks[3] - root) / scale

  # new_lm = old_lm + (to_point - from_point)
  landmarks[0] += (landmarks[2][16] - landmarks[0][0])
  landmarks[1] += (landmarks[2][15] - landmarks[1][0])
  # landmarks[3] += (landmarks[2][0] - landmarks[3][1])

  return landmarks

def extract_landmarks(image):
  if image.shape[0] == 3:
    image = image.permute((1, 2, 0))

  image = np.array(image)

  original_landmarks = []
  num_landmarks = {
      'left_hand': 21,
      'right_hand': 21,
      'pose': 25,
      # 'pose': 33,
      'face': 0
      # 'face': 468
  }

  result = detect_landmarks(image)

  for part_type, landmarks in result.items():
    if landmarks:
      landmark_list = torch.tensor([(lm.x,lm.y,lm.z,lm.visibility) for lm in landmarks.landmark], dtype=torch.float64)
      landmark_list = landmark_list[:num_landmarks[part_type]]
    else:
      landmark_list = torch.tensor([(0,0,0,0)] * num_landmarks[part_type], dtype=torch.float64)

    original_landmarks.append(landmark_list)

  normalized_landmarks = normalize_landmarks(original_landmarks)
  original_landmarks = torch.concat(normalized_landmarks, dim=0)

  return original_landmarks.to(dtype=torch.float64)