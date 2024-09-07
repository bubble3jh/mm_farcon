import dataset
from torch.utils.data import DataLoader
# Mock directory tree
# total_attribute_list=['age/old',
#  'age/young',
#  'arab-muslim/arab-muslim',
#  'arab-muslim/other-people',
#  'asian/american',
#  'asian/asian-american',
#  'asian/european-american',
#  'asian/foreign',
#  'disabled/abled',
#  'disabled/disabled',
#  'disabled/disabled-people',
#  'gender/career',
#  'gender/family',
#  'gender/female',
#  'gender/liberal-arts',
#  'gender/male',
#  'gender/science',
#  'insect-flower/flower',
#  'insect-flower/insect',
#  'intersectional/black',
#  'intersectional/black-female',
#  'intersectional/black-male',
#  'intersectional/female',
#  'intersectional/male',
#  'intersectional/white',
#  'intersectional/white-female',
#  'intersectional/white-male',
#  'native/euro',
#  'native/native',
#  'native/us',
#  'native/world',
#  'presidents/bush',
#  'presidents/clinton',
#  'presidents/kennedy',
#  'presidents/lincoln',
#  'presidents/trump',
#  'race/african-american',
#  'race/african-american-female',
#  'race/african-american-male',
#  'race/european-american',
#  'race/european-american-female',
#  'race/european-american-male',
#  'religion/christianity',
#  'religion/judaism',
#  'sexuality/gay',
#  'sexuality/straight',
#  'skin-tone/dark',
#  'skin-tone/light',
#  'valence/pleasant',
#  'valence/pleasant-1',
#  'valence/unpleasant',
#  'valence/unpleasant-1',
#  'weapon/black',
#  'weapon/tool',
#  'weapon/tool-modern',
#  'weapon/weapon',
#  'weapon/weapon-modern',
#  'weapon/white',
#  'weight/fat',
#  'weight/thin']
total_attribute_list=['american_race/african-american-google',
'american_race/asian-american-google',
'american_race/european-american-google']

import os
import json
import torch
from PIL import Image
from torchvision import transforms
import clip

def preprocess_and_save_embeddings(root_dir, attributes_list, save_dir, clip_model="ViT-B/32", device="cuda"):
    model, preprocess = clip.load(clip_model, device=device)
    for parent, _, _ in os.walk(root_dir):
        parent_attribute = parent.split('/')[-2]  # Parent directory
        attribute = parent.split('/')[-1]  # Current directory
        combined_attribute = f"{parent_attribute}/{attribute}"  # Combine parent and attribute
        if combined_attribute in attributes_list:
            image_data = []
            caption_data = []
            captions_path = os.path.join(parent, "captions.json")
            
            if os.path.exists(captions_path):
                with open(captions_path, 'r') as f:
                    captions = json.load(f)
                
                for item in captions:
                    image_path = os.path.join(root_dir, item['image_path'])
                    caption = item['caption']

                    # Convert caption to clip embedding
                    caption_token = clip.tokenize([caption]).to(device)
                    caption_embedding = model.encode_text(caption_token).detach().cpu().numpy()

                    # Convert image to clip embedding
                    image = Image.open(image_path).convert("RGB")
                    image = preprocess(image).unsqueeze(0).to(device)
                    image_embedding = model.encode_image(image).detach().cpu().numpy()

                    image_data.append({
                        "image_embedding": image_embedding,
                    })
                    
                    caption_data.append({
                        "caption_embedding": caption_embedding
                    })

            # Prepare save directories and paths
            os.makedirs(save_dir, exist_ok=True)
            attribute_save_dir = os.path.join(save_dir, combined_attribute)
            os.makedirs(attribute_save_dir, exist_ok=True)
            
            if clip_model == "ViT-L/14":
                clip_model = "ViT-L14"
            if clip_model == "ViT-B/32":
                clip_model = "ViT-B32"
            
            image_save_path = os.path.join(attribute_save_dir, f"{clip_model}_img.pt")
            
            # Always save image embeddings
            image_embeddings = [item['image_embedding'] for item in image_data]
            torch.save(image_embeddings, image_save_path)

            # Save caption embeddings only if captions.json exists
            if os.path.exists(captions_path):
                caption_save_path = os.path.join(attribute_save_dir, f"{clip_model}_caption.pt")
                print(f"generating caption pt {caption_save_path}")
                caption_embeddings = [item['caption_embedding'] for item in caption_data]
                torch.save(caption_embeddings, caption_save_path)
            else:
                print(f"pass caption saving {captions_path}")


root_dir='/data1/bubble3jh/git_FarconVAE/data/mm_experiments_added/'
for a in total_attribute_list:
    for model in ['RN50x4', 'ViT-L/14', 'ViT-B/32']:
        preprocess_and_save_embeddings(root_dir=root_dir,attributes_list=[a], save_dir="/data1/bubble3jh/git_FarconVAE/data/.preprocess", clip_model=model)
        print(f'{a} weight saved')
# root_dir='/data1/bubble3jh/farcon/FarconVAE_git/data/mm'
# custom_dataset=dataset.MMDataset(root_dir=root_dir, attributes_list=['gender/male'], return_raw=False)
# dataloader = DataLoader(custom_dataset, batch_size=4, shuffle=False)

# for i, (image, attribute, caption) in enumerate(dataloader):
#     print("Batch:", i)