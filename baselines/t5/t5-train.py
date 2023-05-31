import os, sys
import torch

from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config
from transformers import Trainer, TrainingArguments
from transformers import AdamW

NAME = sys.argv[1]

with open('data/' + sys.argv[2]) as f:
  train_src = f.readlines()
with open('data/' + sys.argv[3]) as f:
  train_trg = f.readlines()

train_src = list(map(lambda s: s.strip(), train_src))
train_trg = list(map(lambda s: s.strip(), train_trg))

with open('data/' + sys.argv[4]) as f:
  valid_src = f.readlines()
with open('data/' + sys.argv[5]) as f:
  valid_trg = f.readlines()

valid_src = list(map(lambda s: s.strip(), valid_src))
valid_trg = list(map(lambda s: s.strip(), valid_trg))

tokenizer = T5Tokenizer.from_pretrained('t5-small', extra_ids=0,
                                        additional_special_tokens=['[DATE]', '[REGION]', '[ROW]', '[TOTAL]'])

train_encodings = tokenizer(train_src,  padding=True, truncation=True, max_length=1024)
train_labels = tokenizer(train_trg, padding=True, truncation=True)

valid_encodings = tokenizer(valid_src,  padding=True, truncation=True, max_length=1024)
valid_labels = tokenizer(valid_trg, padding=True, truncation=True)


class Dataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels['input_ids'][idx])
        return item

    def __len__(self):
        return len(self.labels['input_ids'])

train_dataset = Dataset(train_encodings, train_labels)
valid_dataset = Dataset(valid_encodings, valid_labels)

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

training_args = TrainingArguments(
    output_dir='./checkpoints/' + NAME,
    save_total_limit = 2,
    do_train=True,
    do_eval=True,
    evaluation_strategy="epoch",
    load_best_model_at_end=True,
    max_steps=5000,
    save_steps=1000,
    eval_steps=250,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    warmup_steps=250,
    weight_decay=0.01,
    logging_dir='./logs/' + NAME,
    logging_steps=250,
    seed=717,
)

model = T5ForConditionalGeneration.from_pretrained('t5-small')
model.to(device)
model.train()

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=valid_dataset
)

trainer.train()



import gc

model = None
gc.collect()
with torch.no_grad():
    torch.cuda.empty_cache()

model = T5ForConditionalGeneration.from_pretrained(trainer.state.best_model_checkpoint)
model.to(device)
model.eval()

data_loader = torch.utils.data.DataLoader(valid_dataset, batch_size=4)
gens = []

for batch in data_loader:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        outputs = model.generate(input_ids, attention_mask=attention_mask, max_length=512, num_beams=5)
        for output, label in zip(outputs, labels):
            gens.append(tokenizer.decode(output))

gens = list(map(lambda g: g.replace('<pad>', '', 512).replace('</s>', '').strip(), gens))



import sacrebleu

refs = []
for ref in valid_trg:
  refs.append(ref)

bleu = sacrebleu.corpus_bleu(gens, [refs])

print('Best checkpoint: %s' % trainer.state.best_model_checkpoint)
print('Validation BLEU score: %f' % bleu.score)
