# Oryn Basis-Tickets Collection

Diese Sammlung enthält die ersten 15 Basis-Tickets für den Oryn "Silent Alpha" Launch.

## Ticket-Struktur

Jedes Ticket folgt dem YAML-Format mit folgenden Feldern:

```yaml
title: "Kurzer, prägnanter Titel"
category: "security|ui|docs|translation|testing|infrastructure"
difficulty: 1-5  # 1=Einsteiger, 5=Expert
credit_reward: 10-100  # Credits basierend auf Aufwand
reputation_weight: 1-10  # Reputation-Impact
estimated_hours: 1-40  # Geschätzte Arbeitszeit
skill_tags: ["javascript", "react", "security"]
requires_one_human: true|false  # One-Human Attestation erforderlich

dod: |  # Definition of Done
  - Klare, überprüfbare Kriterien
  - Was genau geliefert werden muss
  - Qualitätsstandards

description: |
  Detaillierte Beschreibung der Aufgabe
  Hintergrund und Kontext
  
acceptance_criteria:
  - Kriterium 1
  - Kriterium 2
  
evidence_requirements:
  code_review: true
  tests_passing: true
  documentation: true
  security_audit: false
  accessibility_check: false
  
bonus_criteria:  # Optional für Extra-Credits
  - "Performance-Optimierung"
  - "Zusätzliche Tests"
```

## Kategorien-Übersicht

### 🛡️ Security (5 Tickets)
- E2E-Verschlüsselung für Chat
- Secure Wallet-Integration
- XSS-Schutz für PWA
- Rate-Limiting für API
- Security-Audit-Tools

### 🎨 UI/UX (3 Tickets)  
- Barrierefreies Ticket-Board
- Mobile-First-Design
- Dark-Mode-Support

### 📚 Documentation (3 Tickets)
- Contributor-Guide
- API-Dokumentation
- User-Onboarding-Guide

### 🌐 Translation (2 Tickets)
- I18n-Framework-Setup
- Deutsche Übersetzung

### 🧪 Testing (2 Tickets)
- End-to-End-Tests
- Performance-Tests

## Schwierigkeitsgrade

- **Level 1 (Einsteiger)**: 10-20 Credits, 2-4 Stunden
- **Level 2 (Fortgeschritten)**: 25-35 Credits, 4-8 Stunden  
- **Level 3 (Erfahren)**: 40-60 Credits, 8-16 Stunden
- **Level 4 (Expert)**: 65-85 Credits, 16-24 Stunden
- **Level 5 (Architekt)**: 90-150 Credits, 24-40 Stunden

## Ticket-Status

| ID | Titel | Kategorie | Schwierigkeit | Status |
|----|-------|-----------|---------------|---------|
| 001 | E2E Chat-Verschlüsselung | Security | 4 | ✅ Erstellt |
| 002 | Barrierefreies Ticket-Board | UI | 3 | ✅ Erstellt |
| 003 | Contributor-Guide | Docs | 2 | ✅ Erstellt |
| 004 | I18n-Framework-Setup | Translation | 3 | ✅ Erstellt |
| 005 | PWA-Security-Hardening | Security | 4 | ✅ Erstellt |
| 006-015 | ... | ... | ... | 📝 In Arbeit |