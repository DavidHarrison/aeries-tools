#!/bin/sh
#gets test data as json to be used with GradeCalculator and OptimalGrades (using OGTest)
#requires aeries-cli to be in $PATH as aeries
DATA_FILE='test-data.json'
cat /dev/null > "$DATA_FILE"
echo "[" >> "$DATA_FILE"
for gradebook in Eng Chem French Comp Calc US Journalism
do
	echo "getting gradebook $gradebook"
	aeries -b "$gradebook" >> "$DATA_FILE"
	if [ "$gradebook" != "Journalism" ]
	then
		echo "," >> "$DATA_FILE"
	fi
done
echo "]" >> "$DATA_FILE"
