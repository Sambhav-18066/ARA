ARA

Version: 0.2.0Codename: Genesis

ARA is a modular desktop AI assistant focused on local Windowsautomation, filesystem operations, browser search, system utilities,calculator functions, vision/OCR, visual actions, safety checks, andAI-planner fallback.

Status: Active development. This README documents commands andcapabilities implemented or observed in the current Genesis build.Some Windows and vision commands still need broader end-to-endregression testing.

Run ARA

python -m app.ara

Exit with:

exit
quit

Architecture

User
  ↓
Local Router
  ├─ deterministic match → Intent
  └─ no match → AI Planner
                    ↓
              Decision Engine
                    ↓
                 Executor
                    ↓
                  Skill

Current skill areas include Windows, Browser, System, Calculator,Vision, and Visual Action.

Commands

Open applications

open Brave
open OBS
open Notepad
open Calculator
open Paint
open Chrome

ARA supports built-in mappings and dynamic Windows Start Menuapplication resolution.

Open folders, drives, files, and paths

open Desktop
open Downloads
open Documents
open Pictures
open images
open Videos
open Program Files
open E:
open C:
open yajnya.png
open report.pdf
open C:\Program Files\Google

ARA supports known Windows folders, aliases such as images → Pictures,drive roots, searched files/folders, and explicit paths.

Ambiguous resource selection

When multiple equally strong matches exist, ARA can ask which one youmean:

You > open ara_duplicate_test.txt

ARA > I found multiple matches for 'ara_duplicate_test.txt':
1. C:\Users\...\Desktop\ara_duplicate_test.txt
2. C:\Users\...\Downloads\ara_duplicate_test.txt
Which one? Enter a number or type cancel.

You > 1

Use cancel to abandon a pending selection.

Copy

copy yajnya.png to Downloads
copy report.pdf to Desktop
copy C:\test.txt to E:\Backup
copy yajnya.png to E:

Move

move yajnya.png to Downloads
move report.pdf to Desktop
move C:\test.txt to E:\Backup

Rename

rename test.txt to final.txt
rename yajnya.png to yajnya-old.png

Delete

delete report.pdf
remove old-file.txt

Delete requires explicit confirmation.

You > delete report.pdf
ARA > Delete 'C:\...\report.pdf'? Type yes to confirm or no to cancel.
You > yes

Cancellation responses include no, cancel, stop, never mind, andnevermind.

For duplicate filenames, ARA selects the exact resource before askingfor destructive confirmation:

You > delete ara_duplicate_test.txt
ARA > I found multiple matches...
You > 1
ARA > Delete 'C:\Users\...\Desktop\ara_duplicate_test.txt'?
You > yes

ARA also contains protection intended to prevent deletion of its ownproject tree and important filesystem locations.

Browser and Internet

Web search

search the internet for Unreal Engine optimization
search the web for RTX 5090 reviews
search for a 3d model
look up Python decorators
google Unreal Engine 5 Nanite

Current browser search launches the query in the browser. Fullautonomous multi-page research and synthesis is not yet implemented.

Known websites

Current direct website mappings include:

YouTube
Google
GitHub

Windows Automation

The Windows skill includes keyboard, mouse, window-management,application, and filesystem operations.

Keyboard

Implemented action types include:

type ...
press ...
hotkey ...

Mouse

Implemented action types include:

click
right click
scroll

Window management

Infrastructure exists for operations including:

active window
list windows
focus ...
wait for window ...
minimize ...
maximize ...

active_window was recently identified as needing dispatchcleanup/retesting, so treat this command family as development-stageuntil regression testing is complete.

Multi-Step Commands

ARA can execute a sequence of local intents.

Known pattern:

open notepad and write Hello from ARA

Each step passes through the Decision Engine, and execution stops if astep fails.

System and Calculator

ARA registers dedicated system and calculator skills for localsystem-information operations and calculations.

The exact natural-language phrase coverage should be verified againstthe current Local Router before being considered a fixed public API.

Vision and Visual Actions

ARA currently boots with:

Local OCR
Visual Target Selector
vision skill
visual_action skill

These provide the foundation for screen understanding, OCR, visualtarget selection, and UI interaction. This area is still under activedevelopment.

Safety

ARA's Decision Engine sits between intents and execution.

High-risk action categories include actions such as:

delete
format
shutdown
restart

Delete uses explicit confirmation, exact-path resolution, ambiguityselection, and filesystem protection before destructive execution.

AI Planner Fallback

If the Local Router cannot deterministically understand a request, ARAcan send it to its AI planner:

Local Router
    ↓ no match
AI Planner
    ↓
Decision Engine
    ↓
Executor

The current planner uses Gemini. If that external service is unavailableor quota-limited, ARA reports that AI reasoning is unavailable whilelocal deterministic capabilities remain operational.

Quick Command Reference

open Brave
open OBS
open Notepad
open Calculator
open Paint
open Chrome

open Desktop
open Downloads
open Documents
open Pictures
open images
open Videos
open Program Files
open E:

open yajnya.png
open report.pdf
open C:\Program Files\Google

copy yajnya.png to Downloads
copy report.pdf to Desktop
copy C:\test.txt to E:\Backup

move yajnya.png to Downloads
move test.txt to Desktop

rename test.txt to final.txt
rename yajnya.png to yajnya-old.png

delete report.pdf
remove old-file.txt

search the internet for Unreal Engine optimization
search the web for RTX 5090 reviews
search for a 3d model
look up Python decorators
google Unreal Engine 5 Nanite

open notepad and write Hello from ARA

Planned Capabilities

These are part of the broader ARA vision, but are not current workingcommands:

Android Device Manager

Phone app control

Authenticated phone-unlock integration where the device platformpermits it

Phone camera capture

BGMI and Termux launching/device automation

Cross-device file transfer

Other PC agents

Smart TV and media-device control

Smart-home/IoT control

Webcam gesture recognition

Persistent contextual memory

World-news briefings

Live weather retrieval

Rich web research and synthesis

Music-library intelligence across devices

Invoice/bill generation

Voice-first multi-device orchestration

A future Device Manager can expose generic capabilities:

Device
├── power
├── applications
├── files
├── media
├── camera
├── notifications
└── system

Near-Term Development Priorities

Stabilize and regression-test Windows actions.

Complete ambiguity handling across copy, move, rename, anddestination resolution.

Improve natural-language routing and typo tolerance.

Harden destructive-operation safety and recovery.

Improve multi-step state handling.

Improve browser/research capabilities.

Expand and test vision/UI automation.

Add a centralized capability/command registry and built-in help.

Begin Device Manager architecture and Android integration after thelocal foundation is stable.

ARA v0.2.0 --- Genesis
