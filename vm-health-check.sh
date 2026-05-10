#!/usr/bin/env bash
# vm_health_check.sh
# Usage: ./vm_health_check.sh [explain]
# Returns exit code 0 if HEALTHY, 1 if UNHEALTHY.
# Threshold: 60% (any metric >= 60% is considered unhealthy).

set -uo pipefail

THRESHOLD=60
EXPLAIN=false

if [ "${1-}" = "explain" ] || [ "${1-}" = "--explain" ] || [ "${1-}" = "-e" ]; then
  EXPLAIN=true
fi

# Get CPU usage by sampling /proc/stat
get_cpu_usage() {
  # Read first sample
  read -r _ user1 nice1 system1 idle1 iowait1 irq1 softirq1 steal1 guest1 guest_nice1 < /proc/stat
  idle1=$((idle1 + iowait1))
  total1=$((user1 + nice1 + system1 + idle1 + irq1 + softirq1 + steal1 + guest1 + guest_nice1))

  sleep 0.5

  read -r _ user2 nice2 system2 idle2 iowait2 irq2 softirq2 steal2 guest2 guest_nice2 < /proc/stat
  idle2=$((idle2 + iowait2))
  total2=$((user2 + nice2 + system2 + idle2 + irq2 + softirq2 + steal2 + guest2 + guest_nice2))

  total_delta=$((total2 - total1))
  idle_delta=$((idle2 - idle1))

  if [ "$total_delta" -eq 0 ]; then
    echo "0.0"
    return
  fi

  # Calculate usage percentage
  usage=$(awk -v td="$total_delta" -v id="$idle_delta" 'BEGIN { printf "%.1f", 100 * (td - id) / td }')
  echo "$usage"
}

# Get memory usage percent using 'free' (uses available if present)
get_mem_usage() {
  # columns: total used free shared buff/cache available
  read -r _ total used free shared buff_available available < <(free -m | awk 'NR==2{print "mem",$2,$3,$4,$5,$6,$7}')
  if [ -z "$available" ] || [ "$available" = "0" ]; then
    # Fallback: compute used/total if available not present
    used_val=$used
    total_val=$total
  else
    used_val=$(( total - available ))
    total_val=$total
  fi
  if [ "$total_val" -eq 0 ]; then
    echo "0.0"
    return
  fi
  awk -v u="$used_val" -v t="$total_val" 'BEGIN { printf "%.1f", 100 * u / t }'
}

# Get root disk usage percent
get_disk_usage() {
  # Use POSIX df output for '/' mount
  pct=$(df -P / | awk 'NR==2 {gsub("%","",$5); print $5}')
  # If df didn't return a number, default to 0.0
  if ! printf "%s" "$pct" | grep -qE '^[0-9]+$'; then
    echo "0.0"
  else
    awk -v p="$pct" 'BEGIN { printf "%.1f", p }'
  fi
}

cpu_pct=$(get_cpu_usage)
mem_pct=$(get_mem_usage)
disk_pct=$(get_disk_usage)

# Determine health: UNHEALTHY if any metric is >= THRESHOLD, else HEALTHY
unhealthy_reasons=()

# Compare using awk to handle floating point
check_metric() {
  metric_val="$1"
  metric_name="$2"
  cmp=$(awk -v v="$metric_val" -v t="$THRESHOLD" 'BEGIN { print (v >= t) ? 1 : 0 }')
  if [ "$cmp" -eq 1 ]; then
    unhealthy_reasons+=("$metric_name ($metric_val%)")
  fi
}

check_metric "$cpu_pct" "CPU"
check_metric "$mem_pct" "Memory"
check_metric "$disk_pct" "Disk(/)"

if [ "${#unhealthy_reasons[@]}" -gt 0 ]; then
  echo "UNHEALTHY"
  if $EXPLAIN; then
    echo "Details:"
    printf "  CPU usage:    %s%%\n" "$cpu_pct"
    printf "  Memory usage: %s%%\n" "$mem_pct"
    printf "  Disk usage:   %s%%\n" "$disk_pct"
    echo "Reason(s):"
    for r in "${unhealthy_reasons[@]}"; do
      echo "  - $r is at/above threshold (${THRESHOLD}%)."
    done
  fi
  exit 1
else
  echo "HEALTHY"
  if $EXPLAIN; then
    echo "Details:"
    printf "  CPU usage:    %s%%\n" "$cpu_pct"
    printf "  Memory usage: %s%%\n" "$mem_pct"
    printf "  Disk usage:   %s%%\n" "$disk_pct"
    echo "All metrics are below the threshold (${THRESHOLD}%)."
  fi
  exit 0
fi
