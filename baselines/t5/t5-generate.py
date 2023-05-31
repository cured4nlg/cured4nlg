import os, sys
import torch

from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config
from transformers import Trainer, TrainingArguments
from transformers import AdamW

CHECKPOINT_DIR = './checkpoints/'
MODEL = sys.argv[1]

tokenizer = T5Tokenizer.from_pretrained('t5-small', extra_ids=0,
                                        additional_special_tokens=['[DATE]', '[REGION]', '[ROW]', '[TOTAL]'])

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

with open('data/' + sys.argv[2]) as f:
  test_src = f.readlines()
with open('data/' + sys.argv[3]) as f:
  test_trg = f.readlines()

test_encodings = tokenizer(test_src,  padding=True, truncation=True, max_length=1024)
test_labels = tokenizer(test_trg, padding=True, truncation=True)

test_dataset = Dataset(test_encodings, test_labels)

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model = T5ForConditionalGeneration.from_pretrained(os.path.join(CHECKPOINT_DIR, MODEL))
model.to(device)
model.eval()

data_loader = torch.utils.data.DataLoader(test_dataset, batch_size=4)
gens = []

for batch in data_loader:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        outputs = model.generate(input_ids, attention_mask=attention_mask, max_length=512, num_beams=5)
        for output, label in zip(outputs, labels):
            gens.append(tokenizer.decode(output))

gens = list(map(lambda g: g.replace('<pad>', '', 512).replace('</s>', '').strip(), gens))

with open('outputs/' + MODEL.split('/')[0] + '.gens.txt', 'w') as f:
    f.write('\n'.join(gens))


import sacrebleu

refs = []
for ref in test_trg:
  refs.append(ref)

bleu = sacrebleu.corpus_bleu(gens, [refs])
print('BLEU score: %f' % bleu.score)