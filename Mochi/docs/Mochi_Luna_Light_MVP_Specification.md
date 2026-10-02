# Mochi: Luna Light AI Desktop Pet

**Status:** Accepted brainstorming and MVP baseline  
**Stage:** Planning and pseudocode; implementation has not started  
**Target:** Windows 11 desktop companion for F7Hub and AltF7Hub

**Authority:** Accepted planning baseline; no implementation authorization. Follow [Mochi AGENTS.md](../AGENTS.md), [F7Hub architecture](../../Docs/06_SystemArchitecture.md) and [AltF7Hub instructions](../../AutoHotkey/Troubleshooting_Sections/AGENTS.md). [Architecture](Architecture.md) records proposed responsibilities; [Roadmap](Roadmap.md) breaks down future work. Renderer, provider and any new IPC contract remain unresolved.

## 1. Product Goal

Mochi is a planned desktop companion within the F7Hub repository whose first useful capability is guiding the user through known F7Hub and AltF7Hub screens. Its proposed separate pet window does not create a second application data store or replace F7Hub's primary GUI. Mochi would recognize a supported app view locally, show a concise hint when asked, and optionally use Luna to answer a user-initiated question with minimal, reviewed context.

The guiding rule is: **Mochi helps with the screen the user chose to ask about, using only the context needed to answer.**

## 2. Character and Experience

- Character: plush grey tabby cat with a teal collar.
- Existing concept assets: 73 validated animation frames across 11 states, including running, waving, jumping, waiting, reviewing, directional gaze, colorful smoke, and glitching. Confirm asset inventory before implementation.
- Mochi is movable, easy to hide, and dismissible. His message bubble is short and positioned near the pet without obscuring the app.
- Animations may reflect states such as idle, thinking, showing a hint, waiting for a question, and not recognizing a screen.
- Keyboard shortcuts are configurable and must not conflict with F7Hub or AltF7Hub shortcuts. Escape may dismiss the current hint.

## 3. MVP Capabilities

1. Display Mochi and support basic movement, hide, and exit behavior.
2. Detect whether F7Hub or AltF7Hub is the active process.
3. Recognize a small set of explicitly mapped screens using local window metadata and stable control or accessibility identifiers where available.
4. Show a local hint for a recognized screen: purpose, useful shortcut, or next step in a guided walkthrough.
5. Let the user invoke an "Ask Mochi" action for the current supported screen.
6. Keep local guidance available offline. Luna is optional and can be unavailable without disabling the local guide.
7. Provide guidance only. Mochi does not click, type, or navigate the app in the MVP.

## 4. UI Recognition Approach

- Use AHK Window Spy during development to inspect window titles, process names, classes, controls, and coordinates.
- Window Spy is a development diagnostic tool, not Mochi's runtime dependency or a complete UI navigation engine.
- At runtime, AHK should inspect only the active process/window when it belongs to the configured F7Hub or AltF7Hub allowlist.
- Prefer stable window/control identifiers or Windows accessibility information. Titles and coordinates may change and should be fallback signals only.
- A development process name alone is insufficient: F7Hub runs through Python and AltF7Hub through the shared AHK host. Verify actual checkout/window identities. Window titles may contain customer information; recognition metadata is not automatically approved outbound context.
- If a screen cannot be identified confidently, Mochi says he does not recognize it and offers a manual help action rather than guessing.
- Do not use screenshots or OCR in the MVP.

## 5. Guide Data and F7Hub Context

- Store Mochi's small, versioned screen guide in Mochi's project, for example as `guide.json`.
- A future read-only generator may analyze an explicit allowlist of F7Hub source files and documentation to produce or refresh the guide.
- Generator inputs may include GUI definitions, user-facing labels, shortcut definitions, and approved documentation.
- Exclude databases, live tickets, customer records, clipboard contents, credentials, secrets, and unrelated files.
- The generator reads F7Hub sources and writes generated output only to Mochi's project. It does not modify F7Hub.
- Record source version or commit and generation metadata so the guide can be reviewed when F7Hub changes.
- If selected source/docs are dirty, also record their content identities; a commit alone does not describe the analyzed bytes. Generated output requires review before use.
- Codex may analyze selected repository files during development. This build-time code analysis is separate from Mochi's runtime behavior.

