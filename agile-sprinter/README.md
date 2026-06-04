# Agile Sprint Tracker — Excel + VBA

**Tools:** Microsoft Excel, VBA Macros  
**Domain:** Project Management / Agile / Scrum  
**Author:** Varshini Gayathri Suresh

---

## Overview

A fully functional Agile Sprint Tracker built in Excel for a simulated CRM Modernisation project. Designed for Scrum teams to manage backlog, track sprint progress, monitor velocity, and run retrospectives — all within a single workbook. Includes 4 VBA macros to automate repetitive PMO tasks.

---

## Workbook Structure

| Sheet | Purpose |
|---|---|
| **Sprint Dashboard** | Live sprint board with KPI cards, story status, % progress bars |
| **Backlog** | Full product backlog with MoSCoW prioritisation and data validation dropdowns |
| **Burndown Data** | Sprint 4 burndown chart data (ideal vs actual remaining points) |
| **Velocity Tracker** | Sprint-over-sprint velocity comparison with averages |
| **Retrospective Log** | Structured retro notes — went well, didn't go well, action items |
| **VBA Macros** | 4 automation macros with step-by-step instructions |

---

## Key Features

**Sprint Dashboard**
- KPI cards: stories done, in progress, blocked, velocity, team happiness
- Colour-coded status (Done / In Progress / Blocked / To Do) and priority (Critical / High / Medium / Low)
- Data bar progress indicators on completion % column
- Live formula counters pulling from Backlog sheet

**Product Backlog**
- 25 user stories across 5 sprints
- MoSCoW prioritisation (Must / Should / Could / Won't)
- Dropdown data validation on Status and Priority columns — no free-text errors
- Acceptance criteria and Definition of Done per story

**Velocity Tracker**
- Committed vs completed points per sprint
- Velocity % formula
- Average velocity calculated automatically

**VBA Macros (save as .xlsm to enable)**

| Macro | What it does |
|---|---|
| `UpdateStatusColours` | Auto-applies RAG colours to all status cells |
| `ArchiveDoneStories` | Moves completed stories to an Archive sheet |
| `GenerateSprintSummary` | Pops up a sprint completion summary report |
| `HighlightOverdue` | Flags stories past end date and not yet done |

---

## How to Use

1. Download `Agile_Sprint_Tracker.xlsx`
2. Open in Microsoft Excel (2016 or later)
3. To enable macros: **File → Save As → Excel Macro-Enabled Workbook (.xlsm)**
4. Open VBA Editor: **Alt + F11 → Insert → Module → paste macro code from the VBA sheet**
5. Add buttons to the dashboard: **Developer tab → Insert → Button → assign macro**

---

## Skills Demonstrated

- Advanced Excel formatting and conditional formatting
- Cross-sheet formula referencing
- Data validation (dropdown lists)
- VBA macro development for PMO automation
- Agile/Scrum methodology (backlog management, sprint tracking, retrospectives, velocity)
- Stakeholder-ready dashboard design
