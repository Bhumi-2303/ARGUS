import torch
ckpt = torch.load("data/raw/legacy_package/argus_coral_data/dann_results/dann_best_model.pt", map_location='cpu', weights_only=False)['model_state_dict']
for k, v in ckpt.items():
    print(f"{k}: {v.shape}")
