#!/bin/bash
# Analyze remaining unmerged branches to categorize for manual review

echo "=== UNMERGED BRANCHES ANALYSIS ==="
echo ""

total=$(git branch -r --no-merged main | grep -v HEAD | wc -l)
echo "Total unmerged: $total"
echo ""

echo "By prefix/category:"
git branch -r --no-merged main | grep -v HEAD | sed 's|origin/||' | cut -d'/' -f1 | sort | uniq -c | sort -rn

echo ""
echo "=== OLDER BRANCHES (likely stale) ==="
echo "Branches older than 90 days:"
git for-each-ref --sort=-committerdate refs/remotes/origin/ \
  --format='%(committerdate:short)|%(refname:short)' | \
  awk -F'|' '{
    cmd="date -d "$1" +%s";
    cmd | getline commit_time;
    close(cmd);
    "date +%s" | getline now;
    close("date +%s");
    age_days = int((now - commit_time) / 86400);
    if (age_days > 90 && $2 != "origin/main" && $2 !~ /HEAD/) print age_days " days: " $2
  }' | head -20

echo ""
echo "=== RECENT BRANCHES (potentially active) ==="
echo "Branches less than 30 days old:"
git for-each-ref --sort=-committerdate refs/remotes/origin/ \
  --format='%(committerdate:short)|%(refname:short)' | \
  awk -F'|' '{
    cmd="date -d "$1" +%s";
    cmd | getline commit_time;
    close(cmd);
    "date +%s" | getline now;
    close("date +%s");
    age_days = int((now - commit_time) / 86400);
    if (age_days < 30 && $2 != "origin/main" && $2 !~ /HEAD/) print age_days " days: " $2
  }' | head -20
