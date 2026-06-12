# Environment Dependencies Report

This document outlines the installed dependencies and development tools in this Arch Linux environment.

## 1. System-Level Packages (Pacman)

These packages are explicitly installed via the `pacman` package manager.

| Package | Version | Description |
|---------|---------|-------------|
| `base` | 3-3 | Minimal package set to define a basic Arch Linux installation |
| `base-devel` | 1-2 | Basic tools for building Arch Linux packages |
| `emacs` | 30.2-3 | The extensible, customizable, self-documenting real-time display editor |
| `gemini-cli` | 1:0.45.2-1 | Gemini CLI application |
| `ghostty` | 1.3.1-2 | Fast, feature-rich terminal emulator |
| `git` | 2.54.0-1 | Distributed version control system |
| `nano` | 9.0-1 | Small, free and friendly text editor |
| `neovim` | 0.12.3-1 | Fork of Vim focused on extensibility and usability |
| `openssh` | 10.3p1-1 | SSH protocol implementation for remote login, command execution and file transfer |
| `starship` | 1.25.1-1 | The minimal, blazing-fast, and infinitely customizable prompt for any shell |
| `sudo` | 1.9.17.p2-2 | Give certain users the ability to run some commands as root |
| `tree` | 2.3.2-1 | A directory listing program displaying a depth indented list of files |
| `vim` | 9.2.0600-1 | Vi Improved, a powerful text editor |
| `wget` | 1.25.0-5 | Network utility to retrieve content from web servers |
| `zellij` | 0.44.3-1 | A terminal workspace with batteries included |
| `zsh` | 5.9.1-1 | A very advanced and customizable shell |

*Note: `curl` (v8.20.0-7) is also installed as a core dependency for several of the above packages.*

## 2. Development Tools

| Tool | Version | Installation Method |
|------|---------|---------------------|
| `nvm` (Node Version Manager) | 0.40.5 | Manual script installation via `curl` |
| `starship` | 1.25.1 | Pacman |
| `zellij` | 0.44.3 | Pacman |
| `npm` | 11.13.0 | Installed via NVM |

## 3. Node.js Versions (NVM)

Managed via `nvm`.

- **v24.16.0** (Currently active and set as `default`)
- **system** (v26.2.0)

## 4. Global NPM Packages

Installed globally for Node.js v24.16.0:

| Package | Version |
|---------|---------|
| `@google/gemini-cli` | 0.46.0 |
| `corepack` | 0.35.0 |
| `npm` | 11.13.0 |

---
*Report generated on 2026-06-12.*
