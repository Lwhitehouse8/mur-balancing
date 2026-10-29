"""Turn a 'Reading:' issue into a new row in readings.csv.

Reads the issue body (GitHub issue form format) from $BODY and writes
ok=true/false and msg=... to $GITHUB_OUTPUT. Never executes issue content.
"""
import csv
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

MEL = ZoneInfo("Australia/Melbourne")
CSV_PATH = "readings.csv"
LABELS = {
    "time": "time",
    "cell voltage high (v)": "high",
    "cell voltage low (v)": "low",
    "average (v, optional)": "avg",
    "note (optional)": "note",
}


def output(ok, msg):
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        fh.write(f"ok={'true' if ok else 'false'}\n")
        fh.write("msg<<EOF_MSG\n" + msg + "\nEOF_MSG\n")
    print(msg)


def parse_body(body):
    fields = {}
    for block in re.split(r"^###\s+", body or "", flags=re.M)[1:]:
        label, _, value = block.partition("\n")
        key = LABELS.get(label.strip().lower())
        value = value.strip()
        if key and value != "_No response_":
            fields[key] = value
    return fields


def parse_time(text, fallback):
    text = (text or "").strip()
    for candidate in (text, text.replace(" ", "T", 1)):
        try:
            dt = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=MEL)
            return dt.astimezone(MEL)
        except ValueError:
            pass
    return datetime.fromisoformat(fallback.replace("Z", "+00:00")).astimezone(MEL)


def volts(text, name, required=True):
    text = (text or "").strip()
    if not text and not required:
        return None
    if not re.fullmatch(r"\d\.\d{1,4}", text):
        raise ValueError(f"{name} should look like 3.812, got '{text[:20]}'.")
    value = float(text)
    if not 2.5 <= value <= 4.25:
        raise ValueError(f"{name} should be between 2.5 and 4.25 V.")
    return value


def main():
    fields = parse_body(os.environ.get("BODY", ""))
    try:
        high = volts(fields.get("high"), "Cell voltage high")
        low = volts(fields.get("low"), "Cell voltage low")
        avg = volts(fields.get("avg"), "Average", required=False)
        if low > high:
            raise ValueError("Low cell voltage is higher than the high cell. Check they aren't swapped.")
    except ValueError as err:
        output(False, f"Couldn't add this reading: {err} Open a new one from the tracker page.")
        return
    when = parse_time(fields.get("time"), os.environ["CREATED"])
    note = re.sub(r"\s+", " ", fields.get("note", "")).strip()[:140]

    with open(CSV_PATH, newline="") as fh:
        rows = list(csv.reader(fh))
    header, body = rows[0], rows[1:]
    for row in body:
        try:
            same_time = abs((datetime.fromisoformat(row[0]) - when).total_seconds()) < 120
        except ValueError:
            continue
        if same_time and row[1] == f"{high:.3f}" and row[2] == f"{low:.3f}":
            output(False, "This reading is already in the log, so nothing was added.")
            return
    body.append([when.isoformat(timespec="minutes"), f"{high:.3f}", f"{low:.3f}",
                 "" if avg is None else f"{avg:.3f}", note])
    body.sort(key=lambda r: datetime.fromisoformat(r[0]))
    with open(CSV_PATH, "w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(body)
    output(True, f"Added {high:.3f} / {low:.3f} V at {when:%a %d %b %H:%M}. "
                 "It shows on the tracker within a minute or two.")


if __name__ == "__main__":
    main()
