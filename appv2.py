import torch
import torch.nn as nn
import torch.nn.functional as F

class SingleSliceAttentionLoss(nn.Module):
    """
    Ensures weight updates if even one slice is positive (OR-gate logic).
    """
    def __init__(self, alpha=0.05, lambda_max=0.5):
        super().__init__()
        self.alpha = alpha           # Weight for entropy regularization
        self.lambda_max = lambda_max # Weight for the max-slice loss component

    def forward(self, slice_logit, bag_logit, y):
        """
        slice_logit : (B, N) raw logits from SliceTumourDetector
        bag_logit   : (B,)    raw logit from gated-attention classifier
        y           : (B,)    0/1 volume label
        """
        slice_prob = torch.sigmoid(slice_logit)  # (B, N)
        y_float = y.float()

        # 1. Main Bag Loss (Gated Attention)
        # This updates the model based on the aggregated information
        bag_loss = F.binary_cross_entropy_with_logits(bag_logit, y_float)

        # 2. Max-Slice Loss (The "Single Slice" update)
        # We take the maximum logit across all slices. If the volume is positive (y=1),
        # at least this max slice must be pushed towards 1.
        max_slice_logit, _ = slice_logit.max(dim=1)
        max_loss = F.binary_cross_entropy_with_logits(max_slice_logit, y_float)

        # 3. Entropy Regularizer
        # Keeps slice predictions from being "lazy" (0.5)
        ent = - (slice_prob * torch.log(slice_prob + 1e-7) +
                 (1 - slice_prob) * torch.log(1 - slice_prob + 1e-7))
        ent_loss = ent.mean() * self.alpha

        # Total Loss
        # Combining bag_loss and max_loss ensures that even if attention is spread thin,
        # the strongest slice signal is penalized if it doesn't match y.
        total_loss = bag_loss + (self.lambda_max * max_loss) + ent_loss

        return total_loss, {
            'bag_prob': torch.sigmoid(bag_logit),
            'max_slice_prob': slice_prob.max(dim=1)[0],
            'loss_bag': bag_loss.item(),
            'loss_max': max_loss.item()
        }