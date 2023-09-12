# CURED4NLG Dataset

CURED4NLG is designed as a resource to motivate further research into data-to-text generation. 

For further details, see our paper / poster, presented at [LDK 2023 – 4th Conference on Language, Data and Knowledge](http://2023.ldk-conf.org).

If you use this data, please cite the above paper.

## Abstract
We introduce CURED4NLG, a dataset for the task of table-to-text generation focusing on the public health domain.
The dataset consists of 280 pairs of tables and documents extracted from weekly epidemiological reports published by the [World Health Organisation](https://www.who.int) (WHO).
The tables report the number of cases and deaths from COVID-19, while the documents describe global and regional updates in English text.
Along with the releasing the dataset, we present outputs from three different baselines for the task of table-to-text generation.
Our results suggest that end-to-end models can learn a template-like structure of the reports to produce fluent sentences, but may contain many factual errors especially related to numerical values.
