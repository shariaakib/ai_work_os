# AI WORK OS — VISION DOCUMENT

## The Big Idea

We are building an AI-native Work OS — not another chatbot, not just a collection of AI tools, and not simply a prettier ChatGPT interface.

The vision is:

Instead of humans learning how to operate dozens of software applications, humans describe what they want to accomplish, and AI figures out how to get it done.

Think of it as a Jarvis-like intelligent workplace, but designed for real professional work.

---

## What the user experiences

Today:

You
 ↓
Open Gmail
 ↓
Search emails
 ↓
Open Calendar
 ↓
Open Drive
 ↓
Open Excel
 ↓
Research
 ↓
Write report
 ↓
Send email
 ↓
Update task manager

Our vision:

You:
"Prepare everything I need for tomorrow's meeting with ABC and tell me anything I should know."

                    ↓
                 AI WORK OS
                    ↓
              Understands goal
                    ↓
               Makes a plan
                    ↓
        ┌───────────┼───────────┐
        ↓           ↓           ↓
      Email      Calendar      Drive
        ↓           ↓           ↓
## What we're actually building

The AI model itself isn't the product.

The model is the brain.

Our product is the entire system around it:

                  AI WORK OS
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
     AI BRAIN      WORK GRAPH      MEMORY
        │              │              │
        └──────────────┼──────────────┘
                       ↓
                 AI MANAGER
                       ↓
               SPECIALIST AGENTS
                       ↓
                    TOOLS
                       ↓
          ┌────────────┼────────────┐
          ↓            ↓            ↓
         APIs        Browser      Computer
          ↓            ↓            ↓
          └────────────┼────────────┘
                       ↓
                  VERIFICATION
                       ↓
                   PERMISSIONS
                       ↓
                    RESULT

---

## The AI Manager

Instead of giving the user 20 different agents and expecting them to understand everything, we want a Manager Agent.

The user says:

"I need a business proposal for this client."

The Manager decides:

Manager
   │
   ├── Research Agent
   │
   ├── Analyst Agent
   │
   ├── Finance Agent
   │
   ├── Writer Agent
   │
   └── Verification Agent

The user doesn't need to manually coordinate them.

The AI coordinates the AI.

---

## Specialist AI Workers

Our platform can have different agents for different jobs.

For example:

🔎 Research Agent

Researches information and produces evidence-backed findings.
## Persistent Work Memory

The AI should gradually understand the user's workplace.

For example:

"I prefer short client emails."

"Project Phoenix is high priority."

"Never send external emails without my approval."

"John prefers meetings in the afternoon."

The user controls what the AI remembers.

The principle is:

Memory should belong to the user, not secretly belong to the AI.

---

## Trust is part of the product

A Jarvis that can do everything but cannot be trusted is useless.

So our system will have permission levels.

🟢 Safe — AI can generally do automatically:

* Read
* Search
* Analyse
* Summarise
* Draft

🟡 Approval required — AI asks:

"I've prepared the email. Do you want me to send it?"

"I've prepared the calendar changes. Approve?"

🔴 High risk — Always require explicit confirmation and potentially additional safeguards:

* Financial transactions
* Irreversible deletion
* Security changes
* Legal/regulated actions

Our philosophy:

AI should be powerful enough to be useful and controlled enough to be trusted.

---

## Application-independent AI

We don't want to become another closed ecosystem.

The AI should be able to work with existing software.

For example:
## Continuous Agent Ecosystem

This is another part of your original idea that I think is worth keeping.

The workplace shouldn't feel finished.

New agents can continuously be released.

For example:

AI Work OS
      │
      ▼
  Agent Store
      │
 ┌────┼────┬────┬────┐
 ↓    ↓    ↓    ↓    ↓
Sales HR Finance Dev Research

A user could install:

Real Estate Agent
or:
Restaurant Operations Agent
or:
Marketing Agent
or:
Software Testing Agent

Eventually, developers could build agents for the platform.

---

## Long-Term Business Vision

