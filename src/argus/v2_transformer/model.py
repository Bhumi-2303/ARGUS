import torch
import torch.nn as nn
import math

class GroupTokenEmbedder(nn.Module):
    def __init__(self, d_model=32, num_protocols=256):
        super().__init__()
        self.d_model = d_model
        
        # Token 1: Size (3 dims)
        self.proj_size = nn.Linear(3, d_model)
        # Token 2: Volumetric (2 dims)
        self.proj_vol = nn.Linear(2, d_model)
        # Token 3: Protocol (Proto ID + tcp_flag_density)
        self.proto_embed = nn.Embedding(num_protocols, d_model - 1)
        # Token 4: Directional (2 dims)
        self.proj_dir = nn.Linear(2, d_model)
        # Token 5: Timing (2 dims)
        self.proj_time = nn.Linear(2, d_model)
        
        # Group positional embeddings (6 tokens: CLS + 5 groups)
        self.group_pos_embed = nn.Parameter(torch.randn(1, 6, d_model))
        
        # CLS Token
        self.cls_token = nn.Parameter(torch.randn(1, 1, d_model))

    def forward(self, x_size, x_vol, x_proto_id, x_tcp_density, x_dir, x_time):
        batch_size = x_size.size(0)
        
        # Token 1
        emb_size = self.proj_size(x_size).unsqueeze(1)
        # Token 2
        emb_vol = self.proj_vol(x_vol).unsqueeze(1)
        # Token 3
        p_emb = self.proto_embed(x_proto_id) # (B, d_model-1)
        emb_proto = torch.cat([p_emb, x_tcp_density.unsqueeze(-1)], dim=-1).unsqueeze(1)
        # Token 4
        emb_dir = self.proj_dir(x_dir).unsqueeze(1)
        # Token 5
        emb_time = self.proj_time(x_time).unsqueeze(1)
        
        # CLS
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        
        # Concat: [B, 6, d_model]
        tokens = torch.cat([cls_tokens, emb_size, emb_vol, emb_proto, emb_dir, emb_time], dim=1)
        tokens = tokens + self.group_pos_embed
        
        return tokens

class V2TransformerClassifier(nn.Module):
    def __init__(self, d_model=32, nhead=4, num_layers=2):
        super().__init__()
        self.embedder = GroupTokenEmbedder(d_model=d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=d_model*4, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.classifier = nn.Linear(d_model, 2)
        
    def forward(self, inputs):
        # inputs is a dict containing tensors and key_padding_mask
        tokens = self.embedder(
            inputs['size'], inputs['vol'], inputs['proto_id'], 
            inputs['tcp_density'], inputs['dir'], inputs['time']
        )
        
        # mask shape: [B, 6] (True means ignore). index 0 is CLS (always False)
        mask = inputs.get('key_padding_mask', None)
        
        out = self.transformer(tokens, src_key_padding_mask=mask)
        cls_out = out[:, 0, :] # Take CLS token
        logits = self.classifier(cls_out)
        return logits
