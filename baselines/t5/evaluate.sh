
reference_file=$1
hypothesis_file=$2
table_file=$3

cat $reference_file | \
  perl ~/nmt/OpenNMT-py/tools/tokenizer.perl -q | \
  perl ~/nmt/lowercase.perl > ref.txt

cat $hypothesis_file | \
  perl ~/nmt/OpenNMT-py/tools/tokenizer.perl -q | \
  perl ~/nmt/lowercase.perl > hypo.txt

cat $table_file | \
  perl ~/nmt/lowercase.perl > tabl.txt

# BLEU
perl ~/nmt/scorers/multi-bleu.perl ref.txt < hypo.txt

# METEOR
java -Xmx2G -jar ~/nmt/scorers/meteor-1.5/meteor-1.5.jar \
  hypo.txt \
  ref.txt \
  -l en |
  tail -n1 | \
  sed 's/ \+ /\t/g' | \
  cut -f2

# TER
java -jar ~/nmt/scorers/myTercom.jar -h hypo.txt -r ref.txt

# PARENT-W
source activate language
python ~/language/language/table_text_eval/table_text_eval.py \
  --references ref.txt \
  --generations hypo.txt  \
  --tables tabl.txt

rm ref.txt hypo.txt tabl.txt

