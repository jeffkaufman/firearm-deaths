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
#   W34: unspecified gun unintentional
#   X72 handgun suicide
#   X73 longgun suicide
#   X74 unspecified gun suicide
#   X93 handgun homicide
#   X94 longgun homicide
#   X95 unspecified gun homide
#   Y22: handgun undetermined
#   Y23: longgun undetermined
#   Y24: unspecified gun undetermined
#   Y35: justifiable shooting
#
# Didn't include Y36.4 (war) or U01.4 (terrorism)
#
# Export results: yes

causes_handgun = ["W32", "X72", "X93", "Y22"]
causes_longgun = ["W33", "X73", "X94", "Y23"]
causes_othergun = ["W34", "X74", "X95", "Y24"]

causes_unintentional = ["W32", "W33", "W44"]
causes_suicide = ["X72", "X73", "X74"]
causes_homicide = ["X93", "X94", "X95"]
causes_undetermined = ["Y22", "Y23", "Y24"]
causes_justified = ["Y35"]

# cdc-homicides.txt
# From CDC Wonder
# https://wonder.cdc.gov/ucd-icd10.html
#
# Group Results By
#   Year
#   Single Year Ages
#   Cause of death
#   Gender
#   Race
#
# Demographics: Single-Year Ages All
#
# ICD-10 codes:
#   https://www.gunpolicy.org/firearms/citation/quotes/6107
#   X93 handgun homicide
#   X94 longgun homicide
#   X95 unspecified gun homide
#
# Export results: yes

# cdc-all-deaths.txt
# From CDC Wonder
# https://wonder.cdc.gov/ucd-icd10.html
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
        age_code = records[cols.index("Single-Year Ages Code")]
        if age_code == "NS": continue
        age = int(age_code)
        cause = records[cols.index("Cause of death Code")]
        deaths = int(records[cols.index("Deaths")])

        data[year][age][cause] = deaths
        total_firearm_deaths += deaths

# year -> age -> pop
pops = defaultdict(Counter)

# year -> age -> all deaths
all_deaths = defaultdict(Counter)
ages = set()
with open("cdc-all-deaths.txt") as inf:
    for i, line in enumerate(inf):
        records = [unquote(x) for x in line[:-1].split("\t")]
        if i == 0:
            cols = records
            continue
        if len(records)!= len(cols): continue
        if line.startswith('"Total"'): continue
        
        year = int(records[cols.index("Year")])
        age_code = records[cols.index("Single-Year Ages Code")]
        if age_code == "NS": continue
        age = int(age_code)
        ages.add(age)
        population_raw = records[cols.index("Population")]
        if population_raw == 'Not Applicable':
            continue
        population = int(population_raw)
        deaths = int(records[cols.index("Deaths")])

        pops[year][age] = population
        all_deaths[year][age] = deaths

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

fig, ax = plt.subplots(constrained_layout=True)

xs = sorted(data)
for min_age, max_age in [
        (0, 8), (9,12), (13,17), (18,25),(26,max(ages))]:
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
xs = []
ys = []
for age in sorted(ages):
    total_deaths = 0
    total_people = 0
    for year in data:
        for cause in data[year][age]:
            deaths = data[year][age][cause]
            total_deaths += deaths
        total_people += pops[year][age]

    if not total_people:
        continue
        
    xs.append(age)
    ys.append(total_deaths * 100000 / total_people)

ax.plot(xs, ys)
ax.set_ylabel("firearms deaths per 100k")
ax.set_xlabel("age")
ax.set_title("Firearms deaths by age, 1999-2020")
fig.savefig("firearms-deaths-by-age-big.png")

fig, ax = plt.subplots(constrained_layout=True)
xs = []
ys = []
for age in sorted(ages):
    total_gun_deaths = 0
    total_deaths = 0
    for year in data:
        for cause in data[year][age]:
            deaths = data[year][age][cause]
            total_gun_deaths += deaths
        total_deaths += all_deaths[year][age]

    if not total_deaths:
        continue
        
    xs.append(age)
    ys.append(100 * total_gun_deaths / total_deaths)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.plot(xs, ys)
