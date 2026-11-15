# 🏗️ Construction AI Toolkit

> AI-powered tools, prompts, templates, and automation resources for construction professionals.

## 📌 About the Project

Construction AI Toolkit is an open-source project designed to help engineers, project managers, planners, quantity surveyors, estimators, and contractors leverage Artificial Intelligence in their daily work.

The goal is to build one comprehensive library containing practical AI resources for the construction industry.

---

## 🎯 Project Objectives

- Improve engineering productivity.
- Automate repetitive tasks.
- Standardize engineering documentation.
- Provide high-quality templates.
- Share AI workflows for construction professionals.

---

## 📂 Planned Sections

- 🤖 AI Prompts
- 📅 Primavera P6
- 📊 Quantity Surveying
- 💰 BOQ & Estimation
- 📄 Contracts
- 📝 Method Statements
- ⚠️ Risk Management
- 📈 Project Controls
- 🏗️ BIM Resources
- 📋 Construction Checklists
- 📑 Tendering Documents
- 📂 Excel Templates

---

## 🚀 Project Status

**Currently under development.**

New resources will be added regularly.

---

## 📜 License

This project is released under the MIT License.

---

## Architecture

- [AI Engineering Agent Architecture](docs/architecture/AI-AGENT-ARCHITECTURE.md)

## Specialized Agents

- [Estimation Agent](agents/estimation-agent/README.md)
- [Planning & Primavera P6 Agent](agents/planning-p6-agent/README.md)
- [Tender Manager Agent](agents/tender-manager-agent/README.md)

## Local Scheduling Application

The integrated local application combines project and BOQ intake, WBS, calendars, activity logic, exact durations, Gantt charts, schedule exports, evidence-backed estimating and the repository's Codex Skills library.

Start with **Create synthetic demo / تجربة البرنامج** to create a separate example project. The demo contains synthetic arithmetic inputs, not market prices or project evidence. Your own estimates start with no resource rates.

The **Estimating** workspace supports material/labor/equipment/subcontract build-ups, source references, pricing dates, material waste, project allowances, markup or gross margin, discount and explicit tax. Incomplete items block the final selling price. The **Engineering workflows** workspace exposes the five existing repository skills and the original prompt library.

See [Integrated application and validation](docs/phase-8/INTEGRATED-APPLICATION.md) for the tested scope, calculation basis and current limits. Shared-calendar schedules include a CPM backward pass, working-hour float and critical activity identification. Multi-calendar schedules keep their forward dates and explicitly report that CPM is unavailable.

See [Scheduling MVP](apps/scheduling-mvp/README.md) for installation, launch, test instructions, and the current scope boundary.

On Windows, double-click `START_SCHEDULING_APP.bat` at the repository root. Keep its terminal open, and use `STOP_SCHEDULING_APP.bat` to stop only the managed local application. Python 3.12 is required.
