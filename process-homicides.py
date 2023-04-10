#!/usr/bin/env python3

from collections import defaultdict, Counter

# cdc-homicides.txt
# From CDC Wonder
# https://wonder.cdc.gov/ucd-icd10.html
#
# Group Results By
#   Year
#   Single Year Ages
#   Hispanic Origin
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

# cdc-all-gender-deaths.txt
# From CDC Wonder
# https://wonder.cdc.gov/ucd-icd10.html
#
# Group Results By
#   Year
#   Single Year Ages
#   Gender
#
# Demographics: Single-Year Ages All
#
# Export results: yes

# cdc-all-race-deaths.txt
# From CDC Wonder
# https://wonder.cdc.gov/ucd-icd10.html
#
# Group Results By
#   Year
#   Single Year Ages
#   Race
#   Hispanic Origin
#
# Demographics: Single-Year Ages All
#
# Export results: yes

def unquote(x):
    if x.startswith('"') and x.endswith('"'):
        return x[1:-1].strip()
    return x

years = set()
ages = set()
genders = set()
groups = set()

# (year, age, gender, group) -> deaths
data = Counter()

def to_group(records, cols):
    is_hispanic = records[
        cols.index("Hispanic Origin")] == "Hispanic or Latino"

    race = {
        "White": "White",
        "Black or African American": "Black",
    }.get(records[cols.index("Race")], "Other")

    return "Hispanic" if is_hispanic else race
    
#return "Hispanic" if is_hispanic else race


with open("cdc-homicides.txt") as inf:
    for i, line in enumerate(inf):
        records = [unquote(x) for x in line[:-1].split("\t")]
        if i == 0:
            cols = records
            continue
        if len(records) != len(cols): continue
        year = int(records[cols.index("Year")])
        years.add(year)
        age_code = records[cols.index("Single-Year Ages Code")]
        if age_code == "NS": continue
        age = int(age_code)
        ages.add(age)
        deaths = int(records[cols.index("Deaths")])
        gender = records[cols.index("Gender")]
        genders.add(gender)
        group = to_group(records, cols)
        groups.add(group)
        data[year, age, gender, group] = deaths

# (year, age, gender, group) -> population
populations = Counter()

# (year, age, gender, group) -> all_cause_deaths
all_cause_deaths = Counter()

for fname, gender in [
        ("cdc-all-deaths-race-female.txt", "Female"),
        ("cdc-all-deaths-race-male.txt", "Male")]:
    with open(fname) as inf:
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
            population_raw = records[cols.index("Population")]
            if population_raw == 'Not Applicable': continue
            population = int(population_raw)

            ac_deaths_raw = records[cols.index("Deaths")]
            ac_deaths = int(ac_deaths_raw)

            group = to_group(records, cols)

            all_cause_deaths[year, age, gender, group] = ac_deaths

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

fig, ax = plt.subplots(constrained_layout=True)
for gender in sorted(genders):
    xs = []
    ys = []
    for age in sorted(ages):
        total_deaths = 0
        total_people = 0
        for year in sorted(years):
            for group in sorted(groups):
                total_deaths += data[year, age, gender, group]
                total_people += populations[year, age, gender, group]

        if not total_people:
            continue

        xs.append(age)
        ys.append(total_deaths * 100000 / total_people)
    ax.plot(xs, ys, label=gender)

ax.legend()
ax.set_ylabel("firearm homicides per 100k")
ax.set_xlabel("age")
ax.set_title("Firearm homicides by age and gender, 1999-2020")
fig.savefig("firearm-homicides-by-age-and-gender-big.png")
plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
for group in sorted(groups):
    xs = []
    ys = []
    for age in sorted(ages):
        total_deaths = 0
        total_people = 0
        for year in sorted(years):
            for gender in sorted(genders):
                total_deaths += data[year, age, gender, group]
                total_people += populations[year, age, gender, group]

        if not total_people:
            continue

        xs.append(age)
        ys.append(total_deaths * 100000 / total_people)
    ax.plot(xs, ys, label=group)

