import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2
import json
import pickle
import sys
sys.path.append("./segment-anything")
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import argparse
import os
sam_checkpoint = "./segment-anything/sam_vit_h_4b8939.pth"
model_type = "vit_h"
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint).to(device=device).eval()
predictor = SamPredictor(sam)
def to_sam_bbox(x,y, width, height):
    """
    Convert (x, y, width, height) to SAM bounding box format (x0, y0, x1, y1).
    """
    x0 = x
    y0 = y
    x1 = x + width
    y1 = y + height
    return np.array([x0, y0, x1, y1])
def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0,0,0,0), lw=2))
def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)
def prompt_with_box(image_path, save_path, input_box):
    # input_box = np.array([425, 600, 700, 875])
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    predictor.set_image(image)
    masks, _, _ = predictor.predict(
        point_coords=None,
        point_labels=None,
        box=input_box[None, :],
        multimask_output=False,
    )
    # Save mask as numpy array
    np.save(save_path, masks[0])
    return masks[0]
bbox_dir = "./boxes" # put the bbox json files here
image_dir = "./artwork_images"  #put the figures here
image_name="프리마베라"
save_dir = "./masks"
os.makedirs(save_dir, exist_ok=True)
bbox_path = os.path.join(bbox_dir, image_name+".json")
with open(bbox_path, 'r') as f:
    bbox_data = json.load(f)
image_path = os.path.join(image_dir, image_name+".jpg")
save_2nd_dir = os.path.join(save_dir, image_name.replace(".jpg", ""), "array")
os.makedirs(save_2nd_dir, exist_ok=True)
for bbox in bbox_data["bounding_boxes"]:
    id_num = bbox["id"]
    save_path = os.path.join(save_2nd_dir, f"{image_name}_sam_mask_{id_num:04d}.npy")
    input_box = to_sam_bbox(x=bbox["x"],
                y=bbox["y"],
                width=bbox["width"],
                height=bbox["height"])
    print(f"Processing {image_name} with box {input_box}")
    mask = prompt_with_box(image_path, save_path, input_box)
    print(f"Saved mask to {save_path}")
    