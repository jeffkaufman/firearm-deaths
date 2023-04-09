#!/usr/bin/env python3

from collections import defaultdict, Counter

# cdc.txt
# From CDC Wonder
# https://wonder.cdc.gov/ucd-icd10.html
#
# Group Results By
#   Year
#   Single Year Ages
#   Cause of death
#   Gender
#
# Demographics: Single-Year Ages All
#
# ICD-10 codes:
#   https://www.gunpolicy.org/firearms/citation/quotes/6107
#   W32: handgun unintentional
#   W33: longgun unintentional
#   W34: other gun unintentional
#   X72 handgun suicide
#   X73 longgun suicide
#   X74 other gun suicide
#   X93 handgun homicide
#   X94 longgun homicide
#   X95 other gun homide
#   Y22: handgun undetermined
#   Y23: longgun undetermined
#   Y24: other gun undetermined
#   Y35: justifiable shooting
#
# Didn't include Y36.4 (war) or U01.4 (terrorism)
#
# Export results: yes


# cdc-all-deaths.txt
# From CDC Wonder
#
# Group Results By
#   Year
#   Single Year Ages
#
# Demographics: Single-Year Ages All
#
# Export results: yes

def unquote(x):
    if x.startswith('"') and x.endswith('"'):
        return x[1:-1].strip()
    return x

# year -> age -> cause -> [deaths, % of total deaths]
data = defaultdict(lambda: defaultdict(Counter))
total_firearm_deaths = 0
with open("cdc.tsv") as inf:
    for i, line in enumerate(inf):
        records = [unquote(x) for x in line[:-1].split("\t")]
        if i == 0:
            cols = records
            continue
        if len(records) != len(cols): continue
        year = int(records[cols.index("Year")])
        age = int(records[cols.index("Single-Year Ages Code")])
        cause = records[cols.index("Cause of death Code")]
        deaths = int(records[cols.index("Deaths")])

        data[year][age][cause] = deaths
        total_firearm_deaths += deaths

# year -> age -> pop
pops = defaultdict(Counter)

# year -> age -> all deaths
all_deaths = defaultdict(Counter)

with open("cdc-all-deaths.txt") as inf:
    for i, line in enumerate(inf):
        records = [unquote(x) for x in line[:-1].split("\t")]
        if i == 0:
            cols = records
            continue
        if len(records)!= len(cols): continue
        if line.startswith('"Total"'): continue
        
        year = int(records[cols.index("Year")])
        age = int(records[cols.index("Single-Year Ages Code")])
        population = int(records[cols.index("Population")])
        deaths = int(records[cols.index("Deaths")])

        pops[year][age] = population
        all_deaths[year][age] = deaths

import matplotlib.pyplot as plt

fig, ax = plt.subplots(constrained_layout=True)

xs = sorted(data)
for min_age, max_age in [(0, 8), (9,12), (13,17)]:
    ys = []
    for year in xs:
        total_deaths = 0
        total_people = 0
        for age in range(min_age, max_age+1):
            for cause in data[year][age]:
                deaths = data[year][age][cause]
                total_deaths += deaths
            total_people += pops[year][age]

        deaths_per_100k = total_deaths * 100000 / total_people
        ys.append(deaths_per_100k)

    ax.plot(xs, ys, label="%s-%s" % (min_age, max_age))

ax.legend()
ax.set_ylabel("firearms deaths per 100k")
ax.set_xlabel("year")
ax.set_title("Firearms deaths by age over time")
fig.savefig("firearms-deaths-by-age-over-time-big.png")
plt.clf()


            
fig, ax = plt.subplots(constrained_layout=True)

xs = sorted(data)
for age in range(18):
    ys = []
    for year in xs:
        total_deaths = 0
        total_people = 0
        for cause in data[year][age]:
            deaths = data[year][age][cause]
            total_deaths += deaths
        total_people += pops[year][age]

        deaths_per_100k = total_deaths * 100000 / total_people
        ys.append(deaths_per_100k)

    ax.plot(xs, ys, label="%s" % age)

ax.legend()
ax.set_ylabel("firearms deaths per 100k")
ax.set_xlabel("year")
ax.set_title("Firearms deaths by age over time")
fig.savefig("firearms-deaths-by-age-over-time-fine-big.png")
plt.clf()


            
