import cv2
import mediapipe as mp
import numpy as np
import torch

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

holistic = mp_holistic.Holistic(
    static_image_mode=False,
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
    result = detect_landmarks(frame)

    if result['left_hand']:
      mp_drawing.draw_landmarks(frame, result['left_hand'], mp_holistic.HAND_CONNECTIONS)

    if result['right_hand']:
      mp_drawing.draw_landmarks(frame, result['right_hand'], mp_holistic.HAND_CONNECTIONS)

    if result['pose']:
      mp_drawing.draw_landmarks(frame, result['pose'], mp_holistic.POSE_CONNECTIONS)

    # if result['face']:
    #   mp_drawing.draw_landmarks(frame, result['face'], mp_holistic.FACEMESH_TESSELATION)

    return frame


default_landmarks = torch.load('data/default_landmarks.pth')

def normalize_vector(v):
    return v / (torch.norm(v) + 1e-8)

def hand_rotation_matrix(wrist, index, pinky):
    """
    Compute 3D rotation matrix for a hand using wrist-index-pinky landmarks.
    """
    x_axis = normalize_vector(index - wrist)
    y_axis = normalize_vector(pinky - wrist)
    z_axis = normalize_vector(torch.cross(x_axis, y_axis, dim=0))

    # Re-orthogonalize
    y_axis = normalize_vector(torch.cross(z_axis, x_axis, dim=0))
    R = torch.stack([x_axis, y_axis, z_axis], dim=1)  # shape (3,3)
    return R

def align_hand_landmarks(last_hand, curr_pose, part_type):
    """
    Align previous hand landmarks to current hand rotation using 3D rotation matrix.
    """
    if curr_pose is None:
        return last_hand

    # Extract landmarks
    wrist_prev, index_prev, pinky_prev = last_hand[0], last_hand[5], last_hand[17]

    if part_type == 'left_hand':
      wrist_curr, index_curr, pinky_curr = curr_pose[16], curr_pose[20], curr_pose[18]
    else:
      wrist_curr, index_curr, pinky_curr = curr_pose[15], curr_pose[19], curr_pose[17]

    # Get rotation matrices for previous and current hand orientations
    R_prev = hand_rotation_matrix(wrist_prev, index_prev, pinky_prev)
    R_curr = hand_rotation_matrix(wrist_curr, index_curr, pinky_curr)

    # Compute rotation from prev → curr
    R = R_curr @ R_prev.T  # shape (3,3)

    # Center last hand to its wrist
    L_centered = last_hand - wrist_prev

    # Rotate and translate
    L_rotated = (L_centered @ R.T) + wrist_curr

    return L_rotated

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
  landmarks[0] += (landmarks[2][15] - landmarks[0][0])
  landmarks[1] += (landmarks[2][16] - landmarks[1][0])
  # landmarks[3] += (landmarks[2][0] - landmarks[3][1])

  return landmarks

def extract_landmarks(image): 
  if image.shape[0] == 3:
    image = image.permute(1, 2, 0)

  image = np.array(image)

  num_landmarks = {
      'left_hand': 21,
      'right_hand': 21,
      'pose': 25,
      # 'pose': 33,
      # 'face': 468
  }

  result = detect_landmarks(image)

  extracted_result = {}

  for part_type, landmarks in result.items():
    if landmarks:
      landmark_list = torch.tensor([(lm.x,lm.y,lm.z) for lm in landmarks.landmark], dtype=torch.float64)
      extracted_result[part_type] = landmark_list[:num_landmarks[part_type]]

  return extracted_result

def correct_landmarks(extracted_landmarks, prev_landmarks):
  original_landmarks = []
  parts = ['left_hand', 'right_hand', 'pose']

  if 'pose' in extracted_landmarks:
    pose_lm = extracted_landmarks['pose']
  else:
    pose_lm = prev_landmarks['pose']

  for part_type in parts:
    if part_type not in extracted_landmarks:
      if part_type == 'left_hand' or part_type == 'right_hand':
        # Missing Hand Landmarks
        landmark_list = align_hand_landmarks(prev_landmarks[part_type], pose_lm, part_type)
        # landmark_list = torch.tensor([(0,0,0)] * num_landmarks[part_type], dtype=torch.float64)

      else:
        # Missing Pose Landmarks
        landmark_list = prev_landmarks[part_type]

    else:
        # Available landmarks
        landmark_list = extracted_landmarks[part_type]

    original_landmarks.append(landmark_list)

  original_landmarks = normalize_landmarks(original_landmarks)

  original_landmarks = torch.concat(original_landmarks, dim=0)
  return original_landmarks.to(dtype=torch.float64)