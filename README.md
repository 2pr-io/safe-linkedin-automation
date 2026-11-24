# Safe LinkedIn Automation

**How to automate LinkedIn without risking your account.** A free, open-source Claude skill that keeps track of your LinkedIn network using only your own data export. No bot ever sends an invite, a message or a comment for you.

Most LinkedIn automation tools act *as you* inside LinkedIn: they send connection requests, DMs and comments from your logged-in session. That is what gets accounts restricted, and for most people their LinkedIn account is worth far more than the time those tools save.

This skill works *around* LinkedIn instead:

1. **Export.** Every 2 days, Claude in Chrome opens LinkedIn's own [Download your data](https://www.linkedin.com/mypreferences/d/download-my-data) page and clicks two buttons: download the ready archive, request the next one. It types nothing. If LinkedIn ever asks for a password, a code or a captcha, it stops and tells you.
2. **First steps with the export.** Small Python scripts read the archive on your machine. Nothing is uploaded anywhere.
   - a **report** of who you owe a reply and which new connections never heard from you;
   - a **CRM-ready CSV** of every connection with message history and a relationship status;
   - guided **enrichment**: function, ideal-customer fit, company domains, and when (not) to look up emails.

## What the report shows

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

Those are real numbers from the first run on our founder's account.

- **Owe a reply (warm):** the other person wrote last and you had talked before. Open questions come first.
- **Owe a reply (cold inbound):** people who wrote and never got an answer.
- **New connections you never talked to:** connected in the window, no message either way.

## Your network as a CRM

```bash
python3 skills/linkedin-network-brain/scripts/crm_export.py ~/Downloads/linkedin-archives/ --out linkedin-crm.csv
```

One row per connection: name, LinkedIn URL, email (when shared), company, position, seniority, connected on, number of messages, last message date, who wrote last, and a status:

| status | meaning |
| --- | --- |
| you owe a reply | they wrote last, and it was more than a "thanks" |
| waiting on them | you wrote last |
| closed | they wrote last with a "thanks" or an emoji |
| never talked | no message either way |

On our founder's 9,895 connections: 1,036 "you owe a reply", 2,231 "waiting on them", 409 "closed", 6,219 "never talked". Only 364 shared an email.

Import it into HubSpot, Attio, Pipedrive, Notion or Google Sheets. Use `linkedin_url` as the unique key, so every new export updates people instead of duplicating them. Then ask Claude to enrich it: function, fit with your ideal customer, company domains. The skill explains when looking up emails is fine and when it is not.

## Install

**Claude Code**

```text
/plugin marketplace add 2pr-io/safe-linkedin-automation
/plugin install safe-linkedin-automation@2pr-io
```

**Claude desktop or claude.ai**

Download `linkedin-network-brain.zip` from the [latest release](https://github.com/2pr-io/safe-linkedin-automation/releases/latest) and upload it under Settings > Capabilities > Skills.

Then ask Claude: *"Set up my LinkedIn data export"*, and once you have an archive, *"Who do I owe a reply on LinkedIn?"* or *"Turn my LinkedIn connections into a CRM"*.

You need [Claude in Chrome](https://claude.com/chrome) signed in to your LinkedIn for the export, and Python 3 for the report. The script uses only the standard library.

## Run the scripts by hand

```bash
python3 skills/linkedin-network-brain/scripts/network_report.py ~/Downloads/linkedin-archives/
python3 skills/linkedin-network-brain/scripts/crm_export.py ~/Downloads/linkedin-archives/ --out linkedin-crm.csv
```

Report options: `--days 30`, `--limit 25`, `--out report.md`. It accepts an archive zip, an unzipped archive folder, or a folder of zips (it picks the newest).

Request the **full** ("larger") archive: the report and the CRM statuses need your message history.

## Why this is safe

- Downloading your own data is your legal right (GDPR) and a built-in LinkedIn feature.
- The export clicks the same two buttons you would, every couple of days, in your own browser.
- No password, cookie or session token leaves your machine. No message, invite, like or comment is ever sent.

## More safe LinkedIn automation

A reply fixes one conversation. Posting regularly keeps your whole network warm. [2pr.io](https://2pr.io) writes LinkedIn posts in your own voice and publishes them through LinkedIn's official API, so there is no automation risk there either. [Start a free trial](https://2pr.io/app/login).

## License

MIT
