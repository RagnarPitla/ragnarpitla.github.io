---
layout: everett-post
title: "Why Everett exists: one World per project"
slug: one-world-per-project
date: 2026-08-19 12:00:00 -0400
summary: "A measured project-context failure led Everett to make the World, not the terminal workspace, its top-level object."
description: "The measured problem behind Everett and the model of one World per software project."
status: product-thesis
status_label: "Product thesis grounded in measured current evidence"
tags:
  - worlds
  - ai-agents
hero_image: /assets/images/everett/full/worlds-overview.png
hero_thumbnail: /assets/images/everett/thumb/worlds-overview.png
hero_width: 1440
hero_height: 900
hero_alt: "Everett Worlds overview showing separate project Worlds and their activity."
hero_caption: "Separate Worlds keep unrelated project realities legible while they continue running."
hero_kind: historical-design-mockup
og_image: /assets/images/social/everett-og.png
source_basis:
  - "Grounded in Everett's measured Herdr session notes, current brand decisions, and current World requirements."
  - "Current boundary statements reflect the implemented macOS application and its isolation audit, not the stronger future Mount design."
public_links: []
---

The clearest reason for Everett arrived as a measurement, not a mood. In one live Herdr session, seven agents were running across two directories. Five of the seven were working outside the World their names implied.

That mismatch was visible only after the session state was read as data. On screen, the work looked organized. Tabs had names such as a chess build, an iOS teleprompter, a Remotion pipeline, and a visual development tool. Underneath those names, most of the agents were sitting in the same repository.

The most revealing workspace was called `FUn--Adhoc`. It held six unrelated products because there was no stronger place to put them. It was not a project. It was a leftovers drawer with terminals in it.

This was not operator failure. It was a model failure.

## The object a tool offers becomes the behavior it encourages

A window manager groups windows. It can keep related applications beside one another, but it does not know whether a browser, editor, and terminal belong to the same codebase.

A terminal runtime groups terminals, panes, tabs, and agent processes. It can preserve sessions and report useful process state, but a terminal tab is still a terminal tab. Its working directory is usually inherited once at launch, then trusted.

Neither object represents the whole project reality.

When the top-level object is a terminal workspace, unrelated work can accumulate there without violating any rule. A tab can be called `chess-build` while its shell is running in a completely different repository. The label and the execution context drift apart because nothing owns both.

Everett makes a different choice. The top-level object is a **World**.

## A World is the project reality

A World is the durable place where one software project gathers its workspace folders, terminals, agents, Web links, launch preferences, local environment, history, and persistent Board.

The word matters because it changes the frame. A World is not a prettier folder picker and not a renamed terminal workspace. It is the object that says: this work belongs together, this is the context that should be visible now, and this is where new work begins.

A **Shift** is the act of moving from one World to another. The whole Everett window changes with it. The Board, terminal set, Web collection, and current context are restored for the destination World rather than left behind as unrelated tabs.

The benefit is relevance and focus. Isolation is one mechanism that can support that benefit, but it is not the whole product story and it is not yet absolute.

{% include everett-figure.html
  src="/assets/images/everett/full/board.png"
  alt="Everett Board mockup arranging agent terminals, a plan sketch, notes, and a Web card."
  width="1440"
  height="900"
  label="Historical design mockup"
  caption="The Board explores how one World can keep different kinds of working context visible together."
%}

## The practical change is small and consequential

In the ad-hoc session, the shell happened to start in a repository and the tab inherited it. Everett reverses that relationship. The World supplies the workspace context when a terminal or agent starts.

That does not solve every form of drift by itself. A process can still change directories after launch unless a runtime boundary prevents it. But it creates a stable owner against which drift can be detected, explained, and eventually blocked.

It also changes how the user reads the system. Instead of asking, "Which terminal did I put that in?" the user can ask, "Which World owns this work?" The answer connects the project name, workspace, agents, Web context, and Board.

This is why Everett is not trying to become a terminal multiplexer. The design direction is to integrate Herdr for the terminal runtime rather than rebuild its panes, persistence, agent detection, and worktree handling. That integration does not ship in the installed application today. The current app runs real PTYs itself.

The distinction is important: the World model is current product thinking and partially implemented behavior; the Herdr-backed runtime is direction.

## The honest boundary today

Some separation is real now.

Everett gives each World its own workspace folder and separates several terminal-side state paths, including shell history, caches, temporary files, git configuration, and a port range. Everett Preview also uses a browser storage partition per World.

Other boundaries remain shared.

The host filesystem is still reachable. Host dotfiles and credentials may be reachable. Coding-agent command-line tools can keep their own login and session state under the user's home directory. External browsers opened with a system profile share cookies, logins, bookmarks, and history across Worlds.

That makes the current World **a boundary for relevance, not for secrets**.

It is safe to say that Everett organizes and restores project context. It is not safe to say that one World is a security sandbox against another. Full Mount enforcement is design direction, not shipping behavior.

The process boundary also has a narrow edge. Everett strongly reaps the process trees it starts, including ordinary background jobs, but a fully detached process with no remaining socket can escape discovery. The product should state that limit rather than hide it behind the general idea of cleanup.

## Why measured evidence belongs in the product story

The original seven-agent session does more than provide a dramatic opening. It gives Everett a falsifiable problem.

If Worlds work, the user should be able to tell which project owns an agent. New terminals should begin in the right workspace. Web links and Board objects should restore with the right project. A Shift should replace the visible project reality rather than add more tabs to a shared pile.

The same evidence also prevents the design from becoming abstract. "Better focus" is easy to claim. "Five of seven agents were outside the project their names implied" is a condition that can be measured again.

Everett exists to make that failure harder to create, easier to see, and eventually impossible within the boundaries it can honestly enforce.

The World is the product spine because it connects the name on the screen to the work that is actually happening. Everything else, from Web to Board to future Mount enforcement, is valuable insofar as it keeps that connection intact.
