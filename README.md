# Cashew scripts
This repo holds some scripts I wrote to analyze my data from
[Cashew](https://github.com/jameskokoska/Cashew), a free and open-source budget
app created by James Kokoska. I've been using Cashew to track my money since
January 2024, so I'm happy to say I have enough data to perform some basic data
analysis and manage my finances in a more informed manner.

## Prerequisites
To run these scripts, you will need:
- Python 3
- SQL file exported from Cashew app ("More" at bottom right corner > Settings &
  Customization > Backups > Export Cashew Data File)
- CSV file exported from ebtEDGE app (sign in, then select your card, then go to
  See More > Statements > Email and email the CSV to yourself)

# Aligning EBT data with Cashew data
`./align_ebt_with_cashew.py cashew.sql ebt.csv` brings Cashew up to date with
EBT data by ensuring each EBT purchase has a corresponding entry in Cashew.

# Getting average expenditure
`./get_avg_expenditure.py cashew.sql` prints the monthly expenses and income
from the last 12 months and then prints the average monthly expenditure.

I made this script because I became frustated by the the paywall popups in the
app and I didn't know how to use the GUI to get what I wanted. So this script
doesn't currently have any more capabilities than the GUI, but it is extensible
in a way that the GUI is not.
