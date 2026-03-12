"""
Medical Records Lookup — single-file FastHTML + SQLModel + Datastar prototype.

Run:  python medical_records.py
Opens a browser automatically at http://localhost:8000
"""

import csv
import io
import webbrowser
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

from fasthtml.common import *
from sqlmodel import Field, Session, SQLModel, create_engine, select
from starlette.responses import StreamingResponse

from datastar_py.sse import SSE_HEADERS, ServerSentEventGenerator as SSE

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DB_FILE = "medical_records.db"
engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)


class MedicalRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mrn: str = Field(index=True)          # medical record number
    name: str = Field(index=True)
    encounter_date: date


def seed_db():
    """Insert sample rows if the table is empty."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        if s.exec(select(MedicalRecord)).first():
            return
        samples = [
            ("MRN-1001", "Alice Johnson",  date(2025, 3, 10)),
            ("MRN-1001", "Alice Johnson",  date(2025, 6, 15)),
            ("MRN-1002", "Bob Smith",      date(2025, 1, 22)),
            ("MRN-1003", "Carol Davis",    date(2025, 4, 5)),
            ("MRN-1003", "Carol Davis",    date(2025, 7, 18)),
            ("MRN-1003", "Carol Davis",    date(2025, 11, 1)),
            ("MRN-1004", "David Lee",      date(2025, 2, 14)),
            ("MRN-1005", "Eva Martinez",   date(2025, 5, 30)),
            ("MRN-1005", "Eva Martinez",   date(2025, 8, 22)),
            ("MRN-1006", "Frank Wilson",   date(2025, 9, 11)),
            ("MRN-1007", "Grace Kim",      date(2025, 10, 3)),
            ("MRN-1008", "Henry Brown",    date(2025, 12, 25)),
        ]
        for mrn, name, d in samples:
            s.add(MedicalRecord(mrn=mrn, name=name, encounter_date=d))
        s.commit()


# ---------------------------------------------------------------------------
# FastHTML app
# ---------------------------------------------------------------------------

DATASTAR_CDN = "https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.7/bundles/datastar.js"


@asynccontextmanager
async def lifespan(app):
    seed_db()
    yield

app = FastHTML(
    hdrs=(
        Script(src=DATASTAR_CDN, type="module"),
        # Tailwind + DaisyUI via CDN
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@5/themes.css"),
        Script(src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"),
        Script(src="https://cdn.jsdelivr.net/npm/daisyui@5"),
    ),
    lifespan=lifespan,
    htmlkw={"data-theme": "light"},
    htmx=False,
    surreal=False,
)


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

@app.get("/")
async def home():
    return Html(
        data_theme="light",
    )(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Title("Medical Records Lookup"),
        ),
        Body(cls="min-h-screen bg-base-200")(
            Div(
                cls="container mx-auto p-6 max-w-5xl",
                data_signals='{mrn:"", name:"", encounterDate:"", filterText:"", selectedRows:{}}',
            )(
                # Title
                H1("Medical Records Lookup", cls="text-3xl font-bold mb-6"),

                # --- Search card ---
                Div(cls="card bg-base-100 shadow mb-6")(
                    Div(cls="card-body")(
                        H2("Search", cls="card-title"),
                        Div(cls="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2")(
                            Label(cls="form-control")(
                                Div(cls="label")(Span("MRN", cls="label-text")),
                                Input(type="text", placeholder="e.g. MRN-1001",
                                      cls="input input-bordered w-full",
                                      data_bind="mrn"),
                            ),
                            Label(cls="form-control")(
                                Div(cls="label")(Span("Patient Name", cls="label-text")),
                                Input(type="text", placeholder="e.g. Alice",
                                      cls="input input-bordered w-full",
                                      data_bind="name"),
                            ),
                            Label(cls="form-control")(
                                Div(cls="label")(Span("Encounter Date", cls="label-text")),
                                Input(type="date",
                                      cls="input input-bordered w-full",
                                      data_bind="encounterDate"),
                            ),
                        ),
                        Div(cls="card-actions mt-4")(
                            Button("Search", cls="btn btn-primary",
                                   data_on_click="@get('/search')"),
                            Button("Clear", cls="btn btn-ghost",
                                   data_on_click="$mrn=''; $name=''; $encounterDate=''; $filterText=''; $selectedRows={}"),
                        ),
                    ),
                ),

                # --- CSV Upload card ---
                Div(cls="card bg-base-100 shadow mb-6")(
                    Div(cls="card-body")(
                        H2("Bulk Lookup via CSV", cls="card-title"),
                        P(cls="text-sm opacity-70")(
                            "Upload a CSV with columns: ",
                            Code("mrn", cls="badge badge-outline badge-sm"), " ",
                            Code("name", cls="badge badge-outline badge-sm"), " ",
                            Code("date", cls="badge badge-outline badge-sm"),
                            " (any subset).",
                        ),
                        Form(
                            cls="flex flex-wrap items-end gap-4 mt-3",
                            enctype="multipart/form-data",
                            data_on_submit="evt.preventDefault(); @post('/upload-csv')",
                        )(
                            Input(type="file", name="csv_file", accept=".csv",
                                  cls="file-input file-input-bordered file-input-sm"),
                            Button("Upload & Search", type="submit",
                                   cls="btn btn-secondary btn-sm"),
                        ),
                    ),
                ),

                # --- Results card ---
                Div(cls="card bg-base-100 shadow mb-6")(
                    Div(cls="card-body")(
                        Div(cls="flex flex-wrap justify-between items-center gap-4")(
                            H2("Results", cls="card-title"),
                            Input(type="search", placeholder="Filter results...",
                                  cls="input input-bordered input-sm w-60",
                                  data_bind="filterText",
                                  data_on_input__debounce_300ms="@get('/filter')"),
                        ),
                        Div(id="status", cls="text-sm opacity-60 mt-2")(
                            "Enter search criteria above and click Search."
                        ),
                        Div(id="results-table", cls="mt-4"),
                    ),
                ),

                # --- Actions ---
                Div(cls="flex gap-2", id="action-bar")(
                    Button("Show Selected", cls="btn btn-outline btn-sm",
                           data_on_click="alert('Selected IDs: ' + Object.keys($selectedRows).filter(k => $selectedRows[k]).join(', '))"),
                ),
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def query_records(mrn: str = "", name: str = "", encounter_date: str = "") -> list[MedicalRecord]:
    with Session(engine) as s:
        stmt = select(MedicalRecord)
        if mrn:
            stmt = stmt.where(MedicalRecord.mrn.ilike(f"%{mrn}%"))
        if name:
            stmt = stmt.where(MedicalRecord.name.ilike(f"%{name}%"))
        if encounter_date:
            try:
                d = date.fromisoformat(encounter_date)
                stmt = stmt.where(MedicalRecord.encounter_date == d)
            except ValueError:
                pass
        stmt = stmt.order_by(MedicalRecord.mrn, MedicalRecord.encounter_date)
        return list(s.exec(stmt).all())


def records_to_html_table(records: list[MedicalRecord], filter_text: str = "") -> str:
    """Build an HTML table string with DaisyUI styling and datastar click-to-select rows."""
    if filter_text:
        ft = filter_text.lower()
        records = [r for r in records if
                   ft in r.mrn.lower() or
                   ft in r.name.lower() or
                   ft in str(r.encounter_date)]

    if not records:
        return '<div id="results-table" class="mt-4"><p class="text-sm opacity-60">No records found.</p></div>'

    rows = ""
    for r in records:
        rid = str(r.id)
        rows += (
            f'<tr id="row-{rid}" class="hover cursor-pointer" '
            f'data-on-click="$selectedRows[{rid}] = !$selectedRows[{rid}]" '
            f'data-class-bg-primary="$selectedRows[{rid}]" '
            f'data-class-text-primary-content="$selectedRows[{rid}]">'
            f'<td><input type="checkbox" class="checkbox checkbox-sm" '
            f'data-bind="$selectedRows[{rid}]" /></td>'
            f'<td>{r.mrn}</td>'
            f'<td>{r.name}</td>'
            f'<td>{r.encounter_date}</td>'
            f'</tr>'
        )

    return (
        f'<div id="results-table" class="mt-4">'
        f'<div class="overflow-x-auto">'
        f'<table class="table table-zebra">'
        f'<thead><tr><th></th><th>MRN</th><th>Name</th><th>Date</th></tr></thead>'
        f'<tbody>{rows}</tbody>'
        f'</table>'
        f'</div>'
        f'<div class="mt-2 text-sm opacity-60">{len(records)} record(s)</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# API endpoints (return datastar SSE)
# ---------------------------------------------------------------------------

@app.get("/search")
async def search(request):
    from datastar_py.starlette import read_signals
    signals = await read_signals(request) or {}
    mrn = signals.get("mrn", "")
    name = signals.get("name", "")
    encounter_date = signals.get("encounterDate", "")

    records = query_records(mrn, name, encounter_date)
    table_html = records_to_html_table(records)
    status_html = f'<div id="status" class="text-sm opacity-60 mt-2">Found {len(records)} record(s).</div>'

    async def generate():
        yield SSE.patch_elements(table_html)
        yield SSE.patch_elements(status_html)

    return StreamingResponse(generate(), headers=SSE_HEADERS)


@app.get("/filter")
async def filter_results(request):
    from datastar_py.starlette import read_signals
    signals = await read_signals(request) or {}
    mrn = signals.get("mrn", "")
    name = signals.get("name", "")
    encounter_date = signals.get("encounterDate", "")
    filter_text = signals.get("filterText", "")

    records = query_records(mrn, name, encounter_date)
    table_html = records_to_html_table(records, filter_text)

    filtered_count = len([r for r in records if not filter_text or
                          filter_text.lower() in r.mrn.lower() or
                          filter_text.lower() in r.name.lower() or
                          filter_text.lower() in str(r.encounter_date)])

    status_html = f'<div id="status" class="text-sm opacity-60 mt-2">Showing {filtered_count} of {len(records)} record(s).</div>'

    async def generate():
        yield SSE.patch_elements(table_html)
        yield SSE.patch_elements(status_html)

    return StreamingResponse(generate(), headers=SSE_HEADERS)


@app.post("/upload-csv")
async def upload_csv(request):
    form = await request.form()
    csv_file = form.get("csv_file")

    if not csv_file or not csv_file.filename:
        async def err():
            yield SSE.patch_elements('<div id="status" class="text-sm text-error mt-2">No file uploaded.</div>')
            yield SSE.patch_elements('<div id="results-table" class="mt-4"></div>')
        return StreamingResponse(err(), headers=SSE_HEADERS)

    content = (await csv_file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    all_records: list[MedicalRecord] = []
    for row in reader:
        row_lower = {k.strip().lower(): v.strip() for k, v in row.items()}
        mrn = row_lower.get("mrn", "")
        name = row_lower.get("name", "")
        d = row_lower.get("date", "") or row_lower.get("encounter_date", "")
        results = query_records(mrn, name, d)
        all_records.extend(results)

    # deduplicate by id
    seen = set()
    unique = []
    for r in all_records:
        if r.id not in seen:
            seen.add(r.id)
            unique.append(r)

    table_html = records_to_html_table(unique)
    status_html = f'<div id="status" class="text-sm opacity-60 mt-2">CSV lookup returned {len(unique)} record(s).</div>'

    async def generate():
        yield SSE.patch_elements(table_html)
        yield SSE.patch_elements(status_html)

    return StreamingResponse(generate(), headers=SSE_HEADERS)


# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import threading, time

    def open_browser():
        time.sleep(1)
        webbrowser.open("http://localhost:8000")

    threading.Thread(target=open_browser, daemon=True).start()
    serve(port=8000)