One possible model:

Free / accessible core

Users can experience the AI Work OS without a huge barrier.

Premium agents

Specialised professional agents could be paid.

Business plans

Companies pay for:

* Advanced security
## The ultimate vision: Jarvis for Work

Eventually, imagine sitting at your computer and saying:

"I have three hours today. Look at my priorities and tell me what I should focus on."

The AI knows:

* Your projects
* Deadlines
* Meetings
* Tasks
* Emails
* Documents
* Priorities
* Previous decisions

It says:

"You have a client presentation tomorrow, your proposal is 70% complete, and the financial section is missing. I recommend finishing that first."

You say:

"Handle it."

The AI:

Research
   ↓
Analyse
   ↓
Create draft
   ↓
Check numbers
   ↓
Update document
   ↓
Show you changes
   ↓
Ask approval
   ↓
Complete

That's the experience we're aiming toward.

---

## The Bigger Vision

We aren't trying to build:

"Another AI chatbot."

We're trying to build:

"The operating layer between humans and digital work."

Today, software is organised around applications.

Tomorrow, we want work to be organised around goals.

Today's paradigm

Person
 ↓
Application
 ↓
Feature
 ↓
Action

Our vision

Person
 ↓
Goal
 ↓
AI
 ↓
Agents
 ↓
Tools
 ↓
Applications
 ↓
Outcome

---

## Our North Star

If we eventually succeed, someone should be able to sit down at their computer and think:

"I don't care which application does this. I just want the work done."

And the AI Work OS should be able to understand the goal, figure out the workflow, use the right tools and agents, keep the human in control, and deliver a verified result.

Our North Star:

From apps to outcomes.
From software users to AI-assisted workers.
From individual AI chats to an intelligent workplace.
* Team management
* More integrations
* Higher usage
* Enterprise controls

Agent marketplace

Third-party developers could sell agents.

The platform could take a percentage.

This gives us a potential ecosystem rather than relying only on charging for chat messages.

But we will not lock ourselves into this business model yet. Product-market validation comes first.

              AI WORK OS
                   │
      ┌────────────┼────────────┐
      ↓            ↓            ↓
    Gmail       Calendar      Drive
      ↓            ↓            ↓
   GitHub        CRM          Slack

The existing applications become tools available to the AI.

---

## Model independence

Another important principle:

Our product should not depend on one AI model.

Today it might use:

* Claude
* GPT
* Gemini
* DeepSeek

Tomorrow there could be another better model.

Our architecture should allow us to change the underlying model without rebuilding the entire product.

That's why an AI gateway such as OpenRouter can be useful during development.

📊 Analyst Agent

Analyses datasets, trends and business information.

✍️ Writer Agent

Creates reports, proposals, emails and documents.

💻 Developer Agent

Works with code, repositories and development tools.

📅 Executive Assistant

Manages meetings, schedules and preparation.

🌐 Web Agent

Researches and interacts with websites.

📁 Document Agent

Understands and manages workplace documents.

Eventually:

Finance Agent, Marketing Agent, HR Agent, Sales Agent, Legal-support Agent, Operations Agent, and many more.

---

## The Work Graph

This is one of the ideas I think could make our product significantly more interesting.

Instead of AI only remembering conversations, it understands the relationships between work.

For example:

Sarah
 ↓ manages
Project Phoenix
 ↓ belongs to
ABC Company
 ↓ has
Meeting
 ↓ related to
Proposal
 ↓ requires
Financial Analysis
 ↓ deadline
Friday

Then you could ask:

"What is currently blocking Project Phoenix?"

The AI doesn't just search text.

It understands the structure of the work.
      CRM        Research      Tasks
        └───────────┼───────────┘
                    ↓
              AI synthesises
                    ↓
               Verification
                    ↓
          ┌─────────┴─────────┐
          ↓                   ↓
      Information          Actions
       → safe              → approval
                    ↓
                 RESULT

The user doesn't need to think:

"Which application do I open?"

They think:

"What outcome do I want?"