ax.legend()
ax.set_ylabel("firearm homicides per 100k")
ax.set_xlabel("age")
ax.set_title("Firearm homicides by age and race/ethnicity, 1999-2020")
fig.savefig("firearm-homicides-by-age-and-race-big.png")
plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
for gender_groups in [
        ["Male", "Black"],
        ["Male", "White"],
        ["Male", "Hispanic"],
        ["Female", "Black"],
        [["Male", "Other"],
         ["Female", "Other"],
         ["Female", "White"],
         ["Female", "Hispanic"]]]:

    if type(gender_groups[0]) != type([]):
        gender_groups = [gender_groups]

    xs = []
    ys = []
    for year in sorted(years):
        total_deaths = 0
        total_people = 0

        for gender, group in gender_groups:
            for age in sorted(ages):
                total_deaths += data[year, age, gender, group]
                total_people += populations[year, age, gender, group]

        if not total_people:
            continue

        xs.append(year)
        ys.append(total_deaths * 100000 / total_people)

    if len(gender_groups) > 1:
        label = "Other"
    else:
        (gender, group), = gender_groups
        label = group + " " + gender;
    ax.plot(xs, ys, label=label)

ax.legend()
ax.set_ylabel("firearm homicides per 100k")
ax.set_xlabel("year")
ax.set_title("Firearm homicide rate by victim gender and race/ethnicity")
fig.savefig("firearm-homicide-rate-by-year-and-gender-and-race-big.png")
plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
for gender_groups in [
        ["Male", "Black"],
        ["Male", "White"],
        ["Male", "Hispanic"],
        ["Female", "Black"],
        ["Female", "White"],
        [["Male", "Other"],
         ["Female", "Other"],
         ["Female", "Hispanic"]]]:

    if type(gender_groups[0]) != type([]):
        gender_groups = [gender_groups]

    xs = []
    ys = []
    for year in sorted(years):
        total_deaths = 0

        for gender, group in gender_groups:
            for age in sorted(ages):
                total_deaths += data[year, age, gender, group]

        if not total_people:
            continue

        xs.append(year)
        ys.append(total_deaths)

    if len(gender_groups) > 1:
        label ="Other"
    else:
        (gender, group), = gender_groups
        label = group + " " + gender;
    ax.plot(xs, ys, label=label)

ax.legend()
ax.set_ylabel("firearm homicides")
ax.set_xlabel("year")
ax.set_title("Firearm homicides by victim gender and race/ethnicity")
fig.savefig("firearm-homicides-by-year-and-gender-and-race-big.png")
plt.clf()

import numpy as np
import seaborn as sns
import pandas as pd

frame = []
for year in sorted(years):
    row = []
    for age in sorted(ages):
        total_deaths = 0
        total_population = 0
        for gender in ["Male"]:
            for group in ["Black"]:
                total_deaths += data[year, age, gender, group]
                total_population += populations[year, age, gender, group]
        if total_population == 0:
            row.append(float("NaN"))
        else:
            row.append(100000 * total_deaths/total_population)
    frame.append(row)

fig, ax = plt.subplots(constrained_layout=True, figsize=(12,8))

df = pd.DataFrame(frame, index=sorted(years), columns=sorted(ages))

heatmap = sns.heatmap(df, xticklabels=True, yticklabels=True, ax=ax)
heatmap.set_title("Firearm homicide rate by age and year, black males")
heatmap.figure.savefig("firearm-homicide-rate-by-year-and-age-black-males-big.png" , dpi=180)
plt.clf()


fig, ax = plt.subplots(constrained_layout=True)
for target_ages in reversed([
        (0, 12),13,14,15,16,17,18,(19,22)]):

    if type(target_ages) == type(42):
        min_age = max_age = target_ages
        label = target_ages
    else:
        min_age, max_age = target_ages
        label = "%s-%s" % (min_age, max_age)

    xs = []
    ys = []
    for year in sorted(years):
        total_deaths = 0
        total_people = 0
        for age in range(min_age, max_age+1):
            for gender in genders:
                for group in groups:
                    total_deaths += data[year, age, gender, group]
                    total_people += populations[year, age, gender, group]
        if total_people:
            xs.append(year)
            ys.append(100000 * total_deaths/total_people)
            
    ax.plot(xs, ys, label=label)

