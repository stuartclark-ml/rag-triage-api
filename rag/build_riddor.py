import re
import fitz

NOISE_LINES = {
    "Document Generated: 2026-04-09",
    "Status:  This is the original version (as it was originally made).",
}

REG_PATTERN = re.compile(r"^\d{1,2}\.[\s\—]")

def extract_regulations(pdf_path: str, start_page: int, end_page: int) -> list[dict]:
    doc = fitz.open(pdf_path)

    raw_lines = []
    for page_num in range(start_page, end_page + 1):
        page_text = doc[page_num].get_text()
        for line in page_text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped in NOISE_LINES:
                continue
            if re.match(r"^\d+$", stripped):
                continue
            raw_lines.append(stripped)

    regulations = []
    current_number = None
    current_title = None
    current_lines = []
    prev_line = None

    for line in raw_lines:
        if REG_PATTERN.match(line):
            if current_number is not None:
                regulations.append({
                    "number": current_number,
                    "title": current_title,
                    "text": " ".join(current_lines).strip(),
                })
            number_match = re.match(r"^(\d{1,2})\.", line)
            current_number = number_match.group(1) if number_match else None
            current_title = prev_line if prev_line else ""
            current_lines = [line]
        else:
            if current_number is not None:
                current_lines.append(line)
        prev_line = line

    if current_number is not None:
        regulations.append({
            "number": current_number,
            "title": current_title,
            "text": " ".join(current_lines).strip(),
        })

    return regulations

REG_METADATA: dict[str, dict[str, str | None]] = {
    "3":  {"title": "Responsible person",
            "deadline": None, "route": None},
    "4a": {"title": "Non-fatal injuries to workers — specified injuries",
            "deadline": "Notify without delay, then report within 10 days", "route": "HSE"},
    "4b": {"title": "Non-fatal injuries to workers — over-seven-day incapacitation",
            "deadline": "Report as soon as practicable, within 15 days of incident", "route": "HSE"},
    "5":  {"title": "Non-fatal injuries to non-workers",
            "deadline": "Notify without delay, then report within 10 days", "route": "HSE"},
    "6":  {"title": "Work-related fatalities",
            "deadline": "Without delay", "route": "HSE"},
    "7":  {"title": "Dangerous occurrences",
            "deadline": "Notify without delay, then report within 10 days", "route": "HSE"},
    "8":  {"title": "Occupational diseases",
            "deadline": "Without delay", "route": "HSE"},
    "9":  {"title": "Exposure to carcinogens, mutagens and biological agents",
            "deadline": "Without delay", "route": "HSE"},
    "10": {"title": "Diseases offshore",
            "deadline": "Without delay", "route": "HSE"},
    "11a": {"title": "Gas-related injuries — death, unconsciousness or hospitalisation",
             "deadline": "Without delay", "route": "HSE"},
    "11b": {"title": "Gas installation faults",
             "deadline": "14 days", "route": "HSE"},
    "12": {"title": "Recording and record-keeping",
            "deadline": None, "route": None},
    "13": {"title": "Mines, quarries and offshore site disturbance",
            "deadline": None, "route": None},
    "14": {"title": "Restrictions on the application of regulations 4 to 10",
            "deadline": None, "route": None},
    "15": {"title": "Restriction on parallel requirements",
            "deadline": None, "route": None},
    "16": {"title": "Defence",
            "deadline": None, "route": None},
    "17": {"title": "Certificates of exemption",
            "deadline": None, "route": None},
    "18": {"title": "Revocations, amendments and savings",
            "deadline": None, "route": None},
    "19": {"title": "Extension outside Great Britain",
            "deadline": None, "route": None},
    "20": {"title": "Review",
            "deadline": None, "route": None},
}

SKIP_REGULATIONS = {"1", "2"}

REG4_SPLIT_PHRASE = "Where any person at work is incapacitated for routine work for more than seven consecutive"
REG11_SPLIT_PHRASE = "Where an approved person has sufficient information to decide"


def build_chunks(regulations: list[dict]) -> list[dict]:
    chunks = []

    for reg in regulations:
        number = reg["number"]

        if number in SKIP_REGULATIONS:
            continue

        if number == "4":
            split_index = reg["text"].find(REG4_SPLIT_PHRASE)
            if split_index == -1:
                raise ValueError("Could not find split phrase in Regulation 4 text")
            text_4a = reg["text"][:split_index].strip()
            text_4b = reg["text"][split_index:].strip()
            for key, text in [("4a", text_4a), ("4b", text_4b)]:
                meta = REG_METADATA[key]
                chunks.append({
                    "chunk_id": f"reg_{key}",
                    "chunk_type": "regulation",
                    "regulation_number": key,
                    "title": meta["title"],
                    "reporting_deadline": meta["deadline"],
                    "reporting_route": meta["route"],
                    "text": text,
                })
            continue

        if number == "11":
            split_index = reg["text"].find(REG11_SPLIT_PHRASE)
            if split_index == -1:
                raise ValueError("Could not find split phrase in Regulation 11 text")
            text_11a = reg["text"][:split_index].strip()
            text_11b = reg["text"][split_index:].strip()
            for key, text in [("11a", text_11a), ("11b", text_11b)]:
                meta = REG_METADATA[key]
                chunks.append({
                    "chunk_id": f"reg_{key}",
                    "chunk_type": "regulation",
                    "regulation_number": key,
                    "title": meta["title"],
                    "reporting_deadline": meta["deadline"],
                    "reporting_route": meta["route"],
                    "text": text,
                })
            continue

        meta: dict[str, str | None] | None = REG_METADATA.get(number)
        if meta is None:
            continue

        chunks.append({
            "chunk_id": f"reg_{number}",
            "chunk_type": "regulation",
            "regulation_number": number,
            "title": meta["title"],
            "reporting_deadline": meta["deadline"],
            "reporting_route": meta["route"],
            "text": reg["text"],
        })

    return chunks

RETAINED_SCHEDULE2 = {1, 2, 3, 4, 10, 11, 12, 18, 20, 21, 22}

OMITTED_SCHEDULE2_NOTE = (
    "Schedule 2 dangerous occurrence categories relating to explosives "
    "manufacture and storage (categories 5-9), diving operations "
    "(categories 13-17), and train collisions (category 19) have been "
    "excluded as outside the scope of health and social care settings."
)

SCHEDULE2_TITLE_OVERRIDES = {
    22: "Pipelines — unintentional change in position",
}

def build_schedule_chunks(categories: list[dict]) -> list[dict]:
    chunks = []

    for cat in categories:
        number = int(cat["number"])

        if number not in RETAINED_SCHEDULE2:
            continue

        chunks.append({
            "chunk_id": f"sch2_{number}",
            "chunk_type": "schedule",
            "schedule_number": "2",
            "category_number": str(number),
            "title": SCHEDULE2_TITLE_OVERRIDES.get(number, cat["title"]),
            "parent_regulation": "7",
            "reporting_deadline": "Notify without delay, then report within 10 days",
            "reporting_route": "HSE",
            "omission_note": OMITTED_SCHEDULE2_NOTE,
            "text": cat["text"],
        })

    return chunks