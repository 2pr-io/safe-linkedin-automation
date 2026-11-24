# Safe LinkedIn Automation

**How to automate LinkedIn without risking your account.**

## TL;DR

- LinkedIn has to give you a full copy of your own data: every connection, every message, every invite. It is free and it is a built-in feature.
- This free, open-source Claude skill **downloads that archive for you about every 2 days, at a random time** (two clicks in your own browser, nothing else), then **shows you what to do with it**:
  - who you owe a reply, and which new connections never heard from you;
  - a CRM-ready spreadsheet of your whole network, with message history and a status for every person;
  - how to enrich it (role, fit, company), and where the line is.
- No bot ever sends an invite, a message, a like or a comment for you. Everything is read on your machine. Nothing is uploaded.

On our founder's account, the first run found **42 people waiting on a reply**, **16 messages never answered** and **291 of 434 new connections who never heard from him**. Across all 9,895 connections, **6,219 had never exchanged a single message** with him.

## Why: your network is an asset you are not using

Most people treat LinkedIn connections as a number. But the people are the value: past colleagues, customers, investors, people who reached out once and never heard back.

LinkedIn does not help you keep track. The inbox mixes friends with pitches, there is no "who did I forget" view, and once you pass a few hundred connections you lose the thread. So people reach for automation tools, and that is where accounts get hurt. In a poll we ran, most people valued their LinkedIn access at **$100k+**. That is a lot to bet on a Chrome extension.

The goal of this skill is simple: **know your network and act on it, without putting your account at risk.**

## What is OK and what is not

The line LinkedIn cares about is not "tools vs no tools". It is whether software **acts as you inside LinkedIn**, or **works around it** with official features and a human doing the actual talking.

**Avoid: software acting as you**

- Auto-connect and auto-DM sequences that send invites and messages for you.
- Extensions that auto-like or auto-comment on posts.
- Engagement pods that trade likes and comments on a schedule.
- Scrapers that crawl profiles through your logged-in account.
- Any service that asks for your LinkedIn password or session cookie.

These are what get reach limited and accounts restricted. LinkedIn's own product leaders have called out pods and automated comments publicly.

**Fine: official features and tools**

- Downloading your own data (the export this skill uses). It exists because privacy law (GDPR) gives you the right to it.
- Scheduling posts with LinkedIn's scheduler or a tool on LinkedIn's official API. LinkedIn's Sr. Director of Product Management, Rishi Jobanputra, has said publicly that scheduling and posting from third-party tools do not hurt reach.
- AI that drafts posts or replies that you read, edit and send yourself.
- Native features: following people with the bell, saved searches, Sales Navigator alerts, exporting your post analytics.
- Anything you do with your data *after* it leaves LinkedIn: spreadsheets, a CRM, AI analysis.

**Low risk, and why: this skill's export step**

The export step is technically browser automation: Claude in Chrome clicks for you. We keep it as close to a person as possible: two buttons, on a settings page, about once every two days at a random hour (every 44 to 52 hours, never on a fixed clock), in your own browser, with your own login. It never types into LinkedIn, never visits profiles, never touches your inbox, and stops the moment LinkedIn asks for a password, a code or a captcha. If you would rather not automate even that, the skill gives you the same steps to do by hand.

## What to do with your export

The skill walks you through three first steps.

**1. The report: who is waiting on you**

```text
# LinkedIn network report, last 30 days

- 42 people you talked to before are waiting on your reply
- 16 people wrote to you and never got an answer
- 291 of 434 new connections have never heard from you
- 33 conversations ended on a "thanks" or an emoji, so they are left out

## Owe a reply (warm) (42)
- 2026-11-14 **A. Person** https://www.linkedin.com/in/...
  > At what stage are you? :)
...
```

- **Owe a reply (warm):** they wrote last and you had talked before. Open questions come first. Start here.
- **Owe a reply (cold inbound):** people who wrote and never got an answer. Mostly pitches, but scan them.
- **New connections you never talked to:** one line within a week (not a pitch) goes a long way.

Claude can draft short replies for the warm list. You send them yourself.

**2. Your network as a CRM**

One row per connection: name, LinkedIn URL, email (when the person shares it), company, position, seniority, date connected, number of messages, last message date, who wrote last, and a status:

| status | meaning |
| --- | --- |
| you owe a reply | they wrote last, and it was more than a "thanks" |
| waiting on them | you wrote last |
| closed | they wrote last with a "thanks" or an emoji |
| never talked | no message either way |

On our founder's 9,895 connections: 1,036 "you owe a reply", 2,231 "waiting on them", 409 "closed", 6,219 "never talked". Only 364 (under 4%) shared an email.

Import it into HubSpot, Attio, Pipedrive, Notion or Google Sheets. Use the LinkedIn URL as the unique key, so every new export updates people instead of duplicating them.

**3. Enrich it, carefully**

- **Role and fit:** Claude tags each person's function (sales, marketing, product...) and, if you describe your ideal customer, whether they fit.
- **Company:** add the company website for the people who matter; most CRMs fill in size and industry from there.
- **Emails:** only a few percent share one. Lookup tools exist (Apollo, Hunter, Clay), but use them only for people you already have a relationship with, follow privacy law where you and they live, and never email your whole network.

Never enrich by visiting or scraping LinkedIn profiles. Everything starts from the archive.

## How to set it up

**1. Install the skill**

*Claude Code:*

```text
/plugin marketplace add 2pr-io/safe-linkedin-automation
/plugin install safe-linkedin-automation@2pr-io
```

*Claude desktop or claude.ai:* download `linkedin-network-brain.zip` from the [latest release](https://github.com/2pr-io/safe-linkedin-automation/releases/latest) and upload it under Settings > Capabilities > Skills.

**2. Ask Claude to set up the export**

Say *"Set up my LinkedIn data export"*. Claude creates a scheduled task that checks every 2 hours and exports when the next random 44 to 52 hour slot comes up, so most checks stop right away. You need [Claude in Chrome](https://claude.com/chrome), signed in to your LinkedIn. Pick the full archive: the report and the CRM need your message history. The first archive arrives by email in about a day.

**3. Use it**

Once you have an archive, ask *"Who do I owe a reply on LinkedIn?"* or *"Turn my LinkedIn connections into a CRM"*.

**Or run the scripts yourself** (Python 3, standard library only):

```bash
python3 skills/linkedin-network-brain/scripts/network_report.py ~/Downloads/linkedin-archives/
python3 skills/linkedin-network-brain/scripts/crm_export.py ~/Downloads/linkedin-archives/ --out linkedin-crm.csv
```

Both accept an archive zip, an unzipped archive folder, or a folder of zips (they pick the newest). Report options: `--days 30`, `--limit 25`, `--out report.md`.

## Staying visible to your whole network

A reply fixes one relationship. Posting regularly keeps the rest of your network warm, including the people you have never spoken to. [2pr.io](https://2pr.io) writes LinkedIn posts in your own voice and publishes them through LinkedIn's official API, so there is no automation risk there either. [Start a free trial](https://2pr.io/app/login).

## License

MIT
