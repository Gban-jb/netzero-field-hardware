# netzero-field-hardware

**Student 4 — Field Hardware, Positioning & Connectivity**
Part of the [Net Zero Solar Portal](https://netzero-solar-portal.vercel.app)
at Alabama A&M University. Owner: @Armaaaaannnn.

The portal links here from the
[RF & Positioning workstream page](https://netzero-solar-portal.vercel.app/departments/engineering/students/student-4).

---

## Pushing your code

You already have write access, so you can push straight away:

```sh
git clone https://github.com/Gban-jb/netzero-field-hardware.git
cd netzero-field-hardware
# copy your dashboard and scripts in, then:
git add .
git commit -m "Add the field hardware dashboard"
git push
```

Set your git author first, or the commit will not be credited to you:

```sh
git config --global user.email "<id>+<username>@users.noreply.github.com"
git config --global user.name "Armaan Asim"
```

## What to include

- The dashboard entry point (for example `app.py`)
- `requirements.txt` — every package the code imports
- The GPS / RF measurement scripts and the CSV logger
- Sample recorded CSVs, so the dashboard runs without hardware attached

## Hosting the demo — read this first

The analysis side of this work can go live on
[share.streamlit.io](https://share.streamlit.io) for free: coverage maps,
heatmaps, and anything that reads a recorded CSV.

What cannot go live is anything that talks to hardware directly. A cloud
server has no serial port, no GPS receiver and no radio, so code that
opens a serial device or captures live RF will fail there. Split the two:
record to CSV on site, and let the hosted dashboard read those files.

That split is worth doing anyway — it is what makes the results
reproducible by someone who was not standing in the field.