ax.set_ylabel("Fraction of deaths from firearms")
ax.set_xlabel("age")
ax.set_title("Proportion of deaths from firearms by age, 1999-2020")
fig.savefig("firearms-death-proportion-by-age-big.png")


fig, ax = plt.subplots(constrained_layout=True)
for gun_type, causes in [
        ["handgun", causes_handgun],
        ["long gun", causes_longgun],
        ["unspecified gun", causes_othergun],
]:
    xs = []
    ys = []
    for age in sorted(ages):
        total_deaths = 0
        total_people = 0
        for year in data:
            for cause in data[year][age]:
                if cause not in causes: continue
                deaths = data[year][age][cause]
                total_deaths += deaths
            total_people += pops[year][age]

        if not total_people:
            continue
        
        xs.append(age)
        ys.append(total_deaths * 100000 / total_people)

    ax.plot(xs, ys, label=gun_type)
ax.legend()
ax.set_ylabel("firearms deaths per 100k")
ax.set_xlabel("age")
ax.set_title("Firearms deaths by age and gun type, 1999-2020")
fig.savefig("firearms-deaths-by-age-and-gun-type-big.png")
plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
motive_deaths = {}
for motive, causes in [
        ["homicide", causes_homicide],
        ["suicide", causes_suicide],
        ["unintentional, undetermined, or legal",
         causes_unintentional + causes_undetermined + causes_justified],
]:
    motive_deaths[motive] = 0
    xs = []
    ys = []
    for age in sorted(ages):
        total_deaths = 0
        total_people = 0
        for year in data:
            for cause in data[year][age]:
                if cause not in causes: continue
                deaths = data[year][age][cause]
                total_deaths += deaths
            total_people += pops[year][age]

        motive_deaths[motive] += total_deaths

        
        if not total_people:
            continue

        if motive == "suicide":
            print (age, total_deaths * 100000 / total_people)
        
        xs.append(age)
        ys.append(total_deaths * 100000 / total_people)

    ax.plot(xs, ys, label=motive)
ax.legend()
ax.set_ylabel("firearms deaths per 100k")
ax.set_xlabel("age")
ax.set_title("Firearms deaths by age and motive, 1999-2020")
fig.savefig("firearms-deaths-by-age-and-motive-big.png")
print(motive_deaths)
plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
for motive, causes in [
        ["homicide", causes_homicide],
        ["suicide", causes_suicide],
        ["other", causes_unintentional + causes_undetermined + causes_justified],
]:
    xs = []
    ys = []
    for age in sorted(ages):
        total_gun_deaths = 0
        total_deaths = 0
        for year in data:
            for cause in data[year][age]:
                if cause not in causes: continue
                deaths = data[year][age][cause]
                total_gun_deaths += deaths
            total_deaths += all_deaths[year][age]

        if not total_deaths:
            continue
        
        xs.append(age)
        ys.append(100 * total_gun_deaths / total_deaths)

    ax.plot(xs, ys, label=motive)
ax.legend()
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_xlabel("age")
ax.set_title("Proportion of deaths from firearms by age and motive, 1999-2020")
fig.savefig("firearms-deaths-proportion-by-age-and-motive-big.png")
plt.clf()

fig, ax = plt.subplots(constrained_layout=True)

xs = sorted(data)
for age in range(75):
    ys = []
    use_xs = []
    for year in xs:
        total_deaths = 0
        total_people = 0
        for cause in data[year][age]:
            deaths = data[year][age][cause]
            total_deaths += deaths
        total_people = pops[year][age]
        if not total_people: continue
        
        deaths_per_100k = total_deaths * 100000 / total_people
        ys.append(deaths_per_100k)
        use_xs.append(year)

    ax.plot(use_xs, ys, label="%s" % age)

ax.legend()
ax.set_ylabel("firearms deaths per 100k")
ax.set_xlabel("year")
ax.set_title("Firearms deaths by age over time")
fig.savefig("firearms-deaths-by-age-over-time-fine-big.png")
plt.clf()


            
