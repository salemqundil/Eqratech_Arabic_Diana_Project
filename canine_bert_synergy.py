"""
canine_bert_synergy.py
Helper for synergistic training of CANINE and BERT models.
"""

import torch
from torch import nn


class CanineBertSynergyHelper(nn.Module):
    def __init__(self, canine_model, bert_model, fusion_mode="concat", loss_weights=None):
        super().__init__()
        self.canine = canine_model
        self.bert = bert_model
        self.fusion_mode = fusion_mode
        self.loss_weights = loss_weights or {"canine": 1.0, "bert": 1.0}
        if fusion_mode == "attention":
            self.attn = nn.MultiheadAttention(
                embed_dim=canine_model.config.hidden_size + bert_model.config.hidden_size, num_heads=4
            )

    def forward(self, input_ids, attention_mask=None, labels=None):
        canine_out = self.canine(input_ids, attention_mask=attention_mask, labels=labels)
        bert_out = self.bert(input_ids, attention_mask=attention_mask, labels=labels)
        # Feature fusion
        if self.fusion_mode == "concat":
            fused = torch.cat([canine_out.last_hidden_state, bert_out.last_hidden_state], dim=-1)
        elif self.fusion_mode == "sum":
            fused = canine_out.last_hidden_state + bert_out.last_hidden_state
        elif self.fusion_mode == "attention":
            fused, _ = self.attn(
                torch.cat([canine_out.last_hidden_state, bert_out.last_hidden_state], dim=-1),
                torch.cat([canine_out.last_hidden_state, bert_out.last_hidden_state], dim=-1),
                torch.cat([canine_out.last_hidden_state, bert_out.last_hidden_state], dim=-1),
            )
        else:
            fused = canine_out.last_hidden_state
        # Loss synergy
        loss = None
        if labels is not None:
            canine_loss = canine_out.loss if hasattr(canine_out, "loss") else None
            bert_loss = bert_out.loss if hasattr(bert_out, "loss") else None
            if canine_loss is not None and bert_loss is not None:
                loss = self.loss_weights["canine"] * canine_loss + self.loss_weights["bert"] * bert_loss
            elif canine_loss is not None:
                loss = canine_loss
            elif bert_loss is not None:
                loss = bert_loss
        return {"fused": fused, "canine_out": canine_out, "bert_out": bert_out, "loss": loss}