ax.legend()
ax.set_ylabel("firearm homicides per 100k")
ax.set_xlabel("age")
ax.set_title("Youth firearm homicides by age, 1999-2020")
fig.savefig("youth-firearm-homicides-by-age-big.png")
plt.clf()


fig, ax = plt.subplots(constrained_layout=True)
for target_ages in reversed([
        (0, 12),13,14,15,16,17,18,(19,22)]):

    if type(target_ages) == type(42):
        min_age = max_age = target_ages
        label = target_ages
    else:
        min_age, max_age = target_ages
        label = "%s-%s" % (min_age, max_age)

    xs = []
    ys = []
    for year in sorted(years):
        total_deaths = 0
        total_people = 0
        for age in range(min_age, max_age+1):
            for gender in ["Male"]:
                for group in ["Black"]:
                    total_deaths += data[year, age, gender, group]
                    total_people += populations[year, age, gender, group]
        if total_people:
            xs.append(year)
            ys.append(100000 * total_deaths/total_people)
            
    ax.plot(xs, ys, label=label)

ax.legend()
ax.set_ylabel("firearm homicides per 100k")
ax.set_xlabel("age")
ax.set_title("Youth firearm homicide rates by age, black male, 1999-2020")
fig.savefig("youth-firearm-homicides-by-age-black-male-big.png")
plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
for target_ages in reversed([
        (0, 12),13,14,15,16,17,18,(19,22)]):

    if type(target_ages) == type(42):
        min_age = max_age = target_ages
        label = target_ages
    else:
        min_age, max_age = target_ages
        label = "%s-%s" % (min_age, max_age)

    xs = []
    ys = []
    for year in sorted(years):
        total_deaths = 0
        total_people = 0
        for age in range(min_age, max_age+1):
            for gender in ["Male"]:
                for group in ["Hispanic"]:
                    total_deaths += data[year, age, gender, group]
                    total_people += populations[year, age, gender, group]
        if total_people:
            xs.append(year)
            ys.append(100000 * total_deaths/total_people)
            
    ax.plot(xs, ys, label=label)

ax.legend()
ax.set_ylabel("firearm homicides per 100k")
ax.set_xlabel("age")
ax.set_title("Youth firearm homicide rates by age, hispanic male, 1999-2020")
fig.savefig("youth-firearm-homicides-by-age-hispanic-male-big.png")
plt.clf()


fig, ax = plt.subplots(constrained_layout=True)
for target_ages in reversed([
        (0, 12),13,14,15,16,17,18,(19,22)]):

    if type(target_ages) == type(42):
        min_age = max_age = target_ages
        label = target_ages
    else:
        min_age, max_age = target_ages
        label = "%s-%s" % (min_age, max_age)

    xs = []
    ys = []
    for year in sorted(years):
        total_deaths = 0
        total_people = 0
        for age in range(min_age, max_age+1):
            for gender in genders:
                for group in groups:
                    if gender == "Male" and group == "Black": continue
                    if gender == "Male" and group == "Hispanic": continue

                    
                    total_deaths += data[year, age, gender, group]
                    total_people += populations[year, age, gender, group]
        if total_people:
            xs.append(year)
            ys.append(100000 * total_deaths/total_people)
            
    ax.plot(xs, ys, label=label)

ax.legend()
ax.set_ylabel("firearm homicides per 100k")
ax.set_xlabel("age")
ax.set_title("Youth firearm homicide rates by age, others, 1999-2020")
fig.savefig("youth-firearm-homicides-by-age-others-big.png")
plt.clf()


