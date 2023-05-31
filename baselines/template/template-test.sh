python template.py 2021-04-06 2021-03-30
python template.py 2021-04-13 2021-04-06
python template.py 2021-04-20 2021-04-13
python template.py 2021-04-27 2021-04-20
python template.py 2021-05-04 2021-04-27
python template.py 2021-05-11 2021-05-04
python template.py 2021-05-18 2021-05-11

mkdir -p outputs/
mv *out outputs/
cd outputs/

paste -d'\n' 2021-04-06-global.out 2021-04-06-africa.out 2021-04-06-americas.out 2021-04-06-eastern-mediterranean.out 2021-04-06-europe.out 2021-04-06-south-east-asia.out 2021-04-06-western-pacific.out 2021-04-13-global.out 2021-04-13-africa.out 2021-04-13-americas.out 2021-04-13-eastern-mediterranean.out 2021-04-13-europe.out 2021-04-13-south-east-asia.out 2021-04-13-western-pacific.out 2021-04-20-global.out 2021-04-20-africa.out 2021-04-20-americas.out 2021-04-20-eastern-mediterranean.out 2021-04-20-europe.out 2021-04-20-south-east-asia.out 2021-04-20-western-pacific.out 2021-04-27-global.out 2021-04-27-africa.out 2021-04-27-americas.out 2021-04-27-eastern-mediterranean.out 2021-04-27-europe.out 2021-04-27-south-east-asia.out 2021-04-27-western-pacific.out 2021-05-04-global.out 2021-05-04-africa.out 2021-05-04-americas.out 2021-05-04-eastern-mediterranean.out 2021-05-04-europe.out 2021-05-04-south-east-asia.out 2021-05-04-western-pacific.out 2021-05-11-global.out 2021-05-11-africa.out 2021-05-11-americas.out 2021-05-11-eastern-mediterranean.out 2021-05-11-europe.out 2021-05-11-south-east-asia.out 2021-05-11-western-pacific.out 2021-05-18-global.out 2021-05-18-africa.out 2021-05-18-americas.out 2021-05-18-eastern-mediterranean.out 2021-05-18-europe.out 2021-05-18-south-east-asia.out 2021-05-18-western-pacific.out > template-baseline.out

cd -
