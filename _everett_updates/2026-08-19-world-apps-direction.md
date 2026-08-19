---
layout: everett-post
title: "World Apps: gathering the rest of a project without pretending it moved inside"
slug: world-apps-direction
date: 2026-08-19 08:00:00 -0400
summary: "World Apps is design and MVP direction for remembering files, folders, URLs, applications, and external companions without claiming to contain them."
description: "The design direction for World Apps and the macOS boundaries that keep it honest."
status: design-direction
status_label: "Design and MVP direction, not shipping"
tags:
  - world-apps
  - macos
hero_image: /assets/images/everett/full/world-apps-direction.png
hero_thumbnail: /assets/images/everett/thumb/world-apps-direction.png
hero_width: 1440
hero_height: 900
hero_alt: "World Apps design direction showing references, app launchers, and external running companions."
hero_caption: "World Apps is design and MVP direction, not shipping behavior."
hero_kind: design-direction
og_image: /assets/images/social/everett-og.png
source_basis:
  - "Grounded in the World Apps draft product requirements, macOS feasibility research, and Everett's current brand and boundary language."
  - "No behavior described here should be read as shipping unless it also appears in the current-truth section of the Everett homepage."
public_links: []
---

World Apps is design and MVP direction, not shipping behavior. It explores how a World could remember the external material a project depends on without pretending those files, applications, and windows moved inside Everett.

That distinction is the feature.

A real project is wider than its repository. It may depend on a specification PDF, a design export folder, a set of reference URLs, an installed API client, an editor, and a particular external window. Those things are part of the working reality even though Everett does not own them.

> **Design direction, not shipping:** the proposed World Apps surface coordinates references and launch choices. It does not copy, embed, sandbox, reparent, or own arbitrary macOS applications.

## Three proposed card types

The direction uses three precise kinds rather than one vague "app inside the World" metaphor.

A **Reference** represents a file, folder, or URL. The World stores the label, locator, status, and launch preference. The underlying item stays on the host.

An **App launcher** represents an installed application. The World remembers how to open or activate it. The application's process, profile, accounts, extensions, recent items, and open documents remain normal shared Mac state.

A **Running companion** represents an external application or, where the platform permits, a best-effort match to one of its windows. It stays outside Everett. The card can request focus, but the operating system remains in control.

These types make the boundary visible on every card. "World scoped" refers to the card and preference, not to the external process.

{% include everett-figure.html
  src="/assets/images/everett/full/board.png"
  alt="Historical Everett Board mockup showing heterogeneous project context in one visual surface."
  width="1440"
  height="900"
  label="Design direction"
  caption="The broader Board concept motivates World Apps, but arbitrary external applications would remain outside Everett."
%}

## Dropping is data intake, never consent to execute

The proposed drop behavior is deliberately quiet.

A user can drop a file, folder, URL, or application bundle onto the World. Everett identifies the item, checks whether it is already present, creates the appropriate card, and offers an undo path.

Nothing opens because of the drop.

That rule applies to documents, URLs, folders, and applications. A drop says, "remember this with the project." It does not say, "run this now."

The draft also makes `Open with World` a per-item option that starts off. The default is no automatic opening on add, restart, migration, or Shift.

This reduces accidental execution and keeps the World fast to restore. It also makes each automatic action attributable to a choice the user made on that card.

Unsafe executable content needs a stronger boundary. Scripts, command files, and binaries should remain references with safe reveal or editor actions. A drop must never become an indirect shell command.

## External means external

Everett cannot honestly claim that adding an application card isolates the application.

An external application may use one shared process for several windows. It may keep one account, one extension set, one recent-document list, and one profile across every Everett World and across use outside Everett. Its documents may point to host paths that several Worlds can reach.

The MVP direction therefore avoids ownership language. Removing a card removes the World reference only. It does not delete a host file, uninstall an application, close a document, or quit a process.

Shifting away from a World also leaves external windows alone. Hiding, moving, closing, or reparenting them would be surprising and would imply a stronger contract than Everett has.

The anti-goals are explicit:

- No arbitrary window embedding or reparenting.
- No durable claim that Everett owns a third-party process or window.
- No private macOS window-server APIs.
- No Spaces creation or management.
- No screen-recording trick used to fake an embedded application.

The honest version is still useful. A World can remember what the project needs and get the user back to it without turning an external tool into a fictional Everett surface.

## Accessibility is optional and narrow

Most of the proposed MVP does not require Accessibility permission. Everett can remember references, list application-level choices through normal platform APIs, and request that an application open or activate without asking to inspect every other window.

Accessibility becomes relevant only for specific-window discovery or best-effort focus.

Even with permission, macOS does not offer a durable public identity for every third-party window. Titles change. Window order changes. Some applications expose incomplete accessibility trees. A saved match can become ambiguous.

The proposed language reflects that. Without permission, Everett can focus the application at best. With permission, it may offer specific-window discovery and a best-effort focus attempt. It must not promise that a particular window can always be found tomorrow.

The rest of World Apps should remain usable when the permission is denied or later revoked.

## The automatic-opening tension remains unresolved

There is a genuine product tension in the draft.

One direction says `Open with World` should be an explicit per-item opt-in. That is convenient for a user who always wants an editor and a reference document when shifting into a project.

The stricter direction says external things should open only after an explicit click every time. That is easier to reason about, reduces surprise, and avoids a World activation causing a cascade of application focus changes.

The current draft preserves the tension rather than resolving it by implication.

If per-item automatic opening survives, it should remain off by default, execute only after the Everett World is interactive, suppress duplicate launches, report failures on the card, and never block the Shift. Unsafe or unresolved items should not be eligible.

If explicit click every time wins, the model becomes simpler and more conservative at the cost of convenience.

Both are plausible. Shipping copy should not pick one until the product decision and implementation agree.

## Gathering without containment theater

World Apps matters because project context includes things Everett does not own.

The wrong response would be to ignore them. The other wrong response would be to draw cards that imply containment the operating system does not provide.

The design direction takes a middle path: remember the reference, keep the preference with the World, label the external boundary, and make opening or focusing an explicit, observable action.

That preserves Everett's central promise of relevance while keeping the system honest about macOS. A project can gather the rest of its working reality without pretending that reality moved inside.