fig, ax = plt.subplots(constrained_layout=True)
for gender_groups in [
        ["Male", "Black"], 
        ["Male", "Hispanic"],
        ["Female", "Black"],
        ["Male", "White"],
        ["Female", "White"],
        ["Female", "Hispanic"],
        [["Male", "Other"],
         ["Female", "Other"]]]:

    if type(gender_groups[0]) != type([]):
        gender_groups = [gender_groups]

    xs = []
    ys = []
    for age in sorted(ages):
        total_deaths = 0
        total_people = 0
        for year in sorted(years):
            for gender, group in gender_groups:
                total_deaths += data[year, age, gender, group]
                total_people += populations[year, age, gender, group]
        if total_people:
            xs.append(age)
            ys.append(100000 * total_deaths/total_people)

    print(gender_groups, xs, ys)
            
    if len(gender_groups) > 1:
        label ="Other"
    else:
        (gender, group), = gender_groups
        label = group + " " + gender;
            
    ax.plot(xs, ys, label=label)

ax.legend()
ax.set_ylabel("firearm homicides per 100k")
ax.set_xlabel("age")
ax.set_title("Firearm homicide rate by age, race, and gender 1999-2020")
fig.savefig("firearm-homicide-rate-by-age-and-race-and-gender-big.png", dpi=180)
plt.clf()


fig, ax = plt.subplots(constrained_layout=True)
xs = []
ys = []
for age in sorted(ages):
    total_deaths = 0
    total_people = 0
    for gender in sorted(genders):
        for year in sorted(years):
            for group in sorted(groups):
                total_deaths += data[year, age, gender, group]
                total_people += populations[year, age, gender, group]
    if total_people:
        xs.append(age)
        ys.append(100000 * total_deaths/total_people)
            
ax.plot(xs, ys)

ax.set_ylabel("firearm homicides per 100k")
ax.set_xlabel("age")
ax.set_title("Firearm homicide rate by age 1999-2020")
fig.savefig("firearm-homicide-rate-by-age-big.png", dpi=180)
plt.clf()


fig, ax = plt.subplots(constrained_layout=True)
xs = []
ys = []
for age in sorted(ages):
    total_deaths = 0
    total_ac_deaths = 0
    for gender in sorted(genders):
        for year in sorted(years):
            for group in sorted(groups):
                total_deaths += data[year, age, gender, group]
                total_ac_deaths += all_cause_deaths[year, age, gender, group]
    if total_ac_deaths:
        xs.append(age)
        ys.append(100*total_deaths/total_ac_deaths)
            
ax.plot(xs, ys)

ax.set_ylabel("firearm homicides as a fraction of deaths")
ax.set_xlabel("age")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_title("Firearm homicide death fraction age 1999-2020")
fig.savefig("firearm-homicide-death-fraction-by-age-big.png", dpi=180)
plt.clf()


for age in sorted(ages):
    total_deaths = 0
    for year in sorted(years):
        for gender in genders:
            for group in groups:
                total_deaths += data[year, age, gender, group]
    print (age, total_deaths)

    
fig, ax = plt.subplots(constrained_layout=True)
for gender_groups in [
        ["Male", "Black"], 
        ["Male", "Hispanic"],
        ["Female", "Black"],
        ["Male", "White"],
        ["Female", "White"],
        ["Female", "Hispanic"],
        [["Male", "Other"],
         ["Female", "Other"]]]:

    if type(gender_groups[0]) != type([]):
        gender_groups = [gender_groups]

    xs = []
    ys = []
    for age in sorted(ages):
        total_deaths = 0
        total_ac_deaths = 0
        for year in sorted(years):
            for gender, group in gender_groups:
                total_deaths += data[year, age, gender, group]
                total_ac_deaths += all_cause_deaths[year, age, gender, group]
        if total_ac_deaths:
            xs.append(age)
            ys.append(100*total_deaths/total_ac_deaths)

    if len(gender_groups) > 1:
        label ="Other"
    else:
        (gender, group), = gender_groups
        label = group + " " + gender;
            
    ax.plot(xs, ys, label=label)

ax.legend()
ax.set_ylabel("firearm homicides as a fraction of deaths")
ax.set_xlabel("age")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_title("Firearm homicide death fraction by age, race, and gender 1999-2020")
fig.savefig("firearm-homicide-death-fraction-rate-by-age-and-race-and-gender-big.png", dpi=180)
plt.clf()


