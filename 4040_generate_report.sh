#!/bin/bash

rm -f html_table_confusion_matrix.html report.html.template report.html

cp report_files/report.html.template .

# convert the confusion matrix to a HTML table
perl report_files/generate_html_table.pl confusion_matrix.txt html_table_confusion_matrix.html

# insert the table into the report template
sed '/INSERT_TABLE_HERE/r html_table_confusion_matrix.html' report.html.template | sed '/INSERT_TABLE_HERE/d' > report.html