Suggested guide entry fields:

```json
{
  "app_id": "f7hub",
  "process_name": "F7Hub.exe",
  "screen_id": "tickets.new",
  "match_rules": ["stable window/control identifiers"],
  "title": "New Ticket",
  "summary": "Create a ticket and optionally link its references.",
  "shortcuts": [],
  "walkthrough": [],
  "source_version": "reviewed source revision"
}
```

The example is illustrative. Confirm actual executable names, screen identifiers, controls, and F7Hub workflows from the source before implementing a guide.

## 6. Luna Interaction and Privacy

- Keep Luna behind a replaceable provider adapter until the actual API, authentication method, terms, and data handling are confirmed.
- Never send context automatically. A user must invoke Ask Mochi.
- Before an API request, show the exact context that will be sent and require an explicit Send action.
- Default payload: app identifier, known screen identifier, relevant approved guide text, and the user's question.
- Do not include screenshots, ticket Notes, customer data, clipboard contents, or raw screen text by default.
- Keep credentials out of source code and version control; use an appropriate local secret store if API access is implemented.
- If the API is unavailable, explain that briefly and continue to offer local guide content.

Future selected-text or ticket-note assistance requires a separate design: user-triggered capture, local filtering, a preview, explicit send, and confirmation that the data is permitted for the selected service.

## 7. Conceptual Components

- **Pet shell:** animation, movement, message bubble, hide/exit controls.
- **AHK observer:** supported-app detection and local active-window metadata collection.
- **Guide resolver:** matches observed identifiers to the local guide and returns hints or walkthrough steps.
- **Guide generator:** optional read-only development tool that creates reviewed guide data from approved F7Hub sources.
- **Luna adapter:** optional user-triggered API request with a preview of the minimal payload.

The rendering framework remains undecided. The pet can use a separate renderer while AHK handles Windows app detection and communication through a small, documented local interface.

## 8. MVP Exclusions

- Screenshot capture, background OCR, or screen recording.
- Background clipboard monitoring.
- Automatic ticket, Notes, or customer-data collection.
- Unprompted API requests or passive content analysis.
- Automated clicking, typing, or executing troubleshooting actions.
- Recognition of arbitrary apps outside the configured allowlist.

## 9. Build Sequence

1. Inventory the existing Mochi animation assets and choose a rendering framework.
2. Build the pet shell with movement, hide, exit, and a basic message bubble.
3. Add AHK detection for F7Hub and AltF7Hub, confirming it reads metadata only.
4. Hand-author a small guide for a few verified screens and test unknown-screen behavior.
5. Add the read-only guide generator after the manual guide format proves useful.
6. Confirm Luna API details, then add an explicit question, payload preview, and send flow.
7. Test app switching, offline behavior, unknown screens, privacy boundaries, and shortcut conflicts.

## 10. MVP Acceptance Checks

- Mochi recognizes only the supported F7Hub and AltF7Hub processes.
- Recognized screens show accurate, locally stored guidance; unknown screens do not trigger guessed instructions.
- The MVP does not capture screenshots, inspect clipboard changes, or read ticket content.
- Luna receives no request until the user asks and approves the displayed payload.
- Local hints continue to work without an internet connection.
- Mochi does not interfere with normal F7Hub or AltF7Hub input and can be hidden or exited promptly.
- The guide generator, if built, reads only its allowlisted sources and writes only inside Mochi's project.

## 11. Decisions for Later

- Pet rendering framework and packaging approach.
- Exact F7Hub and AltF7Hub process names, screen identifiers, and supported controls.
- A non-conflicting default hotkey and user settings for shortcuts.
- Luna API endpoint, authentication, provider terms, and data-retention behavior.
- Whether company policy permits sending even limited application context to the chosen AI service.
- Whether selected text or ticket-note assistance belongs in a later version.
