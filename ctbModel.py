'''
Vineet Kumar, sioom.ai
'''

from pytorch_lightning import LightningModule
import torch
from logging import getLogger
from sys import exit
from typing import Dict, List

logg = getLogger(__name__)


class ctbModel(LightningModule):
    def __init__(self, model_type: str, len_tokenizer: int = None):
        logg.debug('')
        super().__init__()
        self.model_type = model_type
        if model_type == "gpt2":
            from transformers import GPT2LMHeadModel
            self.model = GPT2LMHeadModel.from_pretrained('distilgpt2')
            self.save_hyperparameters()
            assert len_tokenizer is not None
            self.model.resize_token_embeddings(len_tokenizer)
        else:
            logg.critical(f'unknown model: {model_type}')
            exit()

    def forward(self):
        logg.debug('')

    def training_step(self, batch: Dict[str, torch.Tensor],
                      batch_idx: int) -> torch.Tensor:
        logg.debug('')
        loss = self.run_model(batch)
        # logger=True => TensorBoard; x-axis is always in steps=batches
        self.log('train_loss',
                 loss,
                 on_step=False,
                 on_epoch=True,
                 prog_bar=True,
                 logger=False)
        return loss

    def training_epoch_end(self,
                           training_step_outputs: List[Dict[str,
                                                            torch.Tensor]]):
        logg.debug('')
        avg_loss = torch.stack([x['loss']
                                for x in training_step_outputs]).mean()
        # on TensorBoard, want to see x-axis in epochs (not steps=batches)
        self.logger.experiment.add_scalar('train_loss_epoch', avg_loss,
                                          self.current_epoch)

    def validation_step(self, batch: Dict[str, torch.Tensor],
                        batch_idx: int) -> torch.Tensor:
        logg.debug('')
        loss = self.run_model(batch)
        # checkpoint-callback monitors epoch val_loss, so on_epoch=True
        self.log('val_loss',
                 loss,
                 on_step=False,
                 on_epoch=True,
                 prog_bar=True,
                 logger=False)
        return loss

    def validation_epoch_end(self, val_step_outputs: List[torch.Tensor]):
        logg.debug('')
        avg_loss = torch.stack([x for x in val_step_outputs]).mean()
        # on TensorBoard, want to see x-axis in epochs (not steps=batches)
        self.logger.experiment.add_scalar('val_loss_epoch', avg_loss,
                                          self.current_epoch)

    def test_step(self, batch: Dict[str, torch.Tensor],
                  batch_idx: int) -> torch.Tensor:
        logg.debug('')
        '''
        batch, y = batch
        y_hat = self(batch)

        loss = F.cross_entropy(y_hat, y.long())
        labels_hat = torch.argmax(y_hat, dim=1)
        n_correct_pred = torch.sum(y == labels_hat).item()

        return {'test_loss': loss, "n_correct_pred": n_correct_pred, "n_pred": len(y)}
    '''

    def test_step_end(self, batch_parts):
        logg.debug('')

    def test_epoch_end(self, test_step_outputs: List[torch.Tensor]):
        logg.debug('')
        '''
        avg_loss = torch.stack([x['test_loss'] for x in outputs]).mean()
        test_acc = sum([x['n_correct_pred'] for x in outputs]) / sum(x['n_pred'] for x in outputs)
        tensorboard_logs = {'test_loss': avg_loss, 'test_acc': test_acc, 'step': self.current_epoch}

        return {'log': tensorboard_logs}
    '''

    def run_model(self, batch: Dict[str, torch.Tensor]) -> torch.Tensor:
        outputs = self.model(**batch, labels=batch["input_ids"])
        return outputs[0]  # mean of losses from each example in batch

    def configure_optimizers(self):
        logg.debug('')
        return torch.optim.Adam(
            [p for p in self.parameters() if p.requires_grad],
            lr=2e-05,
            eps=1e-08)
